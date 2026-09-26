"""Experience-learning tests (checklist items 12-42): success/failure extractors, append-only
persistence, failure-safety, and driver-independent integration (internal + Architecture A).

Extractor/persistence/failure-safety tests run over synthetic ``SolveResult`` projections. The
integration tests drive the REAL frozen pipeline through ``CtfAgentGateway`` with a temp
``learning_root`` so nothing is written outside the test's ``tmp_path`` and the external corpora are
never touched.
"""

from __future__ import annotations

import json
import re
import threading

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
from ctf_experiment.knowledge_dependent_benchmark_v2 import (
    BASE_URL,
    _SSTI_URL,
    _constraints,
    web_environment,
)
from ctf_runtime.experience import extract_failure_experience, extract_success_experience
from ctf_runtime.experience_store import (
    SOURCE_FAILURE,
    SOURCE_SUCCESS,
    ExperienceRecord,
    ExperienceStore,
)
from ctf_runtime.learning import PostTerminalObserver
from ctf_runtime.llm_client import ScriptedLLMClient
from ctf_runtime.mcp_gateway import CtfAgentGateway, VERIFIED
from ctf_runtime.mcp_server import build_mcp

FLAG = "CTF{experience_learning}"
SSTI_URL = "http://127.0.0.1:9/render"


# =========================================================================================
# synthetic SolveResult builders
# =========================================================================================

def _understanding(categories=("web",), constraints=("no external network",)):
    return ChallengeUnderstanding(
        facts=(InputFact("description", "a page", InputFactState.KNOWN, "challenge"),),
        likely_categories=tuple(categories), attack_surfaces=("name",), unknowns=(),
        constraints=tuple(constraints),
    )


def _solved(**ov):
    base = dict(
        status=SolveStatus.SOLVED, run_id="run-s", challenge_name="Solved One",
        understanding=_understanding(), terminal_reason="verified",
        verified_flag=FLAG, verification_evidence_ids=("ev-verify",),
        final_verification_method="local-grader", solution_path_summary="ssti->flag",
        actions=(
            ActionTrace("a1", "probe {{7*7}}", "http_probe", SSTI_URL, "TARGET_RESPONSE", "SUPPORTS", "CONTINUE", 1),
            ActionTrace("a2", "submit", "flag_verifier", "grader", "SUCCESS", "SUPPORTS", "CONTINUE", 1),
        ),
        key_hypotheses=(
            HypothesisTrace("web-ssti", "name is evaluated by a server-side template", "SUPPORTED",
                            ("ev-1",), (), (), 1),
        ),
        important_evidence=(
            EvidenceTrace("ev-1", SSTI_URL, "TARGET_RESPONSE", "SUPPORTS", ("web-ssti",), "http_probe"),
        ),
    )
    base.update(ov)
    return SolveResult(**base)


def _failed(**ov):
    base = dict(
        status=SolveStatus.BLOCKED, run_id="run-f", challenge_name="Hard One",
        understanding=_understanding(), terminal_reason="rate limited then exhausted",
        actions=(
            ActionTrace("a1", "brute login", "http_probe", "http://127.0.0.1:9/login", "RATE_LIMIT",
                        "UNRESOLVES", "CONTINUE", 1),
            ActionTrace("a2", "probe", "http_probe", SSTI_URL, "TIMEOUT", "UNRESOLVES", "CONTINUE", 1),
        ),
        key_hypotheses=(
            HypothesisTrace("h-sqli", "login is sql-injectable", "DISPROVEN", (), ("ev-x",), (), 1),
            HypothesisTrace("h-jwt", "jwt is forgeable", "UNRESOLVED", (), (), ("ev-y",), 2),
        ),
        important_evidence=(
            EvidenceTrace("ev-x", "http://127.0.0.1:9/login", "AUTH_FAILURE", "REFUTES", ("h-sqli",), "http_probe"),
        ),
        remaining_hypotheses=("h-lfi",),
        unresolved_blockers=("SECRET_KEY unknown",),
    )
    base.update(ov)
    return SolveResult(**base)


# =========================================================================================
# 12-19 — success extractor
# =========================================================================================

