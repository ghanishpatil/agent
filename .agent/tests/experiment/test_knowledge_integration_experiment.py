"""Controlled Knowledge-Augmented Solver Integration tests (checklist items 1-20).

Integration items run the REAL frozen pipeline through ``solve_experimental`` over the knowledge-v2
benchmark (control = knowledge OFF, treatment = knowledge EXPERIMENTAL). Unit items exercise the
treatment source / translator boundary directly. Nothing here executes tools itself; all execution
is owned by the frozen TrustKernel + trusted adapters.
"""

from __future__ import annotations

from urllib.parse import quote

import pytest

from ctf_agent.autonomy.contracts import (
    ActionTrace,
    ChallengeUnderstanding,
    EvidenceTrace,
    HypothesisTrace,
    InputFact,
    InputFactState,
    SolveResult,
    SolveStatus,
)

from ctf_ingest.models import (
    ChallengeMetadata,
    KnowledgeRecord,
    Provenance,
    ReasoningTrajectory,
    SourceType,
    Technique,
    TrajectoryStep,
    TrajectoryStepKind as K,
)

from ctf_experiment.knowledge_dependent_benchmark_v2 import BASE_URL, build_cases_v2
from ctf_experiment.knowledge_solver import solve_with_knowledge
from ctf_experiment.knowledge_translation import (
    Applicability,
    KnowledgeOrigin,
    KnowledgeTranslator,
    TranslationContext,
    TranslationStatus,
)
from ctf_experiment.knowledge_experiment import (
    ExperimentalTranslationSource,
    KnowledgeContribution,
    KnowledgeMode,
    KnowledgeTrace,
    classify_contribution,
    run_knowledge_integration_experiment,
    solve_experimental,
)
from ctf_ingest.retrieval import KnowledgeRetriever


# =========================================================================================
# helpers / fixtures
# =========================================================================================

@pytest.fixture
def cases(tmp_path):
    return {c.case_id: c for c in build_cases_v2(tmp_path / "bench")}


def _env(case, tmp_path, arm):
    from dataclasses import replace
    base = case.environment_factory()
    root = tmp_path / f"{case.case_id}-{arm}"
    root.mkdir(parents=True, exist_ok=True)
    return replace(base, workspace_root=root, journal_path=root / "journal.jsonl",
                   run_id=f"{case.case_id}-{arm}")


def _experimental(case, tmp_path, arm="t", control=None):
    return solve_experimental(
        case.challenge, (), _env(case, tmp_path, arm), case.constraints,
        retriever=KnowledgeRetriever.from_records(case.treatment_records),
        knowledge_mode=KnowledgeMode.EXPERIMENTAL,
        control_result=(control.result if control else None),
    )


def _off(case, tmp_path, arm="c"):
    return solve_experimental(case.challenge, (), _env(case, tmp_path, arm), case.constraints,
                              knowledge_mode=KnowledgeMode.OFF)


class _StubBrain:
    def suggest_hypotheses(self, context):
        return ()

    def suggest_actions(self, context):
        return ()

    def interpret(self, context):
        return ()


def _ssti_record(rid="ext-ssti", steps=(), source_uri="https://ex.invalid/w"):
    return KnowledgeRecord(
        record_id=rid, content_hash="h",
        provenance=Provenance(SourceType.HTTP, source_uri, document_path="ssti.md"),
        metadata=ChallengeMetadata(name="c", category="web"),
        techniques=(Technique("ssti", "Server-Side Template Injection", "web", confidence=0.9),),
        trajectory=ReasoningTrajectory(steps=tuple(steps)),
        title="c", summary="s",
    )


def _source(mode=KnowledgeMode.EXPERIMENTAL, tools=("http_probe", "flag_verifier")):
    return ExperimentalTranslationSource(
        _StubBrain(), None, knowledge_mode=mode, available_tools=tools, verifier_tool="flag_verifier",
    )


def _ctx(**ov):
    base = dict(category="web", target_urls=(BASE_URL,), available_tools=("http_probe", "flag_verifier"),
                verifier_tool="flag_verifier")
    base.update(ov)
    return TranslationContext(**base)


def _ingest_all(src, record, ctx):
    added = []
    for tr in src.translator.translate_record(record, ctx):
        added.append((tr, src._ingest_translation(tr, record.record_id)))
    return added


# synthetic SolveResult builder for classify_contribution unit tests
def _understanding():
    return ChallengeUnderstanding(
        facts=(InputFact("description", "d", InputFactState.KNOWN, "c"),),
        likely_categories=("web",), attack_surfaces=("name",), unknowns=(), constraints=(),
    )


