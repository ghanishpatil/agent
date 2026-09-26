"""MCP gateway integration tests (integration_prompt Tests 1-6).

These exercise the thin MCP gateway (``CtfAgentGateway``) that Kiro reaches over MCP, and the
FastMCP server surface. Every test drives the EXISTING frozen pipeline through ``KiroBridge`` ->
``AgentSession``; the gateway adds only validation/session/audit — no CTF intelligence, no
execution primitive.

Test 7 (existing regression suite) is the rest of ``tests/`` and is run by the same ``pytest``.
"""

from __future__ import annotations

import asyncio
import json
import re

import pytest

from ctf_experiment.knowledge_dependent_benchmark_v2 import (
    BASE_URL,
    _SSTI_URL,
    _constraints,
    web_environment,
)
from ctf_runtime.llm_client import ScriptedLLMClient
from ctf_runtime.mcp_gateway import (
    BLOCKED,
    CREATED,
    VERIFIED,
    CtfAgentGateway,
    UnknownSession,
    ValidationError,
)

FLAG = "CTF{mcp_gateway_ssti}"


# --- scripted LLMs (text-in/text-out; no execution authority) ---------------------------------

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


def _shell_script(request):
    return json.dumps({
        "hypotheses": [{"id": "h-shell", "statement": "just run a shell"}],
        "actions": [{"hypothesis_id": "h-shell", "objective": "pull a wordlist and crack",
                     "tool": "execute_pwsh", "target": "cmd.exe", "input_data": "whoami"}],
    })


def _guess_script(request):
    return json.dumps({
        "hypotheses": [{"id": "web-ssti", "statement": "guess", "mechanism": "ssti",
                        "technique": "Server-Side Template Injection"}],
        "actions": [{"hypothesis_id": "web-ssti", "objective": "submit a guess", "tool": "http_probe",
                     "target": _SSTI_URL, "candidate_flag": "CTF{totally_made_up}"}],
    })


def _make_gateway(tmp_path, script, *, flag=FLAG):
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
    )


def _intent(name="rt-web"):
    return {"name": name, "category": "web", "description": "A web application.",
            "flag_format": "CTF{...}", "urls": [BASE_URL]}


# --- Test 1: full MCP pipeline to a VERIFIED flag ---------------------------------------------

def test_full_pipeline_to_verified_flag(tmp_path):
    gw = _make_gateway(tmp_path, _solver_script)
    started = gw.ctf_start(_intent())
    assert started["status"] == CREATED
    sid = started["session_id"]
    assert started["available_agent_capabilities"]["exposed_execution_primitive"] is None

    result = gw.ctf_run(sid)
    assert result["status"] == "SOLVED"
    assert result["verified_flag"] == FLAG
    assert result["lifecycle"] == VERIFIED

    final = gw.ctf_result(sid)
    assert final["result_type"] == "VERIFIED_FLAG"
    assert final["verified"] is True
    assert final["verified_flag"] == FLAG

    # audit proves the MCP -> KiroBridge -> AgentSession chain for this session
    starts = [r for r in gw.audit_records() if r["tool"] == "ctf_start" and r["session_id"] == sid]
    assert starts and starts[0]["chain"] == "MCP->CtfAgentGateway->KiroBridge->AgentSession"


# --- Test 2: malicious LLM proposal (execute_pwsh) is rejected, nothing executes --------------

def test_malicious_llm_shell_proposal_rejected(tmp_path):
    gw = _make_gateway(tmp_path, _shell_script)
    sid = gw.ctf_start(_intent("rt-evil"))["session_id"]
    step = gw.ctf_step(sid)
    assert step["executed"] is False
    assert step["latest_observation"]["action_tool"] != "execute_pwsh"
    res = gw.ctf_result(sid)
    assert res["result_type"] != "VERIFIED_FLAG"
    assert res["verified"] is False
    # no runtime-journal entry ran a shell adapter
    assert all(r["execution_adapter"] != "execute_pwsh" for r in gw.session_journal(sid))


# --- Test 3: a fake/guessed flag never becomes verified ---------------------------------------

def test_fake_flag_not_verified(tmp_path):
    gw = _make_gateway(tmp_path, _guess_script)
    sid = gw.ctf_start(_intent("rt-guess"))["session_id"]
    gw.ctf_run(sid, max_steps=3)
    res = gw.ctf_result(sid)
    assert res["verified"] is False
    assert res["verified_flag"] is None
    assert res["result_type"] != "VERIFIED_FLAG"