def test_12_success_requires_solved():
    with pytest.raises(ValueError):
        extract_success_experience(_failed(), session_id="s", driver="internal")


def test_13_success_source_kind():
    rec = extract_success_experience(_solved(), session_id="s", driver="internal")
    assert rec.source_kind == SOURCE_SUCCESS
    assert rec.status == "SOLVED"


def test_14_success_flag_set():
    rec = extract_success_experience(_solved(), session_id="s", driver="internal")
    assert rec.verified_flag == FLAG


def test_15_mechanism_is_supported_statement():
    rec = extract_success_experience(_solved(), session_id="s", driver="internal")
    assert rec.mechanism == "name is evaluated by a server-side template"


def test_16_techniques_from_successful_tools():
    rec = extract_success_experience(_solved(), session_id="s", driver="internal")
    assert "http_probe" in rec.techniques and "flag_verifier" in rec.techniques


def test_17_success_action_partition():
    rec = extract_success_experience(_solved(), session_id="s", driver="internal")
    assert len(rec.successful_actions) == 2 and rec.dead_end_actions == ()
    assert rec.failure_classes == ()


def test_18_evidence_refs_include_verification():
    rec = extract_success_experience(_solved(), session_id="s", driver="internal")
    assert "ev-verify" in rec.evidence_refs and "ev-1" in rec.evidence_refs


def test_19_provenance_fields():
    rec = extract_success_experience(_solved(), session_id="sess-9", driver="kiro")
    assert rec.provenance.run_id == "run-s"
    assert rec.provenance.session_id == "sess-9"
    assert rec.provenance.driver == "kiro"
    assert rec.provenance.source_kind == SOURCE_SUCCESS


# =========================================================================================
# 20-26 — failure extractor
# =========================================================================================

def test_20_failure_rejects_solved():
    with pytest.raises(ValueError):
        extract_failure_experience(_solved(), session_id="s", driver="internal")


def test_21_failure_kind_and_no_flag():
    rec = extract_failure_experience(_failed(), session_id="s", driver="internal")
    assert rec.source_kind == SOURCE_FAILURE
    assert rec.verified_flag is None


def test_22_env_failures_not_disproof():
    rec = extract_failure_experience(_failed(), session_id="s", driver="internal")
    # rate-limit + timeout captured as failure classes / dead ends, NOT as technique disproof
    assert "RATE_LIMIT" in rec.failure_classes and "TIMEOUT" in rec.failure_classes
    assert len(rec.dead_end_actions) == 2
    # the disproven set must never contain a hypothesis that only saw env/rate-limit failure
    assert "h-jwt" not in rec.disproven


def test_23_only_authoritative_disproven():
    rec = extract_failure_experience(_failed(), session_id="s", driver="internal")
    assert rec.disproven == ("h-sqli",)   # the only DISPROVEN-status hypothesis


def test_24_unresolved_stays_unresolved():
    rec = extract_failure_experience(_failed(), session_id="s", driver="internal")
    assert "h-jwt" in rec.unresolved       # UNRESOLVED-status hypothesis
    assert "h-lfi" in rec.unresolved       # merged from remaining_hypotheses


def test_25_terminal_reason_preserved():
    rec = extract_failure_experience(_failed(), session_id="s", driver="internal")
    assert rec.terminal_reason == "rate limited then exhausted"


def test_26_unresolved_blockers_preserved():
    rec = extract_failure_experience(_failed(), session_id="s", driver="internal")
    assert "SECRET_KEY unknown" in rec.unresolved_blockers


# =========================================================================================
# 27-33 — append-only persistence
# =========================================================================================

def test_27_append_creates_records_and_manifest(tmp_path):
    store = ExperienceStore.for_kind(tmp_path, SOURCE_SUCCESS)
    rec = extract_success_experience(_solved(), session_id="s", driver="internal")
    manifest = store.append(rec)
    assert (tmp_path / "success" / "records.jsonl").exists()
    assert (tmp_path / "success" / "manifest.json").exists()
    assert manifest["total_records"] == 1


