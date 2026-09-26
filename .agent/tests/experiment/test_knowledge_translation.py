"""Generalized Knowledge Translation Layer tests.

Covers the required checklist: existing SSTI/SQLi compatibility, cross-category generalization,
safety (no-invention + target/encoding alignment), trajectory semantics, provenance, determinism,
authority (advisory-only + frozen proposal validators), and experience-record translation.
"""

from __future__ import annotations

from urllib.parse import quote

import pytest

from ctf_agent.adapters import AdapterRegistry
from ctf_agent.proposals import (
    ProposalRejected,
    validate_action_suggestion,
    validate_hypothesis_suggestion,
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

from ctf_experiment.knowledge_reasoning import _WEB_TESTS
from ctf_experiment.knowledge_translation import (
    Applicability,
    KnowledgeOrigin,
    KnowledgeTranslator,
    MechanismTemplate,
    RunnableSpec,
    TemplateRegistry,
    TranslationContext,
    TranslationStatus,
    extract_trajectory,
)

from ctf_runtime.experience_store import (
    SOURCE_FAILURE,
    SOURCE_SUCCESS,
    ExperienceProvenance,
    ExperienceRecord,
)

BASE = "http://127.0.0.1:9/"
WEB_TOOLS = ("http_probe", "flag_verifier")


# =========================================================================================
# builders
# =========================================================================================

def _record(*, record_id="rec", category="web", techniques=(), steps=(),
            source_uri="https://ex.invalid/writeup", document_path="w.md", completeness=0.5):
    return KnowledgeRecord(
        record_id=record_id, content_hash="h",
        provenance=Provenance(SourceType.HTTP, source_uri, document_path=document_path),
        metadata=ChallengeMetadata(name="c", category=category),
        techniques=tuple(techniques),
        trajectory=ReasoningTrajectory(steps=tuple(steps), completeness=completeness),
        title="c", summary="s",
    )


def _tech(tid, name, category="web", confidence=0.9, evidence=""):
    return Technique(technique_id=tid, name=name, category=category, confidence=confidence, evidence=evidence)


def _step(order, kind, text, confidence=0.7):
    return TrajectoryStep(order=order, kind=kind, text=text, confidence=confidence)


def _web_ctx(**ov):
    base = dict(category="web", target_urls=(BASE,), available_tools=WEB_TOOLS,
                verifier_tool="flag_verifier")
    base.update(ov)
    return TranslationContext(**base)


def _experience(*, source_kind, mechanism="", techniques=(), disproven=(), unresolved=(),
                failure_classes=(), record_id="exp", run_id="run-x", session_id="sess-x",
                driver="internal", status="SOLVED"):
    prov = ExperienceProvenance(run_id=run_id, session_id=session_id, driver=driver,
                                source_kind=source_kind)
    return ExperienceRecord(
        record_id=record_id, source_kind=source_kind, status=status, provenance=prov,
        challenge_name="c", category="web", mechanism=mechanism, techniques=tuple(techniques),
        disproven=tuple(disproven), unresolved=tuple(unresolved),
        failure_classes=tuple(failure_classes),
    )


@pytest.fixture
def tr():
    return KnowledgeTranslator()


# =========================================================================================
# A. Existing behavior (1-2) + _WEB_TESTS compatibility
# =========================================================================================

def test_1_existing_ssti_translation_still_works(tr):
    rec = _record(techniques=(_tech("ssti", "Server-Side Template Injection"),),
                  steps=(_step(2, K.CANDIDATE_MECHANISM, "server-side template injection in name"),))
    res = tr.translate_record(rec, _web_ctx())[0]
    assert res.status is TranslationStatus.RUNNABLE_TEST
    assert res.runnable_action.tool == "http_probe"
    assert res.runnable_action.target == f"{BASE}?name={quote('{{7*7}}')}"


def test_2_existing_sqli_translation_still_works(tr):
    rec = _record(techniques=(_tech("sql-injection", "SQL Injection"),))
    res = tr.translate_record(rec, _web_ctx())[0]
    assert res.status is TranslationStatus.RUNNABLE_TEST
    sqli_payload = "1' OR '1'='1"
    assert res.runnable_action.target == BASE + "?id=" + quote(sqli_payload)


def test_web_tests_target_construction_is_equivalent(tr):
    # The seeded templates must reproduce _WEB_TESTS' exact target construction, byte-for-byte.
    for tid, wt in _WEB_TESTS.items():
        rec = _record(record_id=f"rec-{tid}", techniques=(_tech(tid, wt.technique),))
        res = tr.translate_record(rec, _web_ctx())[0]
        assert res.status is TranslationStatus.RUNNABLE_TEST
        expected_target = f"{BASE}?{wt.param}={quote(wt.payload)}"
        assert res.runnable_action.target == expected_target
        assert res.runnable_action.expected_observation == wt.expected_observation
        assert res.hypothesis.hypothesis_id == wt.hypothesis_id


# =========================================================================================
# B. Generalization across categories (3-6)
# =========================================================================================

@pytest.mark.parametrize("tid, name, category", [
    ("mersenne-twister-prng", "PRNG State Recovery", "crypto"),        # 3 crypto
    ("dynamic-analysis", "Dynamic Analysis", "reverse"),               # 4 reverse
    ("audio-steganography", "Audio Steganography", "forensics"),       # 5 forensics
    ("format-string", "Format String", "pwn"),                         # 6a pwn
    ("python-jail-escape", "Python Jail Escape", "misc"),              # 6b misc
])
def test_3_to_6_cross_category_translation(tr, tid, name, category):
    rec = _record(record_id=f"rec-{tid}", category=category, techniques=(_tech(tid, name, category),))
    res = tr.translate_record(rec, _web_ctx(category=category))[0]
    # generalized: a mechanism + hypothesis + described test even with no runnable payload
    assert res.status is TranslationStatus.HYPOTHESIS_ONLY
    assert res.runnable_action is None
    assert res.hypothesis is not None and res.mechanism
    assert res.discriminating_test                     # a described test is always present
    assert res.technique_id == tid


def test_generalization_not_web_only(tr):
    # A non-web trajectory with no structured technique still extracts a mechanism via prose.
    rec = _record(category="crypto", techniques=(),
                  steps=(_step(2, K.CANDIDATE_MECHANISM, "the RNG looks like mt19937 / predictable random"),))
    res = tr.translate_record(rec, _web_ctx(category="crypto"))[0]
    assert res.status is TranslationStatus.HYPOTHESIS_ONLY
    assert res.technique_id == "mersenne-twister-prng"


# =========================================================================================
# C. Safety (7-14)
# =========================================================================================

def test_7_missing_target_hypothesis_only(tr):
    rec = _record(techniques=(_tech("ssti", "Server-Side Template Injection"),))
    res = tr.translate_record(rec, _web_ctx(target_urls=()))[0]
    assert res.status is TranslationStatus.HYPOTHESIS_ONLY
    assert "target_url" in res.missing_requirements
    assert res.runnable_action is None


def test_8_missing_parameter_hypothesis_only(tr):
    # a stricter template that requires the parameter to be grounded in current evidence
    reg = TemplateRegistry()
    reg.register(MechanismTemplate(
        technique_id="reflected-xss", category="web", mechanism="reflected xss",
        technique="Reflected XSS", hypothesis_id="web-xss",
        hypothesis_statement="a reflected parameter may execute injected markup",
        discriminating_test="inject a marker into the reflected parameter",
        runnable=RunnableSpec(kind="web_query_probe", param="q", payload="<x>",
                              expected_observation="the marker is reflected unescaped",
                              param_must_be_grounded=True),
    ))
    tr2 = KnowledgeTranslator(reg)
    rec = _record(techniques=(_tech("reflected-xss", "Reflected XSS"),))
    # 'q' is NOT among known_parameters -> hypothesis-only
    res = tr2.translate_record(rec, _web_ctx(known_parameters=("id",)))[0]
    assert res.status is TranslationStatus.HYPOTHESIS_ONLY
    assert any(m.startswith("parameter:") for m in res.missing_requirements)
    # when grounded, it becomes runnable
    res2 = tr2.translate_record(rec, _web_ctx(known_parameters=("q",)))[0]
    assert res2.status is TranslationStatus.RUNNABLE_TEST


def test_9_missing_payload_hypothesis_only(tr):
    # a template that names a mechanism but ships NO runnable synthesis (no payload) -> hyp-only
    rec = _record(category="web", techniques=(_tech("jwt-algorithm-confusion", "JWT Algorithm Confusion"),))
    res = tr.translate_record(rec, _web_ctx())[0]
    assert res.status is TranslationStatus.HYPOTHESIS_ONLY
    assert res.runnable_action is None
    assert res.mechanism and res.discriminating_test


def test_10_missing_required_evidence_hypothesis_only(tr):
    # no probe tool available (only the verifier) -> cannot run -> hypothesis-only
    rec = _record(techniques=(_tech("ssti", "Server-Side Template Injection"),))
    res = tr.translate_record(rec, _web_ctx(available_tools=("flag_verifier",)))[0]
    assert res.status is TranslationStatus.HYPOTHESIS_ONLY
    assert "probe_tool" in res.missing_requirements


def test_11_target_mismatch_hypothesis_only(tr):
    # retrieved knowledge references a DIFFERENT host than the grounded current target
    rec = _record(
        techniques=(_tech("ssti", "Server-Side Template Injection"),),
        steps=(_step(4, K.NEXT_ACTION, "send {{7*7}} to https://prod.example.com/render"),),
    )
    res = tr.translate_record(rec, _web_ctx())[0]  # current host is 127.0.0.1:9
    assert res.status is TranslationStatus.HYPOTHESIS_ONLY
    assert "alignment failed" in res.reason


def test_12_url_encoding_mismatch_hypothesis_only(tr):
    # exact authoritative target uses a raw '*'; our synthesis encodes '*' as %2A -> mismatch
    rec = _record(techniques=(_tech("ssti", "Server-Side Template Injection"),))
    raw_star_target = f"{BASE}?name=" + "{{7*7}}"          # contains a raw '*', not %2A
    res = tr.translate_record(rec, _web_ctx(exact_targets=(raw_star_target,)))[0]
    assert res.status is TranslationStatus.HYPOTHESIS_ONLY
    assert "byte-match" in res.reason
    # and when the exact target matches the encoded synthesis, it IS runnable
    encoded = f"{BASE}?name={quote('{{7*7}}')}"
    res2 = tr.translate_record(rec, _web_ctx(exact_targets=(encoded,)))[0]
    assert res2.status is TranslationStatus.RUNNABLE_TEST


def test_13_expected_observation_never_invented(tr):
    # prose claims a bogus observation; the runnable action must carry ONLY the template constant
    rec = _record(
        techniques=(_tech("ssti", "Server-Side Template Injection"),),
        steps=(_step(5, K.OBSERVATION, "the server returned SECRET=hunter2 and dumped /etc/passwd"),),
    )
    res = tr.translate_record(rec, _web_ctx())[0]
    assert res.status is TranslationStatus.RUNNABLE_TEST
    assert res.runnable_action.expected_observation == _WEB_TESTS["ssti"].expected_observation
    assert "hunter2" not in res.runnable_action.expected_observation


def test_14_invented_tool_rejected(tr):
    # knowledge references a tool that is NOT available; only grounded available tools may be used
    rec = _record(techniques=(_tech("ssti", "Server-Side Template Injection"),),
                  steps=(_step(4, K.NEXT_ACTION, "use sqlmap and metasploit against the app"),))
    res = tr.translate_record(rec, _web_ctx(available_tools=("http_probe", "flag_verifier")))[0]
    assert res.status is TranslationStatus.RUNNABLE_TEST
    assert res.runnable_action.tool == "http_probe"       # from grounded context, not from prose
    # with no non-verifier tool at all, it cannot invent one
    res2 = tr.translate_record(rec, _web_ctx(available_tools=("flag_verifier",)))[0]
    assert res2.status is TranslationStatus.HYPOTHESIS_ONLY


# =========================================================================================
# D. Trajectory semantics (15-24)
# =========================================================================================

def _full_trajectory():
    return (
        _step(0, K.CHALLENGE_CONTEXT, "a web app renders a greeting"),
        _step(1, K.OBSERVED_CLUE, "the name is reflected"),
        _step(2, K.CANDIDATE_MECHANISM, "server-side template injection"),
        _step(3, K.HYPOTHESIS, "the name parameter is evaluated by a template engine"),
        _step(4, K.DISCRIMINATING_TEST, "send {{7*7}} and look for 49"),
        _step(5, K.OBSERVATION, "response contained 49"),
        _step(6, K.INTERPRETATION, "the template evaluates expressions"),
        _step(7, K.NEXT_ACTION, "read the flag via the template context"),
    )


def test_15_to_20_trajectory_extraction():
    ex = extract_trajectory(ReasoningTrajectory(steps=_full_trajectory()))
    assert ex.mechanism == "server-side template injection"                    # 15
    assert ex.hypothesis.startswith("the name parameter")                      # 16
    assert ex.discriminating_test.startswith("send {{7*7}}")                   # 17
    assert ex.observation == "response contained 49"                           # 18
    assert ex.interpretation == "the template evaluates expressions"           # 19
    assert ex.next_action.startswith("read the flag")                          # 20


def test_21_partial_trajectory():
    ex = extract_trajectory(ReasoningTrajectory(steps=(
        _step(2, K.CANDIDATE_MECHANISM, "sql injection"),
    )))
    assert ex.mechanism == "sql injection"
    assert ex.hypothesis == "" and ex.discriminating_test == ""


def test_22_malformed_trajectory(tr):
    # empty / textless trajectory + no techniques -> NOT_APPLICABLE, no crash
    ex = extract_trajectory(ReasoningTrajectory(steps=(_step(0, K.CANDIDATE_MECHANISM, "   "),)))
    assert ex.mechanism == ""
    rec = _record(techniques=(), steps=())
    res = tr.translate_record(rec, _web_ctx())[0]
    assert res.status is TranslationStatus.NOT_APPLICABLE


def test_23_repeated_trajectory_steps():
    # lowest-order step wins; later differing ones are noted as conflicts, never merged
    ex = extract_trajectory(ReasoningTrajectory(steps=(
        _step(3, K.CANDIDATE_MECHANISM, "sql injection"),
        _step(1, K.CANDIDATE_MECHANISM, "ssti"),
        _step(5, K.CANDIDATE_MECHANISM, "ssti"),   # duplicate of chosen -> not a conflict
    )))
    assert ex.mechanism == "ssti"                   # order 1 wins
    assert any("CANDIDATE_MECHANISM#3" in c for c in ex.conflicts)


def test_24_conflicting_trajectory_steps(tr):
    # two different mechanisms: deterministic pick (lowest order), conflict recorded, not merged
    rec = _record(steps=(
        _step(1, K.CANDIDATE_MECHANISM, "server-side template injection"),
        _step(2, K.CANDIDATE_MECHANISM, "sql injection"),
    ))
    res = tr.translate_record(rec, _web_ctx())[0]
    assert res.mechanism == "server-side template injection"
    assert res.support.extract.conflicts


# =========================================================================================
# E. Provenance (25-27)
# =========================================================================================

def test_25_external_provenance_preserved(tr):
    rec = _record(record_id="ext-42", techniques=(_tech("ssti", "Server-Side Template Injection"),),
                  source_uri="https://jia.je/x", document_path="ssti.md")
    res = tr.translate_record(rec, _web_ctx())[0]
    p = res.provenance
    assert p.origin is KnowledgeOrigin.EXTERNAL_WRITEUP
    assert p.source_id == "ext-42" and p.source_uri == "https://jia.je/x"
    assert p.run_id == "" and p.session_id == ""       # not conflated with agent fields


def test_26_agent_success_provenance_preserved(tr):
    exp = _experience(source_kind=SOURCE_SUCCESS, mechanism="ssti", record_id="exp-succ-1",
                      run_id="run-7", session_id="sess-7", driver="kiro")
    res = tr.translate_experience(exp, _web_ctx())[0]
    p = res.provenance
    assert p.origin is KnowledgeOrigin.AGENT_SUCCESS_EXPERIENCE
    assert p.source_id == "exp-succ-1" and p.run_id == "run-7" and p.driver == "kiro"
    assert p.source_kind == SOURCE_SUCCESS
    assert p.source_uri == ""                          # not conflated with external fields


def test_27_agent_failure_provenance_preserved(tr):
    exp = _experience(source_kind=SOURCE_FAILURE, mechanism="sqli", record_id="exp-fail-1",
                      failure_classes=("RATE_LIMIT",), unresolved=("web-sqli",))
    res = tr.translate_experience(exp, _web_ctx())[0]
    p = res.provenance
    assert p.origin is KnowledgeOrigin.AGENT_FAILURE_EXPERIENCE
    assert p.source_id == "exp-fail-1" and p.source_kind == SOURCE_FAILURE


def test_three_origins_never_collapse(tr):
    origins = set()
    ext = _record(techniques=(_tech("ssti", "SSTI"),))
    origins.add(tr.translate_record(ext, _web_ctx())[0].provenance.origin)
    origins.add(tr.translate_experience(_experience(source_kind=SOURCE_SUCCESS, mechanism="ssti"),
                                        _web_ctx())[0].provenance.origin)
    origins.add(tr.translate_experience(_experience(source_kind=SOURCE_FAILURE, mechanism="ssti"),
                                        _web_ctx())[0].provenance.origin)
    assert origins == {KnowledgeOrigin.EXTERNAL_WRITEUP, KnowledgeOrigin.AGENT_SUCCESS_EXPERIENCE,
                       KnowledgeOrigin.AGENT_FAILURE_EXPERIENCE}


# =========================================================================================
# F. Determinism (28)
# =========================================================================================

def test_28_deterministic_output(tr):
    rec = _record(techniques=(_tech("ssti", "Server-Side Template Injection"),),
                  steps=_full_trajectory())
    a = tr.translate_record(rec, _web_ctx())[0].to_dict()
    b = KnowledgeTranslator().translate_record(rec, _web_ctx())[0].to_dict()
    import json
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


# =========================================================================================
# G. Authority (29-32)
# =========================================================================================

def test_29_translator_never_verifies_flags(tr):
    # even when a historical flag is present in knowledge, it never becomes a candidate flag
    rec = _record(
        techniques=(_tech("ssti", "Server-Side Template Injection"),),
        steps=(_step(9, K.VERIFICATION, "the flag was CTF{historical_flag_from_writeup}"),),
    )
    res = tr.translate_record(rec, _web_ctx())[0]
    assert res.runnable_action.candidate_flag == ""
    assert "CTF{" not in (res.runnable_action.target + res.runnable_action.expected_observation)


def test_30_translator_never_changes_hypothesis_state(tr):
    # produced hypotheses are plain suggestions with no status field / no state assertion
    rec = _record(techniques=(_tech("ssti", "Server-Side Template Injection"),))
    res = tr.translate_record(rec, _web_ctx())[0]
    assert not hasattr(res.hypothesis, "status")
    # a failure experience never yields a DISPROVEN/verified claim, only advisory applicability
    exp = _experience(source_kind=SOURCE_FAILURE, mechanism="sqli", failure_classes=("TIMEOUT",))
    fres = tr.translate_experience(exp, _web_ctx())[0]
    assert fres.applicability is Applicability.UNRESOLVED


def test_31_translator_never_executes_tools(tr):
    # the result is inert data; the runnable action is a suggestion, not an execution
    rec = _record(techniques=(_tech("ssti", "Server-Side Template Injection"),))
    res = tr.translate_record(rec, _web_ctx())[0]
    assert res.runnable_action.__class__.__name__ == "ActionSuggestion"
    assert not hasattr(res, "execute") and not hasattr(tr, "execute")


def test_32_outputs_pass_frozen_planner_kernel_validators(tr):
    # a RUNNABLE_TEST's suggestions must be accepted by the FROZEN proposal validators unchanged
    registry = AdapterRegistry()
    # register a minimal stub adapter named 'http_probe' so the frozen validator sees it
    class _Stub:
        name = "http_probe"
        def run(self, *a, **k):  # pragma: no cover - never called by the translator
            raise AssertionError("translator must not execute")
    registry.register(_Stub())

    rec = _record(techniques=(_tech("ssti", "Server-Side Template Injection"),))
    res = tr.translate_record(rec, _web_ctx())[0]
    validate_hypothesis_suggestion(res.hypothesis)                 # must not raise
    validate_action_suggestion(res.runnable_action, registry)      # must not raise

    # and an action naming an unregistered tool is still rejected by the frozen validator
    empty = AdapterRegistry()
    with pytest.raises(ProposalRejected):
        validate_action_suggestion(res.runnable_action, empty)


# =========================================================================================
# Experience knowledge translation (section 17)
# =========================================================================================

def test_success_experience_yields_advisory_hypothesis(tr):
    exp = _experience(source_kind=SOURCE_SUCCESS, mechanism="ssti", techniques=("http_probe",))
    res = tr.translate_experience(exp, _web_ctx())[0]
    # success experience + grounded web context -> runnable advisory test (still kernel-authorized)
    assert res.status is TranslationStatus.RUNNABLE_TEST
    assert res.applicability is Applicability.PLAUSIBLE
    assert res.provenance.origin is KnowledgeOrigin.AGENT_SUCCESS_EXPERIENCE


def test_success_experience_hypothesis_only_without_grounding(tr):
    exp = _experience(source_kind=SOURCE_SUCCESS, mechanism="ssti")
    res = tr.translate_experience(exp, _web_ctx(target_urls=()))[0]
    assert res.status is TranslationStatus.HYPOTHESIS_ONLY


def test_failure_experience_rate_limit_is_unresolved_not_disproven(tr):
    # SQLi attempt -> HTTP 429 rate limit -> "unresolved / applicability uncertain", NOT disproven
    exp = _experience(source_kind=SOURCE_FAILURE, mechanism="sqli",
                      failure_classes=("RATE_LIMIT",), unresolved=("web-sqli",))
    res = tr.translate_experience(exp, _web_ctx())[0]
    assert res.status is TranslationStatus.HYPOTHESIS_ONLY
    assert res.applicability is Applicability.UNRESOLVED
    assert res.runnable_action is None
    assert "unresolved" in res.reason.lower()
    assert res.applicability is not Applicability.DISPROVEN_ELSEWHERE


def test_failure_experience_authoritative_disproven_is_reduced_applicability(tr):
    # only an authoritative DISPROVEN hypothesis for THIS mechanism reduces applicability
    exp = _experience(source_kind=SOURCE_FAILURE, mechanism="sqli", disproven=("web-sqli",))
    res = tr.translate_experience(exp, _web_ctx())[0]
    assert res.applicability is Applicability.DISPROVEN_ELSEWHERE
    assert res.status is TranslationStatus.HYPOTHESIS_ONLY   # advisory, never a current disproof


# =========================================================================================
# Conflict handling (section 13)
# =========================================================================================

def test_current_evidence_disproves_mechanism_advisory_conflict(tr):
    rec = _record(techniques=(_tech("ssti", "Server-Side Template Injection"),))
    res = tr.translate_record(rec, _web_ctx(disproven_mechanisms=("ssti",)))[0]
    assert res.status is TranslationStatus.ADVISORY_CONFLICT
    assert res.runnable_action is None                       # current evidence wins


def test_knowledge_endpoint_not_in_evidence_is_not_created(tr):
    # knowledge names /login; current challenge has no /login and no grounded target
    rec = _record(
        techniques=(_tech("sql-injection", "SQL Injection"),),
        steps=(_step(3, K.NEXT_ACTION, "attack the /login endpoint"),),
    )
    res = tr.translate_record(rec, _web_ctx(target_urls=()))[0]
    assert res.status is TranslationStatus.HYPOTHESIS_ONLY
    assert "/login" not in (res.runnable_action.target if res.runnable_action else "")