def _solved_result(hyp_id="web-ssti", flag="CTF{x}"):
    return SolveResult(
        status=SolveStatus.SOLVED, run_id="r", challenge_name="c", understanding=_understanding(),
        terminal_reason="verified", verified_flag=flag, verification_evidence_ids=("ev",),
        final_verification_method="local-grader",
        actions=(ActionTrace("a1", "knowledge-derived discriminating test for SSTI", "http_probe",
                             "t", "TARGET_RESPONSE", "SUPPORTS", "CONTINUE", 1),),
        key_hypotheses=(HypothesisTrace(hyp_id, "ssti", "SUPPORTED", ("ev",), (), (), 1),),
    )


# =========================================================================================
# 1-2: mode switch
# =========================================================================================

def test_1_off_preserves_existing_behavior(cases, tmp_path):
    # OFF must match the established knowledge-off baseline (solve_with_knowledge retriever=None).
    for cid in ("kd2-knowledge-dependent", "kd2-baseline-solvable"):
        case = cases[cid]
        off = _off(case, tmp_path, "off")
        baseline = solve_with_knowledge(case.challenge, (), _env(case, tmp_path, "base"),
                                        case.constraints, retriever=None)
        assert off.result.status is baseline.result.status
        assert off.result.verified_flag == baseline.result.verified_flag
        assert len(off.result.actions) == len(baseline.result.actions)
        assert off.contribution is KnowledgeContribution.NO_KNOWLEDGE
        assert off.trace.proposals == []


def test_2_experimental_activates_translation(cases, tmp_path):
    case = cases["kd2-knowledge-dependent"]
    off = _off(case, tmp_path, "off")
    treat = _experimental(case, tmp_path, "t", control=off)
    assert off.result.status is SolveStatus.BLOCKED          # brain alone cannot
    assert treat.result.status is SolveStatus.SOLVED         # knowledge bridges it
    assert treat.trace.proposals                              # translation actually ran


# =========================================================================================
# 3-4: proposal reaches planner / invalid rejected
# =========================================================================================

def test_3_valid_proposal_reaches_planning_path(cases, tmp_path):
    case = cases["kd2-knowledge-dependent"]
    off = _off(case, tmp_path, "off")
    treat = _experimental(case, tmp_path, "t", control=off)
    executed = [a for a in treat.result.actions
                if a.objective.startswith("knowledge-derived discriminating test")
                and a.decision != "DUPLICATE"]
    assert executed                                           # planner accepted + executed it
    assert executed[0].tool == "http_probe"


def test_4_invalid_proposal_is_downgraded_not_executed():
    # no probe tool available (only the verifier) -> translator downgrades -> no probe registered
    src = _source(tools=("flag_verifier",))
    added = _ingest_all(src, _ssti_record(), _ctx(available_tools=("flag_verifier",)))
    assert all(not was_probe for _tr, was_probe in added)
    assert src._knowledge_probes == []
    assert any(tr.status is TranslationStatus.HYPOTHESIS_ONLY for tr, _ in added)


# =========================================================================================
# 5-7: safety downgrades (missing target / host mismatch / encoding mismatch)
# =========================================================================================

def test_5_missing_target_downgrade():
    src = _source()
    added = _ingest_all(src, _ssti_record(), _ctx(target_urls=()))
    assert src._knowledge_probes == []
    tr = added[0][0]
    assert tr.status is TranslationStatus.HYPOTHESIS_ONLY and "target_url" in tr.missing_requirements


def test_6_host_mismatch_downgrade():
    src = _source()
    rec = _ssti_record(steps=(TrajectoryStep(3, K.NEXT_ACTION, "send {{7*7}} to https://prod.example.com/x"),))
    added = _ingest_all(src, rec, _ctx())   # current host is local.invalid
    assert src._knowledge_probes == []
    assert src.trace.alignment_failures >= 1


def test_7_encoding_mismatch_downgrade():
    tr_layer = KnowledgeTranslator()
    raw_star = f"{BASE_URL}?name=" + "{{7*7}}"     # raw '*' authoritative target
    res = tr_layer.translate_record(_ssti_record(), _ctx(exact_targets=(raw_star,)))[0]
    assert res.status is TranslationStatus.HYPOTHESIS_ONLY and "byte-match" in res.reason


# =========================================================================================
# 8: historical flag cannot become current flag
# =========================================================================================