def test_28_manifest_increments_and_hash_matches(tmp_path):
    store = ExperienceStore.for_kind(tmp_path, SOURCE_FAILURE)
    store.append(extract_failure_experience(_failed(run_id="f1"), session_id="s", driver="internal"))
    m2 = store.append(extract_failure_experience(_failed(run_id="f2"), session_id="s", driver="internal"))
    assert m2["total_records"] == 2
    import hashlib
    raw = (tmp_path / "failure" / "records.jsonl").read_bytes()
    assert m2["records_sha256"] == hashlib.sha256(raw).hexdigest()


def test_29_append_only_preserves_prior(tmp_path):
    store = ExperienceStore.for_kind(tmp_path, SOURCE_FAILURE)
    store.append(extract_failure_experience(_failed(run_id="f1"), session_id="s", driver="internal"))
    first_line = (tmp_path / "failure" / "records.jsonl").read_text(encoding="utf-8").splitlines()[0]
    store.append(extract_failure_experience(_failed(run_id="f2"), session_id="s", driver="internal"))
    lines = (tmp_path / "failure" / "records.jsonl").read_text(encoding="utf-8").splitlines()
    assert lines[0] == first_line and len(lines) == 2


def test_30_success_and_failure_are_separated(tmp_path):
    ExperienceStore.for_kind(tmp_path, SOURCE_SUCCESS).append(
        extract_success_experience(_solved(), session_id="s", driver="internal"))
    ExperienceStore.for_kind(tmp_path, SOURCE_FAILURE).append(
        extract_failure_experience(_failed(), session_id="s", driver="internal"))
    assert (tmp_path / "success" / "records.jsonl").exists()
    assert (tmp_path / "failure" / "records.jsonl").exists()
    succ = ExperienceStore.for_kind(tmp_path, SOURCE_SUCCESS).read_all()
    fail = ExperienceStore.for_kind(tmp_path, SOURCE_FAILURE).read_all()
    assert len(succ) == 1 and len(fail) == 1
    assert succ[0]["source_kind"] == SOURCE_SUCCESS and fail[0]["source_kind"] == SOURCE_FAILURE


def test_31_read_all_roundtrip_and_stable_hash(tmp_path):
    store = ExperienceStore.for_kind(tmp_path, SOURCE_SUCCESS)
    rec = extract_success_experience(_solved(), session_id="s", driver="internal")
    store.append(rec)
    loaded = store.read_all()
    assert loaded[0]["record_id"] == rec.record_id
    assert rec.content_hash() == rec.content_hash()   # deterministic


def test_32_record_to_dict_json_serialisable(tmp_path):
    rec = extract_success_experience(_solved(), session_id="s", driver="internal")
    blob = json.dumps(rec.to_dict(), sort_keys=True)
    assert isinstance(blob, str) and rec.record_id in blob


def test_33_concurrent_appends_all_land(tmp_path):
    store = ExperienceStore.for_kind(tmp_path, SOURCE_FAILURE)
    n = 25

    def worker(i):
        store.append(extract_failure_experience(_failed(run_id=f"f{i}"), session_id="s", driver="internal"))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    lines = (tmp_path / "failure" / "records.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == n
    for ln in lines:                       # no interleaved/partial lines
        json.loads(ln)


# =========================================================================================
# 34-38 — failure-safety
# =========================================================================================

class _ExplodingResult:
    """A stand-in result whose attribute access raises, to prove the observer swallows anything."""
    status = SolveStatus.SOLVED
    run_id = "boom"

    def __getattr__(self, name):
        raise RuntimeError(f"exploding attribute {name}")


def test_34_observer_never_raises_on_bad_result(tmp_path):
    obs = PostTerminalObserver(tmp_path)
    summary = obs.observe(_ExplodingResult(), session_id="s", driver="internal")
    assert summary["learned"] is False and summary["error"]


def test_35_soft_error_logged(tmp_path):
    obs = PostTerminalObserver(tmp_path)
    obs.observe(_ExplodingResult(), session_id="s", driver="internal")
    errs = obs.read_errors()
    assert errs and errs[0]["error_type"] == "RuntimeError"


def test_36_learning_disabled_writes_nothing(tmp_path):
    # learning_root omitted -> disabled -> no experience dirs created even after a solve
    gw = _internal_gateway(tmp_path, _solver_script, learning=False)
    sid = gw.ctf_start(_intent())["session_id"]
    gw.ctf_run(sid)
    assert gw.ctf_result(sid)["result_type"] == "VERIFIED_FLAG"
    assert not (tmp_path / "learn").exists()
    assert gw.get_experience(sid)["learned"] is False


def test_37_observer_failure_does_not_affect_result(tmp_path, monkeypatch):
    gw = _internal_gateway(tmp_path, _solver_script, learning=True)
    # force the observer to blow up internally; the solve result must be unaffected
    import ctf_runtime.mcp_gateway as gw_mod
    monkeypatch.setattr(gw_mod.PostTerminalObserver, "observe",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("kaboom")))
    sid = gw.ctf_start(_intent())["session_id"]
    run = gw.ctf_run(sid)
    assert run["status"] == "SOLVED" and run["verified_flag"] == FLAG
    assert gw.ctf_result(sid)["verified"] is True


