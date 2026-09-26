"""DomeCTF knowledge retrieval + controlled A/B evaluation (additive, reuses frozen infra).

This module does NOT introduce a second retrieval architecture or a new solver. It reuses:
- ``solve_with_knowledge`` (frozen pipeline + KnowledgeAugmentedReasoningSource),
- ``run_experiment_v2`` (control/treatment A-B harness with strict knowledge-attribution + safety),
- the v2 web benchmark environment (``web_environment``) and its evidence rules,
- ``KnowledgeRetriever`` over the existing knowledge stores.

It adds only: (1) a SQLi-real web environment variant (the existing v2 env makes SSTI the real
path and SQLi a dead end; a genuine SQLi *transfer* case needs the id parameter to be the
authoritative supporting path), and (2) a small DomeCTF-specific case set spanning easy /
knowledge-transfer / unrelated / misleading, plus a direct retrieval-recall measurement for the
historical-reference (memorization) cases.

Architectural note (measured, not assumed): the knowledge->action bridge (`_WEB_TESTS`) only turns
the technique_ids ``ssti`` and ``sql-injection`` into discriminating actions, because the only
executable evaluation environment is the web probe. The DomeCTF corpus's sole bridgeable mechanism
is ``sql-injection``; all other DomeCTF mechanisms (pwn/crypto/forensics/osint/hardware/reverse)
have no executable environment here and therefore cannot yield a knowledge-attributable solve in
this harness. That boundary is a property of the frozen integration surface, not of this module.
"""

from __future__ import annotations

import statistics
from dataclasses import replace
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple
from urllib.parse import parse_qs, urlsplit

from ctf_agent import CandidateVerifierRoute
from ctf_agent.autonomy.contracts import (
    ChallengeInput,
    EnvironmentConfig,
    EvidenceRule,
    PermittedTool,
)
from ctf_agent.models import Action, ExecutionResult

from ctf_ingest import KnowledgeStore, records_from_store
from ctf_ingest.models import KnowledgeRecord
from ctf_ingest.retrieval import KnowledgeRetriever, RetrievalQuery

from .knowledge_dependent_benchmark_v2 import (
    BASELINE_SOLVABLE,
    BASE_URL,
    KNOWLEDGE_DEPENDENT,
    KDCaseV2,
    MISLEADING,
    NOISE,
    _INDICATOR_RICH,
    _SQL_URL,
    _Verifier,
    _constraints,
    web_environment,
)
from .knowledge_dependent_harness_v2 import run_experiment_v2

# Bland description: no mechanism indicators, so the frozen brain genuinely stalls in control.
_BLAND_WEB = "A web application is available at the provided endpoint. Recover the flag."


# --------------------------------------------------------------------------------------------
# SQLi-real environment (additive; mirrors web_environment but the id param is the real path)
# --------------------------------------------------------------------------------------------
class _SqliProbe:
    name = "http_probe"

    def __init__(self, *, real_flag: str) -> None:
        self.real_flag = real_flag
        self.calls = 0

    def execute(self, action: Action) -> ExecutionResult:
        self.calls += 1
        query = parse_qs(urlsplit(action.target).query)
        if "id" in query:  # SQL injection is the authoritative supporting path here
            return ExecutionResult(
                action.action_id, action.tool, http_status=200,
                response_body=f"SQL_ROWS_EXPANDED rows leaked flag {self.real_flag}",
            )
        if "name" in query:  # template is NOT evaluated (SSTI is a dead end in this env)
            return ExecutionResult(
                action.action_id, action.tool, http_status=200,
                response_body="LITERAL_TEMPLATE {{7*7}} not evaluated",
            )
        return ExecutionResult(action.action_id, action.tool, http_status=200, response_body="normal")