def test_8_historical_flag_cannot_become_current(cases, tmp_path):
    # the misleading case ships a decoy flag inside knowledge; it must never verify.
    case = cases["kd2-misleading"]
    off = _off(case, tmp_path, "off")
    treat = _experimental(case, tmp_path, "t", control=off)
    assert treat.result.verified_flag != "CTF{sqli_decoy_should_never_verify}"
    assert treat.result.verified_flag in (None,)             # nothing verified
    # and every knowledge probe carried an empty candidate_flag
    src = _source()
    _ingest_all(src, _ssti_record(steps=(TrajectoryStep(9, K.VERIFICATION,
                "the flag was CTF{historical_from_writeup}"),)), _ctx())
    assert all(p.candidate_flag == "" for p in src._knowledge_probes)


# =========================================================================================
# 9-12: authority boundaries
# =========================================================================================

def test_9_knowledge_cannot_mark_verification():
    # a knowledge probe cannot assert verification: no candidate_flag, hypothesis has no status field
    src = _source()
    _ingest_all(src, _ssti_record(), _ctx())
    assert src._knowledge_probes and all(p.candidate_flag == "" for p in src._knowledge_probes)
    hyp = next(iter(src._knowledge_hypotheses.values()))
    assert not hasattr(hyp, "status")


def test_10_knowledge_cannot_mark_disproven():
    # translating a rate-limited failure experience stays UNRESOLVED, never disproven
    from ctf_runtime.experience_store import SOURCE_FAILURE, ExperienceProvenance, ExperienceRecord
    exp = ExperienceRecord(
        record_id="e", source_kind=SOURCE_FAILURE, status="BLOCKED",
        provenance=ExperienceProvenance("run", "sess", "internal", SOURCE_FAILURE),
        mechanism="sqli", failure_classes=("RATE_LIMIT",), unresolved=("web-sqli",),
    )
    res = KnowledgeTranslator().translate_experience(exp, _ctx())[0]
    assert res.applicability is Applicability.UNRESOLVED
    assert res.status is TranslationStatus.HYPOTHESIS_ONLY


def test_11_knowledge_cannot_bypass_kernel():
    # the source only produces inert proposal DATA; it exposes no execution/verification primitive
    src = _source()
    for attr in ("execute", "run_tool", "verify", "http", "shell", "process"):
        assert not hasattr(src, attr)
    _ingest_all(src, _ssti_record(), _ctx())
    # probes are inert CandidateAction data (converted + validated + planned by the frozen pipeline)
    assert all(type(p).__name__ == "CandidateAction" for p in src._knowledge_probes)


def test_12_knowledge_cannot_execute_tools_directly():
    # translating never touches the network/filesystem; result is data only (no side effects)
    src = _source()
    added = _ingest_all(src, _ssti_record(), _ctx())
    assert added and src._knowledge_probes            # produced a proposal
    # the probe is a suggestion, not an execution: no result/observation attached
    p = src._knowledge_probes[0]
    assert not hasattr(p, "result") and not hasattr(p, "observation")


# =========================================================================================
# 13-15: dedup / failure-safety / conflict resolution
# =========================================================================================

def test_13_duplicate_knowledge_action_suppressed(cases, tmp_path):
    case = cases["kd2-knowledge-dependent"]
    treat = _experimental(case, tmp_path, "t")
    # the same knowledge probe target must be executed at most once (existing dedup owns this)
    knowledge_targets = [a.target for a in treat.result.actions
                         if a.objective.startswith("knowledge-derived discriminating test")
                         and a.decision != "DUPLICATE"]
    assert len(knowledge_targets) == len(set(knowledge_targets))


def test_14_knowledge_failure_falls_back_safely(cases, tmp_path):
    class _BrokenRetriever:
        def retrieve(self, query, k=5):
            raise RuntimeError("retrieval exploded")

    case = cases["kd2-knowledge-dependent"]
    out = solve_experimental(
        case.challenge, (), _env(case, tmp_path, "broken"), case.constraints,
        retriever=_BrokenRetriever(), knowledge_mode=KnowledgeMode.EXPERIMENTAL,
    )
    # solver did not crash; it fell back to the normal (brain-only) path and stayed safe
    assert out.result.status in (SolveStatus.BLOCKED, SolveStatus.EXHAUSTED, SolveStatus.FAILED)
    assert out.trace.errors                                   # the failure was isolated + logged
    assert out.result.verified_flag is None