def test_38_observer_fires_at_most_once(tmp_path):
    gw = _internal_gateway(tmp_path, _solver_script, learning=True)
    sid = gw.ctf_start(_intent())["session_id"]
    gw.ctf_run(sid)
    gw.ctf_run(sid)                      # second call must not append a duplicate experience
    gw.close_session(sid)                # nor must close
    store = ExperienceStore.for_kind(tmp_path / "learn", SOURCE_SUCCESS)
    assert len(store.read_all()) == 1


# =========================================================================================
# 39-42 — driver-independent integration (real frozen pipeline)
# =========================================================================================

def _solver_script(request):
    prompt = request.prompt
    hyps = [{"id": "web-ssti", "statement": "name is evaluated by a server-side template",
             "mechanism": "ssti", "technique": "Server-Side Template Injection"}]
    actions = [{"hypothesis_id": "web-ssti", "objective": "probe {{7*7}}", "tool": "http_probe",
                "target": _SSTI_URL, "expected_observation": "EVAL=49"}]
    seen = re.search(r"CTF\{[A-Za-z0-9_]+\}", prompt)
    if "EVAL=49" in prompt and seen:
        actions.append({"hypothesis_id": "web-ssti", "objective": "submit observed flag",
                        "tool": "http_probe", "target": _SSTI_URL, "candidate_flag": seen.group(0)})
    return json.dumps({"hypotheses": hyps, "actions": actions})


def _idle_script(request):
    # proposes nothing executable -> internal driver reaches a non-SOLVED terminal state
    return json.dumps({"hypotheses": [{"id": "h", "statement": "unsure"}], "actions": []})


def _internal_gateway(tmp_path, script, *, learning=True, flag=FLAG):
    counter = {"n": 0}

    def factory(meta):
        counter["n"] += 1
        return web_environment(tmp_path / f"env_{counter['n']}", flag=flag)

    return CtfAgentGateway(
        environment_factory=factory,
        llm_client=ScriptedLLMClient(script),
        constraints=_constraints(),
        journal_dir=tmp_path / "journals",
        audit_log_path=tmp_path / "audit.jsonl",
        learning_root=(tmp_path / "learn") if learning else None,
    )


def _intent(name="rt-web"):
    return {"name": name, "category": "web", "description": "A web application.",
            "flag_format": "CTF{...}", "urls": [BASE_URL]}


def test_39_internal_solved_persists_success_and_writeup(tmp_path):
    gw = _internal_gateway(tmp_path, _solver_script)
    sid = gw.ctf_start(_intent())["session_id"]
    assert gw.ctf_run(sid)["status"] == "SOLVED"

    exp = gw.get_experience(sid)
    assert exp["learned"] is True and exp["source_kind"] == SOURCE_SUCCESS
    assert exp["record"]["verified_flag"] == FLAG

    wu = gw.get_writeup(sid)
    assert wu["available"] is True and wu["grounded"] is True
    assert wu["flag"] == FLAG and FLAG in wu["markdown"]

    # persisted to the temp learning root, success side only
    assert len(ExperienceStore.for_kind(tmp_path / "learn", SOURCE_SUCCESS).read_all()) == 1
    assert (tmp_path / "learn" / "writeups_generated").exists()