def sqli_web_environment(root: Path, *, flag: str) -> EnvironmentConfig:
    """A web env where SQL injection on ?id is the authoritative supporting path (reuses the
    existing evidence-rule / verifier machinery; nothing in ctf_agent is modified)."""
    root.mkdir(parents=True, exist_ok=True)
    probe = _SqliProbe(real_flag=flag)
    verifier = _Verifier(flag)
    return EnvironmentConfig(
        permitted_tools=(
            PermittedTool("http_probe", probe, authoritative_sources=(_SQL_URL,), network=True, remote=True),
            PermittedTool("flag_verifier", verifier, verifier=True, remote=True),
        ),
        evidence_rules=(
            EvidenceRule(
                "web-sqli",
                supporting_body_contains=("SQL_ROWS_EXPANDED",),
                contradicting_body_contains=("SQL_NOT_VULNERABLE",),
                authoritative_sources=(_SQL_URL,),
            ),
            EvidenceRule(
                "web-ssti",
                supporting_body_contains=("EVAL=49",),
                contradicting_body_contains=("LITERAL_TEMPLATE",),
                authoritative_sources=(f"{BASE_URL}?name=%7B%7B7%2A7%7D%7D",),
            ),
        ),
        verifier_route=CandidateVerifierRoute("flag_verifier", "local-grader"),
        workspace_root=root,
        journal_path=root / "journal.jsonl",
        run_id=root.name,
    )


# --------------------------------------------------------------------------------------------
# DomeCTF-specific evaluation cases
# --------------------------------------------------------------------------------------------
def _challenge(name: str, description: str) -> ChallengeInput:
    return ChallengeInput(
        name=name, category="web", description=description, hints=(),
        flag_format="CTF{...}", urls=(BASE_URL,),
    )


def build_domectf_eval_cases(root: Path) -> Tuple[KDCaseV2, ...]:
    """Cases spanning easy / knowledge-transfer / unrelated / misleading.

    All use the web-probe environment because that is the only executable environment the frozen
    knowledge->action integration supports. Flags are NEW (never historical DomeCTF flags), so a
    solve cannot come from replaying a memorized flag — the current challenge must be verified.
    """
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)

    def ssti_env(sub: str, flag: str, decoy: str = ""):
        return lambda: web_environment(root / sub, flag=flag, decoy=decoy)

    def sqli_env(sub: str, flag: str):
        return lambda: sqli_web_environment(root / sub, flag=flag)

    # Challenge names are NEUTRAL (they never contain a technique id/name), so retrieval cannot be
    # trivially satisfied by a technique token leaking through the challenge name.
    return (
        # A. EASY — indicator-rich SSTI; solvable on the fast path. Latency + zero-retrieval check.
        KDCaseV2(
            "dc-easy", BASELINE_SOLVABLE,
            _challenge("dc-greeting-studio", _INDICATOR_RICH),
            ssti_env("easy", "CTF{dc_easy_real}"), _constraints(),
            (), "web-ssti", "CTF{dc_easy_real}",
            baseline_should_solve=True, treatment_should_solve=True, max_retrieval_calls=0,
        ),
        # B. KNOWLEDGE-TRANSFER (SQLi) — bland challenge, SQLi is the real path, NEW flag.
        #    DomeCTF's only bridgeable mechanism is sql-injection; this case measures whether that
        #    knowledge is attributable. (Finding: the frozen brain self-solves SQLi, so there is no
        #    headroom for knowledge to be attributable here — see the report.)
        KDCaseV2(
            "dc-transfer-sqli", KNOWLEDGE_DEPENDENT,
            _challenge("dc-web-alpha", _BLAND_WEB),
            sqli_env("transfer_sqli", "CTF{dc_transfer_sqli_real}"), _constraints(),
            (), "web-sqli", "CTF{dc_transfer_sqli_real}",
            baseline_should_solve=False, treatment_should_solve=True,
        ),
        # B'. KNOWLEDGE-TRANSFER (SSTI) — bland challenge, SSTI real, NEW flag. DomeCTF has NO ssti
        #     technique, so config C cannot bridge it: it will try its only bridgeable mechanism
        #     (sql-injection), which current evidence on this SSTI env correctly rejects. This is the
        #     honest coverage boundary + a wrong-mechanism-rejection safety demonstration.
        KDCaseV2(
            "dc-transfer-ssti", KNOWLEDGE_DEPENDENT,
            _challenge("dc-web-beta", _BLAND_WEB),
            ssti_env("transfer_ssti", "CTF{dc_transfer_ssti_real}"), _constraints(),
            (), "web-ssti", "CTF{dc_transfer_ssti_real}",
            baseline_should_solve=False, treatment_should_solve=False,
        ),
        # C. UNRELATED — bland web challenge; DomeCTF crypto/pwn/forensics knowledge is irrelevant.
        #    Expect bounded retrieval, no solve, no hypothesis explosion.
        KDCaseV2(
            "dc-unrelated", NOISE,
            _challenge("dc-web-gamma", _BLAND_WEB),
            ssti_env("unrelated", "CTF{dc_unrelated_real}"), _constraints(),
            (), "web-ssti", None,
            baseline_should_solve=False, treatment_should_solve=False,
        ),
        # D. MISLEADING — SSTI is the real path but a SQLi decoy is present. DomeCTF's sql-injection
        #    knowledge points at SQLi; current evidence (SQL_NOT_VULNERABLE) must reject it and the
        #    decoy flag must never verify.
        KDCaseV2(
            "dc-misleading", MISLEADING,
            _challenge("dc-web-delta", _BLAND_WEB),
            ssti_env("misleading", "CTF{dc_misleading_real}", decoy="CTF{dc_sqli_decoy_never}"),
            _constraints(), (), "web-sqli", None,
            baseline_should_solve=False, treatment_should_solve=False,
            decoy_flag="CTF{dc_sqli_decoy_never}",
        ),
    )


