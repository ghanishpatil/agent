"""Architecture A tests — Kiro-driven observe/propose loop.

The TEST plays the role of Kiro's model: it calls ctf_observe, reads authoritative state, decides a
typed proposal, and calls ctf_propose. The gateway feeds proposals through the frozen
validate -> plan -> TrustKernel -> trusted adapter -> evidence -> verification pipeline. No LLM runs
inside the runtime on this path; the flag is read from observed evidence, never injected.
"""

from __future__ import annotations

import re

import pytest

from ctf_experiment.knowledge_dependent_benchmark_v2 import BASE_URL, _SSTI_URL, _constraints, web_environment
from ctf_runtime.llm_client import ScriptedLLMClient
from ctf_runtime.mcp_gateway import CtfAgentGateway, ValidationError

FLAG = "CTF{kiro_driven_ssti}"


def _gateway(tmp_path):
    counter = {"n": 0}

    def factory(meta):
        counter["n"] += 1
        return web_environment(tmp_path / f"env_{counter['n']}", flag=FLAG)

    # llm_client is required by the gateway but UNUSED on the kiro-driven path.
    return CtfAgentGateway(
        environment_factory=factory,
        llm_client=ScriptedLLMClient(lambda r: "{}"),
        constraints=_constraints(),
        journal_dir=tmp_path / "j",
        audit_log_path=tmp_path / "audit.jsonl",
    )


def _start_kiro(gw, name="kiro-web"):
    return gw.ctf_start({"name": name, "category": "web", "description": "A web app.",
                         "flag_format": "CTF{...}", "urls": [BASE_URL], "driver": "kiro"})["session_id"]


# --- POSITIVE: full observe -> propose -> execute -> observe -> propose -> VERIFIED_FLAG -------

def test_kiro_driven_full_loop_to_verified(tmp_path):
    gw = _gateway(tmp_path)
    sid = _start_kiro(gw)

    # 1) observe initial state (no evidence yet); available tools include the trusted probe+verifier
    obs = gw.ctf_observe(sid)
    assert obs["verified"] is False and obs["hypotheses"] == []
    assert "http_probe" in obs["available_tools"] and "proposal_schema" in obs

    # 2) "Kiro reasons": propose the SSTI hypothesis + a discriminating probe action
    r1 = gw.ctf_propose(sid,
        hypotheses=[{"hypothesis_id": "web-ssti", "statement": "name is evaluated by a server-side template",
                     "mechanism": "ssti", "technique": "Server-Side Template Injection"}],
        actions=[{"hypothesis_id": "web-ssti", "objective": "probe {{7*7}}", "tool": "http_probe",
                  "target": _SSTI_URL, "expected_observation": "EVAL=49"}])
    assert any(a == "http_probe" for a in r1["accepted"]["actions"])
    assert len(r1["executed"]) == 1 and r1["verified"] is False

    # 3) observe again: the REAL adapter output is now visible; extract the flag from evidence
    obs2 = gw.ctf_observe(sid)
    blob = " ".join(o["output"] for o in obs2["recent_observations"])
    assert "EVAL=49" in blob
    seen = re.search(r"CTF\{[A-Za-z0-9_]+\}", blob)
    assert seen and seen.group(0) == FLAG   # flag came from observed evidence, not injected

    # 4) "Kiro reasons again": submit the observed flag through the verifier
    r2 = gw.ctf_propose(sid, hypotheses=[],
        actions=[{"hypothesis_id": "web-ssti", "objective": "submit observed flag",
                  "tool": "flag_verifier", "target": "local-grader", "candidate_flag": seen.group(0)}])
    assert r2["verified"] is True and r2["result_type"] == "VERIFIED_FLAG"
    assert r2["verified_flag"] == FLAG

    # 5) result + journal prove the full pipeline
    assert gw.ctf_result(sid)["result_type"] == "VERIFIED_FLAG"
    adapters = {j["execution_adapter"] for j in gw.session_journal(sid)}
    assert "http_probe" in adapters and "flag_verifier" in adapters


# --- NEGATIVE: proposals that must be rejected without executing -------------------------------