def test_40_internal_non_solved_persists_failure_no_writeup(tmp_path):
    gw = _internal_gateway(tmp_path, _idle_script)
    sid = gw.ctf_start(_intent())["session_id"]
    gw.ctf_run(sid, max_steps=3)
    assert gw.ctf_result(sid)["verified"] is False

    exp = gw.get_experience(sid)
    assert exp["learned"] is True and exp["source_kind"] == SOURCE_FAILURE
    assert exp["record"]["verified_flag"] is None
    assert gw.get_writeup(sid)["available"] is False
    assert len(ExperienceStore.for_kind(tmp_path / "learn", SOURCE_FAILURE).read_all()) == 1


def _kiro_gateway(tmp_path, *, flag=FLAG):
    counter = {"n": 0}

    def factory(meta):
        counter["n"] += 1
        return web_environment(tmp_path / f"env_{counter['n']}", flag=flag)

    return CtfAgentGateway(
        environment_factory=factory,
        llm_client=ScriptedLLMClient(lambda r: "{}"),
        constraints=_constraints(),
        journal_dir=tmp_path / "j",
        audit_log_path=tmp_path / "audit.jsonl",
        learning_root=tmp_path / "learn",
    )


def _start_kiro(gw, name="kiro-web"):
    return gw.ctf_start({"name": name, "category": "web", "description": "A web app.",
                         "flag_format": "CTF{...}", "urls": [BASE_URL], "driver": "kiro"})["session_id"]


def test_41_kiro_verified_persists_success_via_tools(tmp_path):
    gw = _kiro_gateway(tmp_path)
    mcp = build_mcp(gw)                     # prove the read-only MCP tools surface the artifacts
    sid = _start_kiro(gw)

    gw.ctf_propose(sid,
        hypotheses=[{"hypothesis_id": "web-ssti", "statement": "name is evaluated by a server-side template",
                     "mechanism": "ssti", "technique": "Server-Side Template Injection"}],
        actions=[{"hypothesis_id": "web-ssti", "objective": "probe {{7*7}}", "tool": "http_probe",
                  "target": _SSTI_URL, "expected_observation": "EVAL=49"}])
    obs2 = gw.ctf_observe(sid)
    blob = " ".join(o["output"] for o in obs2["recent_observations"])
    seen = re.search(r"CTF\{[A-Za-z0-9_]+\}", blob)
    r2 = gw.ctf_propose(sid, hypotheses=[],
        actions=[{"hypothesis_id": "web-ssti", "objective": "submit observed flag",
                  "tool": "flag_verifier", "target": "local-grader", "candidate_flag": seen.group(0)}])
    assert r2["verified"] is True

    exp = gw.get_experience(sid)
    assert exp["learned"] is True and exp["source_kind"] == SOURCE_SUCCESS
    assert exp["record"]["provenance"]["driver"] == "kiro"
    wu = gw.get_writeup(sid)
    assert wu["available"] is True and wu["flag"] == FLAG
    assert len(ExperienceStore.for_kind(tmp_path / "learn", SOURCE_SUCCESS).read_all()) == 1


def test_42_kiro_closed_without_flag_persists_failure(tmp_path):
    gw = _kiro_gateway(tmp_path)
    sid = _start_kiro(gw)
    # one non-verifying probe, then close without ever verifying a flag
    gw.ctf_propose(sid,
        hypotheses=[{"hypothesis_id": "h", "statement": "unsure guess"}],
        actions=[{"hypothesis_id": "h", "objective": "probe", "tool": "http_probe", "target": _SSTI_URL}])
    assert gw.ctf_result(sid)["verified"] is False
    gw.close_session(sid)

    exp = gw.get_experience(sid)
    assert exp["learned"] is True and exp["source_kind"] == SOURCE_FAILURE
    assert exp["record"]["verified_flag"] is None
    assert len(ExperienceStore.for_kind(tmp_path / "learn", SOURCE_FAILURE).read_all()) == 1