# --------------------------------------------------------------------------------------------
# retriever configs (the ONLY variable across arms)
# --------------------------------------------------------------------------------------------
def load_records(store_dir: Path) -> List[KnowledgeRecord]:
    try:
        return list(records_from_store(KnowledgeStore(store_dir)))
    except Exception:
        return []


def build_config_factories(agent_root: Path) -> Dict[str, Optional[Callable]]:
    local = load_records(agent_root / "knowledge" / "local_writeups")
    jiaje = load_records(agent_root / "knowledge" / "jiaje_v1")
    redbud = load_records(agent_root / "knowledge" / "jiaje_redbud_v1" / "store")
    domectf = load_records(agent_root / "knowledge" / "domectf_v1" / "store")

    def mk(records):
        return lambda case: KnowledgeRetriever.from_records(records)

    return {
        "A_control": None,  # handled by the harness control arm (retriever=None)
        "B_generic_jiaje": mk(local + jiaje),
        "C_domectf": mk(domectf),
        "D_combined": mk(local + jiaje + redbud + domectf),
        "_corpus_sizes": {"local": len(local), "jiaje": len(jiaje), "redbud": len(redbud), "domectf": len(domectf)},
    }


# --------------------------------------------------------------------------------------------
# historical-reference retrieval recall (memorization-oriented; NOT solving)
# --------------------------------------------------------------------------------------------
def historical_reference_recall(domectf_records: Sequence[KnowledgeRecord], k: int = 5) -> Dict[str, object]:
    """Query the DomeCTF retriever with each challenge's own identity and measure whether its
    record (and a technique) is retrieved. This measures memorization/retrieval recall only."""
    retriever = KnowledgeRetriever.from_records(list(domectf_records))
    per_case = []
    hits = 0
    tech_hits = 0
    for rec in domectf_records:
        meta = rec.metadata
        query = RetrievalQuery(
            text=" ".join(p for p in (meta.name, meta.category, " ".join(t.name for t in rec.techniques[:3])) if p),
            category=meta.category or "", keywords=(),
        )
        results = retriever.retrieve(query, k=k)
        ids = [r.record.record_id for r in results]
        found = rec.record_id in ids
        rank = ids.index(rec.record_id) + 1 if found else None
        top_tech = {t.technique_id for r in results for t in r.record.techniques}
        own_tech = {t.technique_id for t in rec.techniques}
        tech_ok = bool(own_tech & top_tech)
        hits += int(found)
        tech_hits += int(tech_ok)
        per_case.append({
            "challenge": meta.name, "year": rec.provenance.extra.get("year", ""),
            "category": meta.category, "retrieved_self": found, "self_rank": rank,
            "mechanism_recall": tech_ok,
        })
    n = len(domectf_records) or 1
    return {
        "k": k,
        "records": len(domectf_records),
        "self_recall_at_k": round(hits / n, 4),
        "mechanism_recall_at_k": round(tech_hits / n, 4),
        "note": "memorization/retrieval recall only; NOT a solve. Historical flags are never treated as verification.",
        "per_case": per_case,
    }