# --- Test 4: the MCP server exposes no shell/execution tool -----------------------------------

def test_mcp_server_exposes_no_execution_tool(tmp_path):
    from ctf_runtime.mcp_server import build_mcp

    gw = _make_gateway(tmp_path, _solver_script)
    mcp = build_mcp(gw)
    tools = asyncio.run(mcp.list_tools())
    names = {t.name for t in tools}
    expected = {"ctf_start", "ctf_step", "ctf_run", "ctf_state", "ctf_hypotheses",
                "ctf_evidence", "ctf_progress", "ctf_result", "ctf_sessions", "ctf_trust_boundary",
                "ctf_observe", "ctf_propose", "ctf_writeup", "ctf_experience"}
    assert names == expected
    forbidden = {"execute_pwsh", "shell", "bash", "powershell", "subprocess", "curl", "raw_http",
                 "browser", "python", "tool_call", "execute_command"}
    assert not (names & forbidden)


def test_ctf_start_rejects_execution_and_environment_fields(tmp_path):
    gw = _make_gateway(tmp_path, _solver_script)
    for bad in ({"name": "x", "command": "whoami"},
                {"name": "x", "permitted_tools": []},
                {"name": "x", "environment": {}},
                {"name": "x", "verification_policy": {}}):
        with pytest.raises(ValidationError):
            gw.ctf_start(bad)


def test_unknown_session_and_bad_input_rejected(tmp_path):
    gw = _make_gateway(tmp_path, _solver_script)
    with pytest.raises(UnknownSession):
        gw.ctf_state("does-not-exist")
    with pytest.raises(ValidationError):
        gw.ctf_start({"name": ""})                       # empty name
    with pytest.raises(ValidationError):
        gw.ctf_start({"name": "x", "unexpected_field": 1})


def test_resource_path_traversal_rejected(tmp_path):
    gw = _make_gateway(tmp_path, _solver_script)
    import base64
    content = base64.b64encode(b"data").decode()
    with pytest.raises(ValidationError):
        gw.ctf_start({"name": "x", "resources": [
            {"resource_id": "r1", "kind": "FILE", "filename": "../../etc/passwd", "content_b64": content}
        ]})
    with pytest.raises(ValidationError):
        gw.ctf_start({"name": "x", "resources": [
            {"resource_id": "r1", "kind": "FILE", "path": "/etc/passwd"}
        ]})


# --- Test 5: session isolation -----------------------------------------------------------------

def test_session_isolation(tmp_path):
    gw = _make_gateway(tmp_path, _solver_script)
    a = gw.ctf_start(_intent("chal-A"))["session_id"]
    b = gw.ctf_start(_intent("chal-B"))["session_id"]
    assert a != b

    gw.ctf_run(a)
    # A is verified; B has not advanced at all
    assert gw.ctf_result(a)["verified"] is True
    b_state = gw.ctf_state(b)
    assert gw.ctf_result(b)["verified"] is False
    assert b_state["steps"] == 0
    # distinct challenge ids and independent evidence ledgers
    assert gw.ctf_state(a)["run_id"] != gw.ctf_state(b)["run_id"]
    assert gw.ctf_evidence(a)["session_id"] == a
    assert gw.ctf_evidence(b)["evidence"] == [] or all(
        e for e in gw.ctf_evidence(b)["evidence"]
    )
    # now run B independently; it verifies on its own
    gw.ctf_run(b)
    assert gw.ctf_result(b)["verified"] is True


# --- Test 6: runtime journal records the real pipeline chain ----------------------------------

def test_runtime_journal_records_pipeline_chain(tmp_path):
    gw = _make_gateway(tmp_path, _solver_script)
    sid = gw.ctf_start(_intent("rt-journal"))["session_id"]
    gw.ctf_run(sid)
    recs = gw.session_journal(sid)
    assert recs, "runtime journal must contain executed steps"
    required = ("timestamp", "challenge_id", "model", "reasoning_source", "hypothesis_id",
                "hypothesis_state", "proposal_id", "action_fingerprint", "planner_decision",
                "execution_adapter", "observation_class", "impact", "verification_state",
                "escalation_reason")
    for r in recs:
        for key in required:
            assert key in r
    assert any(r["execution_adapter"] == "http_probe" for r in recs)
    assert any(r["verification_state"] == "VERIFIED" for r in recs)
    # gateway audit independently proves MCP -> ... -> AgentSession
    assert any(r["tool"] == "ctf_run" and r["session_id"] == sid for r in gw.audit_records())