def test_kiro_execute_pwsh_proposal_rejected(tmp_path):
    gw = _gateway(tmp_path)
    sid = _start_kiro(gw)
    r = gw.ctf_propose(sid,
        hypotheses=[{"hypothesis_id": "h", "statement": "run a shell"}],
        actions=[{"hypothesis_id": "h", "objective": "crack it", "tool": "execute_pwsh",
                  "target": "cmd.exe", "input_data": "whoami"}])
    assert r["executed"] == []
    assert any(x["kind"] == "action" and "not registered" in x["reason"] for x in r["rejected"])
    assert r["verified"] is False


def test_kiro_unknown_tool_and_malformed_rejected(tmp_path):
    gw = _gateway(tmp_path)
    sid = _start_kiro(gw)
    r = gw.ctf_propose(sid, hypotheses=[{"hypothesis_id": "h", "statement": "x"}],
        actions=[{"hypothesis_id": "h", "objective": "curl it", "tool": "curl", "target": "http://x"},
                 {"hypothesis_id": "h", "objective": "", "tool": "http_probe", "target": ""},  # empty objective+target
                 {"not": "an action"}])
    assert r["executed"] == []
    assert len(r["rejected"]) >= 3


def test_kiro_fake_flag_not_verified(tmp_path):
    gw = _gateway(tmp_path)
    sid = _start_kiro(gw)
    # propose a candidate flag with no supporting evidence -> cannot verify
    gw.ctf_propose(sid, hypotheses=[{"hypothesis_id": "web-ssti", "statement": "guess",
                                     "mechanism": "ssti", "technique": "Server-Side Template Injection"}],
        actions=[{"hypothesis_id": "web-ssti", "objective": "submit a guess", "tool": "http_probe",
                  "target": _SSTI_URL, "candidate_flag": "CTF{totally_made_up}"}])
    res = gw.ctf_result(sid)
    assert res["verified"] is False and res["verified_flag"] is None


def test_kiro_duplicate_action_deduplicated(tmp_path):
    gw = _gateway(tmp_path)
    sid = _start_kiro(gw)
    hyp = [{"hypothesis_id": "web-ssti", "statement": "ssti", "mechanism": "ssti",
            "technique": "Server-Side Template Injection"}]
    act = [{"hypothesis_id": "web-ssti", "objective": "probe", "tool": "http_probe", "target": _SSTI_URL}]
    r1 = gw.ctf_propose(sid, hypotheses=hyp, actions=act)
    assert len(r1["executed"]) == 1
    r2 = gw.ctf_propose(sid, hypotheses=[], actions=act)   # identical action, unchanged state
    assert r2["executed"] == []   # deduplicated -> not executed again


def test_kiro_session_isolation(tmp_path):
    gw = _gateway(tmp_path)
    a = _start_kiro(gw, "A")
    b = _start_kiro(gw, "B")
    assert a != b
    gw.ctf_propose(a, hypotheses=[{"hypothesis_id": "web-ssti", "statement": "ssti", "mechanism": "ssti",
                                   "technique": "Server-Side Template Injection"}],
                   actions=[{"hypothesis_id": "web-ssti", "objective": "probe", "tool": "http_probe", "target": _SSTI_URL}])
    assert len(gw.ctf_observe(a)["evidence"]) >= 1
    assert gw.ctf_observe(b)["evidence"] == []   # B untouched by A


def test_kiro_driver_rejects_internal_tools(tmp_path):
    gw = _gateway(tmp_path)
    sid = _start_kiro(gw)
    with pytest.raises(ValidationError):
        gw.ctf_run(sid)
    with pytest.raises(ValidationError):
        gw.ctf_step(sid)


def test_internal_driver_rejects_kiro_tools(tmp_path):
    gw = _gateway(tmp_path)
    # default gateway driver is internal when not specified
    sid = gw.ctf_start({"name": "internal-web", "category": "web", "description": "d",
                        "flag_format": "CTF{...}", "urls": [BASE_URL]})["session_id"]
    with pytest.raises(ValidationError):
        gw.ctf_observe(sid)
    with pytest.raises(ValidationError):
        gw.ctf_propose(sid, [], [])