# --------------------------------------------------------------------------------------------
# A/B/C/D orchestration + performance aggregation
# --------------------------------------------------------------------------------------------
_ADVERSARIAL_KINDS = {MISLEADING, NOISE}
_EASY_KINDS = {BASELINE_SOLVABLE}


def _p90(values: List[float]) -> Optional[float]:
    vals = [v for v in values if v is not None]
    if len(vals) < 5:
        return None
    vals = sorted(vals)
    idx = min(len(vals) - 1, int(round(0.9 * (len(vals) - 1))))
    return round(vals[idx], 3)


def _aggregate_metrics(cases: List[dict]) -> Dict[str, object]:
    def col(key):
        return [c["metrics"].get(key) for c in cases if c["metrics"].get(key) is not None]

    def stat(key):
        vals = col(key)
        if not vals:
            return {"mean": None, "median": None, "p90": None}
        return {"mean": round(statistics.mean(vals), 3), "median": round(statistics.median(vals), 3), "p90": _p90(vals)}

    return {
        "time_to_first_action_ms": stat("time_to_first_action_ms"),
        "time_to_verified_ms": stat("time_to_verified_ms"),
        "actions_per_solve": stat("actions_per_solve"),
        "retrieval_calls_per_solve": stat("retrieval_calls_per_solve"),
        "total_unnecessary_retrievals": sum(col("unnecessary_retrievals")),
        "total_duplicate_actions": sum(col("duplicate_actions")),
        "total_budget_violations": sum(col("budget_violations")),
        "false_verifications": sum(1 for c in cases if c["metrics"].get("false_verification")),
        "false_disproofs": sum(1 for c in cases if c["metrics"].get("false_disproof")),
        "stopping_correct_cases": sum(1 for c in cases if c["metrics"].get("stopping_correct")),
        "fast_path_zero_retrieval_cases": sum(1 for c in cases if c["metrics"].get("retrieval_calls_per_solve") == 0),
    }


def run_domectf_ab(work_root: Path, agent_root: Path) -> Dict[str, object]:
    """Run the DomeCTF A/B/C/D evaluation over the DomeCTF eval cases.

    Control (arm A) is retriever=None (identical across configs). Treatments B/C/D differ ONLY in
    which knowledge corpus is available. Returns a structured result dict.
    """
    work_root = Path(work_root)
    work_root.mkdir(parents=True, exist_ok=True)
    factories = build_config_factories(agent_root)
    corpus_sizes = factories.pop("_corpus_sizes")

    cases = build_domectf_eval_cases(work_root / "cases")
    treatment_configs = ["B_generic_jiaje", "C_domectf", "D_combined"]

    control_summary: Dict[str, dict] = {}
    per_config: Dict[str, dict] = {}

    for config in treatment_configs:
        report = run_experiment_v2(work_root / config, cases=cases, retriever_factory=factories[config])
        d = report.to_dict()
        per_config[config] = {
            "verdict": d["verdict"],
            "knowledge_attributable_verified_solves": d["knowledge_attributable_verified_solves"],
            "all_safety_invariants_preserved": d["all_safety_invariants_preserved"],
            "cases": {c["case_id"]: c for c in d["cases"]},
            "aggregate": _aggregate_metrics(d["cases"]),
            "aggregate_by_kind": {
                "easy": _aggregate_metrics([c for c in d["cases"] if c["kind"] in _EASY_KINDS]),
                "knowledge_dependent": _aggregate_metrics([c for c in d["cases"] if c["kind"] == KNOWLEDGE_DEPENDENT]),
                "adversarial": _aggregate_metrics([c for c in d["cases"] if c["kind"] in _ADVERSARIAL_KINDS]),
            },
        }
        # Control arm is identical across configs; capture once.
        if not control_summary:
            for c in d["cases"]:
                control_summary[c["case_id"]] = c["control"]

    return {
        "corpus_sizes": corpus_sizes,
        "configs": ["A_control", *treatment_configs],
        "control_A": control_summary,
        "treatments": per_config,
    }
