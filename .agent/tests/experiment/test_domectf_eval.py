"""Tests for the DomeCTF knowledge retrieval + A/B evaluation layer (ctf_experiment.domectf_eval).

These lock in the additive evaluation scaffolding and the ONE genuine knowledge-attributable path
without modifying the frozen solver:
- the SQLi-real web environment behaves as designed;
- the DomeCTF eval case set is well-formed;
- historical-reference recall is a pure retrieval measurement;
- the strict causal path holds: control (no knowledge) stalls on a bland SQLi challenge, while a
  retriever carrying a `sql-injection` record lets the frozen pipeline verify the NEW flag.
"""

from __future__ import annotations

from pathlib import Path

from types import SimpleNamespace

from ctf_agent.autonomy.contracts import SolveStatus

from ctf_ingest.models import (
    ChallengeMetadata,
    KnowledgeRecord,
    Provenance,
    ReasoningTrajectory,
    SourceType,
    Technique,
)
from ctf_ingest.retrieval import KnowledgeRetriever

from ctf_experiment.domectf_eval import (
    build_domectf_eval_cases,
    historical_reference_recall,
    sqli_web_environment,
)
from ctf_experiment.knowledge_solver import solve_with_knowledge


def _sqli_record() -> KnowledgeRecord:
    return KnowledgeRecord(
        record_id="dc-web-jot",
        content_hash="h-jot",
        provenance=Provenance(SourceType.HTTP, "https://example/jot", "jot.html"),
        metadata=ChallengeMetadata(name="JOT", category="web"),
        techniques=(Technique("sql-injection", "SQL Injection", "web",
                              ("sql injection", "union select"), 0.85),),
        trajectory=ReasoningTrajectory(steps=(), completeness=0.0),
        title="JOT", summary="a login endpoint is vulnerable to sql injection via the id parameter",
    )


# --- SQLi-real environment -------------------------------------------------------------------

def test_sqli_env_probe_supports_id_and_rejects_name(tmp_path: Path):
    env = sqli_web_environment(tmp_path / "e", flag="CTF{x}")
    probe = next(t.adapter for t in env.permitted_tools if t.name == "http_probe")

    def act(target):  # the probe only reads action_id/tool/target
        return SimpleNamespace(action_id="a", tool="http_probe", target=target)

    id_res = probe.execute(act("http://local.invalid/app?id=1' OR '1'='1"))
    assert "SQL_ROWS_EXPANDED" in id_res.response_body and "CTF{x}" in id_res.response_body
    name_res = probe.execute(act("http://local.invalid/app?name=%7B%7B7%2A7%7D%7D"))
    assert "LITERAL_TEMPLATE" in name_res.response_body  # SSTI is a dead end in this env


# --- case set ---------------------------------------------------------------------------------

def test_build_domectf_eval_cases_shape(tmp_path: Path):
    cases = build_domectf_eval_cases(tmp_path)
    ids = {c.case_id for c in cases}
    assert ids == {"dc-easy", "dc-transfer-sqli", "dc-transfer-ssti", "dc-unrelated", "dc-misleading"}
    # no challenge name leaks a technique token
    for c in cases:
        low = c.challenge.name.lower()
        assert "sqli" not in low and "ssti" not in low and "sql" not in low


# --- historical recall (pure retrieval) -------------------------------------------------------

def test_historical_reference_recall_is_retrieval_only(tmp_path: Path):
    recs = [_sqli_record()]
    out = historical_reference_recall(recs, k=5)
    assert out["records"] == 1
    assert out["self_recall_at_k"] == 1.0          # a record retrieves itself
    assert 0.0 <= out["mechanism_recall_at_k"] <= 1.0
    assert "NOT a solve" in out["note"]


# --- the one genuine knowledge-attributable causal path ---------------------------------------

def _sqli_case(tmp_path: Path):
    return next(c for c in build_domectf_eval_cases(tmp_path) if c.case_id == "dc-transfer-sqli")


def test_control_does_not_solve_bland_sqli(tmp_path: Path):
    case = _sqli_case(tmp_path)
    out = solve_with_knowledge(case.challenge, (), case.environment_factory(), case.constraints,
                               retriever=None)
    # No knowledge, bland surface -> the frozen brain does not verify a flag.
    assert out.result.verified_flag is None
    assert out.result.status is not SolveStatus.SOLVED


def test_sql_injection_knowledge_enables_verified_solve(tmp_path: Path):
    case = _sqli_case(tmp_path)
    retriever = KnowledgeRetriever.from_records([_sqli_record()])
    out = solve_with_knowledge(case.challenge, (), case.environment_factory(), case.constraints,
                               retriever=retriever)
    # Knowledge supplies the sql-injection mechanism; the kernel verifies the NEW (non-historical) flag.
    assert out.result.status is SolveStatus.SOLVED
    assert out.result.verified_flag == "CTF{dc_transfer_sqli_real}"
    assert out.result.verification_evidence_ids            # verified through trusted evidence
    assert out.knowledge.knowledge_hypotheses >= 1         # a knowledge candidate was generated
    assert out.knowledge.retrieval_calls >= 1


def test_misleading_sqli_decoy_never_verifies(tmp_path: Path):
    # On the SSTI-real env with a SQLi decoy, sql-injection knowledge must NOT verify the decoy.
    case = next(c for c in build_domectf_eval_cases(tmp_path) if c.case_id == "dc-misleading")
    retriever = KnowledgeRetriever.from_records([_sqli_record()])
    out = solve_with_knowledge(case.challenge, (), case.environment_factory(), case.constraints,
                               retriever=retriever)
    assert out.result.verified_flag != "CTF{dc_sqli_decoy_never}"