def test_15_conflict_resolved_in_favor_of_current_evidence(cases, tmp_path):
    # conflicting knowledge (SSTI-yes vs SSTI-is-a-dead-end): current evidence decides, no false disproof
    case = cases["kd2-conflicting"]
    off = _off(case, tmp_path, "off")
    treat = _experimental(case, tmp_path, "t", control=off)
    assert treat.result.status is SolveStatus.SOLVED
    hyp = next((h for h in treat.result.key_hypotheses if h.hypothesis_id == "web-ssti"), None)
    assert hyp is not None and hyp.status != "DISPROVEN"     # knowledge cannot force a disproof


# =========================================================================================
# 16-19: provenance + attribution
# =========================================================================================

def test_16_provenance_preserved(cases, tmp_path):
    case = cases["kd2-knowledge-dependent"]
    treat = _experimental(case, tmp_path, "t")
    assert treat.trace.proposals
    p = treat.trace.proposals[0]
    assert p["origin"] == KnowledgeOrigin.EXTERNAL_WRITEUP.value
    assert p["source_record_id"] and p["technique_id"] == "ssti"


def test_17_attribution_is_evidence_based(cases, tmp_path):
    rep = run_knowledge_integration_experiment(tmp_path / "eval")
    by_id = {c.case_id: c for c in rep.cases}
    assert by_id["kd2-knowledge-dependent"].contribution == \
        KnowledgeContribution.KNOWLEDGE_DIRECTLY_ENABLED_SOLVE.value
    assert by_id["kd2-conflicting"].contribution == \
        KnowledgeContribution.KNOWLEDGE_DIRECTLY_ENABLED_SOLVE.value
    assert rep.all_safety_preserved and rep.total_fabricated_attempts == 0


def test_18_retrieved_but_unused_writeup_not_counted():
    # knowledge proposed a hypothesis but NO knowledge test executed (brain solved independently)
    trace = KnowledgeTrace()
    trace.proposals.append({"hypothesis_id": "web-ssti", "technique_id": "ssti", "status": "RUNNABLE_TEST",
                            "origin": "EXTERNAL_WRITEUP", "source_record_id": "r"})
    # a verified solve whose actions contain NO knowledge-derived test
    result = SolveResult(
        status=SolveStatus.SOLVED, run_id="r", challenge_name="c", understanding=_understanding(),
        terminal_reason="v", verified_flag="CTF{x}", verification_evidence_ids=("ev",),
        final_verification_method="grader",
        actions=(ActionTrace("a1", "brain probe", "http_probe", "t", "TARGET_RESPONSE",
                             "SUPPORTS", "CONTINUE", 1),),
        key_hypotheses=(HypothesisTrace("web-ssti", "s", "SUPPORTED", ("ev",), (), (), 1),),
    )
    assert classify_contribution(result, trace) is KnowledgeContribution.KNOWLEDGE_HYPOTHESIS_ONLY


def test_19_knowledge_guided_verified_test_counted():
    trace = KnowledgeTrace()
    trace.proposals.append({"hypothesis_id": "web-ssti", "technique_id": "ssti", "status": "RUNNABLE_TEST",
                            "origin": "EXTERNAL_WRITEUP", "source_record_id": "r"})
    result = _solved_result()
    control_unsolved = SolveResult(status=SolveStatus.BLOCKED, run_id="c", challenge_name="c",
                                   understanding=_understanding(), terminal_reason="blocked")
    assert classify_contribution(result, trace, control_result=control_unsolved) is \
        KnowledgeContribution.KNOWLEDGE_DIRECTLY_ENABLED_SOLVE
    # if the control ALSO solved independently, it is NOT knowledge-directly-enabled
    control_solved = _solved_result()
    assert classify_contribution(result, trace, control_result=control_solved) is \
        KnowledgeContribution.KNOWLEDGE_GUIDED_TEST


# =========================================================================================
# 20: environment failure of a knowledge-guided test stays unresolved (never technique disproof)
# =========================================================================================

def test_20_timeout_rate_limit_stays_unresolved():
    from ctf_runtime.experience_store import SOURCE_FAILURE, ExperienceProvenance, ExperienceRecord
    for cls in ("TIMEOUT", "RATE_LIMIT", "NETWORK_FAILURE"):
        exp = ExperienceRecord(
            record_id="e", source_kind=SOURCE_FAILURE, status="BLOCKED",
            provenance=ExperienceProvenance("run", "sess", "internal", SOURCE_FAILURE),
            mechanism="sqli", failure_classes=(cls,), unresolved=("web-sqli",),
        )
        res = KnowledgeTranslator().translate_experience(exp, _ctx())[0]
        assert res.applicability is Applicability.UNRESOLVED
        assert res.applicability is not Applicability.DISPROVEN_ELSEWHERE
        assert res.status is TranslationStatus.HYPOTHESIS_ONLY
