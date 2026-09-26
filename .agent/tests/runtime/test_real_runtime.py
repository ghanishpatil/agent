"""Security-boundary tests for the operator-controlled REAL runtime (integration_prompt §16).

These exercise the frozen trusted adapters as composed by ``ctf_runtime.real_environment`` plus the
gateway. They are deterministic and require no real network/model. They assert the runtime is
deny-by-default and that failures are classified (not mistaken for hypothesis disproof).
"""

from __future__ import annotations

import base64
import json

import pytest

from ctf_agent.adapters.base import AdapterRegistry, UnknownToolError
from ctf_agent.adapters.file_adapter import FileAdapter
from ctf_agent.adapters.http_adapter import HttpAdapter, HttpPolicy
from ctf_agent.adapters.subprocess_adapter import SubprocessAdapter, SubprocessCommand
from ctf_agent.classifier import classify_result
from ctf_agent.models import (
    Action,
    EnvironmentState,
    ExecutionResult,
    RelevantState,
    ResultClass,
)

from ctf_runtime.llm_client import ScriptedLLMClient
from ctf_runtime.real_environment import (
    AllowedExecutable,
    OperatorPolicy,
    build_operator_environment,
    build_operator_gateway,
)

_STATE = RelevantState(
    environment=EnvironmentState(revision="r1", available_tools=(), network_available=True),
    authentication_context="none", session_context="s", challenge_revision="r1",
)


def _action(tool, target="", input_data=None, params=None):
    return Action(
        action_id="a1", objective="test", tool=tool, target=target, input_data=input_data,
        relevant_parameters=params or {}, prerequisites=(), state_before=_STATE,
    )


# --- 1 & 4 & 12: file read is confined to allowed_root; traversal/absolute rejected -----------

def test_file_adapter_confined_to_root(tmp_path):
    (tmp_path / "flag.txt").write_text("CTF{real_file}")
    secret = tmp_path.parent / "outside_secret.txt"
    secret.write_text("SHOULD_NOT_BE_READABLE")
    fa = FileAdapter("read_file", tmp_path)

    ok = fa.execute(_action("read_file", input_data="flag.txt"))
    assert ok.exit_code == 0 and "CTF{real_file}" in ok.stdout

    trav = fa.execute(_action("read_file", input_data="../outside_secret.txt"))
    assert trav.tool_available is False and "escapes" in trav.metadata.get("reason", "")

    absolute = fa.execute(_action("read_file", input_data=str(secret)))
    assert absolute.tool_available is False  # absolute path resolves outside the root


# --- 3: unauthorized network target refused before any I/O ------------------------------------

def test_http_adapter_rejects_unauthorized_target():
    ha = HttpAdapter("http_probe", HttpPolicy(allowed_host_prefixes=("https://target.example",)))
    res = ha.execute(_action("http_probe", target="https://evil.example/steal"))
    assert res.network_state == "unreachable"
    assert res.metadata.get("reason") == "target not in allowed_host_prefixes"
    # cloud metadata endpoint is likewise not on the allow-list -> refused
    meta = ha.execute(_action("http_probe", target="http://169.254.169.254/latest/meta-data/"))
    assert meta.network_state == "unreachable"


# --- 5 & 1: process adapter is one fixed executable; no execute_anything ----------------------

def test_subprocess_adapter_is_fixed_executable():
    ad = SubprocessAdapter("run_python", SubprocessCommand("this_exe_does_not_exist_xyz"))
    # wrong tool name cannot be executed by this adapter
    with pytest.raises(ValueError):
        ad.execute(_action("execute_pwsh", input_data="whoami"))
    # a non-existent (unregistered on PATH) executable is reported unavailable, never guessed
    res = ad.execute(_action("run_python", input_data=["-c", "print(1)"]))
    assert res.tool_available is False


# --- 4 & 6: registry is deny-by-default; unknown/arbitrary tool rejected ----------------------

def test_registry_rejects_unregistered_tool():
    from pathlib import Path
    reg = AdapterRegistry()
    reg.register(FileAdapter("read_file", Path(".")))
    assert reg.is_registered("read_file")
    with pytest.raises(UnknownToolError):
        reg.execute(_action("execute_pwsh", input_data="whoami"))
    with pytest.raises(UnknownToolError):
        reg.execute(_action("curl", target="http://x"))


# --- 5: operator environment is deny-by-default and composes only what is authorized ----------

def test_operator_environment_deny_by_default(tmp_path):
    # empty policy: no http, no executables, only read_file (default on), no verifier
    env = build_operator_environment(OperatorPolicy(allowed_host_prefixes=(), allowed_executables=()),
                                     tmp_path / "ws1")
    names = {t.name for t in env.permitted_tools}
    assert names == {"read_file"}
    assert env.verifier_route is None  # no verifier => VERIFIED_FLAG impossible

    # authorized policy: file + http + one executable
    policy = OperatorPolicy(
        allowed_host_prefixes=("https://target.example",),
        allowed_executables=(AllowedExecutable("run_python", "python", ("-c",)),),
    )
    env2 = build_operator_environment(policy, tmp_path / "ws2")
    names2 = {t.name for t in env2.permitted_tools}
    assert names2 == {"read_file", "http_probe", "run_python"}
    assert "execute_pwsh" not in names2 and "execute_anything" not in names2


# --- 7 & 11: failures classified correctly (not hypothesis disproof) --------------------------

def test_failures_are_classified_not_disproof():
    assert classify_result(ExecutionResult("a", "t", timed_out=True)).result_class is ResultClass.TIMEOUT
    assert classify_result(ExecutionResult("a", "t", http_status=429)).result_class is ResultClass.RATE_LIMIT
    assert classify_result(ExecutionResult("a", "t", http_status=403)).result_class is ResultClass.AUTHZ_FAILURE
    assert classify_result(ExecutionResult("a", "t", tool_available=False)).result_class is ResultClass.TOOL_FAILURE
    assert classify_result(ExecutionResult("a", "t", network_state="unreachable")).result_class is ResultClass.NETWORK_FAILURE
    # none of these are a SUCCESS/authoritative result -> cannot verify a flag off them
    for rc in (ResultClass.TIMEOUT, ResultClass.RATE_LIMIT, ResultClass.AUTHZ_FAILURE,
               ResultClass.TOOL_FAILURE, ResultClass.NETWORK_FAILURE):
        assert rc not in (ResultClass.SUCCESS,)


# --- 9: fake flag is not verified when there is no authoritative verifier ---------------------

def _guess_script(_request):
    return json.dumps({
        "hypotheses": [{"id": "h1", "statement": "guess", "mechanism": "ssti",
                        "technique": "Server-Side Template Injection"}],
        "actions": [{"hypothesis_id": "h1", "objective": "submit guess", "tool": "read_file",
                     "target": "", "candidate_flag": "CTF{made_up}"}],
    })


def test_fake_flag_not_verified_without_verifier(tmp_path):
    policy = OperatorPolicy(allowed_executables=(), allowed_host_prefixes=())  # no verifier
    gw = build_operator_gateway(policy, ScriptedLLMClient(_guess_script),
                                workspace_base=tmp_path / "fake")
    sid = gw.ctf_start({"name": "c", "category": "web", "description": "d", "flag_format": "CTF{...}"})["session_id"]
    gw.ctf_run(sid, max_steps=3)
    res = gw.ctf_result(sid)
    assert res["verified"] is False
    assert res["verified_flag"] is None
    assert res["result_type"] != "VERIFIED_FLAG"


# --- 10: budget exhaustion is a clean terminal state (not DISPROVEN/UNSOLVABLE) ---------------

def _noop_script(_request):
    return json.dumps({"hypotheses": [{"id": "h1", "statement": "x"}], "actions": []})


def test_budget_exhaustion_clean_terminal(tmp_path):
    from ctf_agent.autonomy.contracts import SolveConstraints
    policy = OperatorPolicy(constraints=SolveConstraints(max_actions=2, max_iterations=2, timeout_seconds=600.0))
    gw = build_operator_gateway(policy, ScriptedLLMClient(_noop_script), workspace_base=tmp_path / "budget")
    sid = gw.ctf_start({"name": "c", "category": "web", "description": "d"})["session_id"]
    out = gw.ctf_run(sid)
    assert out["status"] in ("BLOCKED", "EXHAUSTED", "FAILED")   # a defined terminal, never a flag
    assert out["verified_flag"] is None


# --- 11 (isolation): two sessions are independent ---------------------------------------------

def test_session_isolation_real_gateway(tmp_path):
    policy = OperatorPolicy()
    gw = build_operator_gateway(policy, ScriptedLLMClient(_noop_script), workspace_base=tmp_path / "iso")
    a = gw.ctf_start({"name": "A", "category": "web", "description": "d"})["session_id"]
    b = gw.ctf_start({"name": "B", "category": "web", "description": "d"})["session_id"]
    assert a != b
    assert gw.ctf_state(a)["run_id"] != gw.ctf_state(b)["run_id"]
    assert gw.ctf_evidence(a)["session_id"] == a and gw.ctf_evidence(b)["session_id"] == b


# --- 2 & 12: challenge resource cannot escape its resource boundary ---------------------------

def test_resource_boundary_rejects_traversal_at_gateway(tmp_path):
    policy = OperatorPolicy()
    gw = build_operator_gateway(policy, ScriptedLLMClient(_noop_script), workspace_base=tmp_path / "resb")
    content = base64.b64encode(b"data").decode()
    with pytest.raises(Exception):
        gw.ctf_start({"name": "c", "resources": [
            {"resource_id": "r", "kind": "FILE", "filename": "../escape.txt", "content_b64": content}
        ]})


# --- REAL adapter path: a real FileAdapter read + real verifier verify through the pipeline ----

def test_real_file_adapter_pipeline_verifies(tmp_path):
    """End-to-end with a REAL disk adapter (not the fake demo probe): a real FileAdapter reads a
    materialized resource, produces real evidence, and a real deterministic verifier confirms the
    candidate the reasoning observed. Reasoning is scripted (no real LLM); the flag is read from the
    file, not injected into the submission."""
    import hashlib
    from ctf_agent.autonomy.contracts import EvidenceRule, SolveConstraints
    from ctf_agent.models import Action, ExecutionResult

    flag = "CTF{" + hashlib.sha256(b"pytest-file-pilot").hexdigest()[:16] + "}"

    class Verifier:
        name = "flag_verifier"
        def execute(self, action):
            cand = (action.input_data or {}).get("flag", "") if isinstance(action.input_data, dict) else str(action.input_data or "")
            exp = "CTF{" + hashlib.sha256(b"pytest-file-pilot").hexdigest()[:16] + "}"
            return ExecutionResult(action.action_id, action.tool, exit_code=0,
                metadata={"submitted_candidate": cand, "verifier_accepted": cand == exp,
                          "rejection_reason": "" if cand == exp else "wrong"})

    rel = "resources/notes/notes.txt"

    def script(request):
        import re
        acts = [{"hypothesis_id": "flag-in-file", "objective": "read the file", "tool": "read_file",
                 "target": rel, "input_data": rel}]
        seen = re.search(r"CTF\{[0-9a-f]+\}", request.prompt)
        if seen:
            acts.append({"hypothesis_id": "flag-in-file", "objective": "submit observed flag",
                         "tool": "flag_verifier", "target": "operator-grader",
                         "candidate_flag": seen.group(0)})
        return json.dumps({"hypotheses": [{"id": "flag-in-file", "statement": "file has the flag",
                                           "mechanism": "file-read", "technique": "artifact inspection"}],
                           "actions": acts})

    policy = OperatorPolicy(
        verifier_tool_name="flag_verifier", verifier_target="operator-grader", verifier_adapter=Verifier(),
        evidence_rules=(EvidenceRule("flag-in-file", supporting_body_contains=(flag,),
                                     authoritative_sources=(rel,)),),
        authoritative_sources_by_tool={"read_file": (rel,)},
        constraints=SolveConstraints(max_actions=6, max_iterations=6, timeout_seconds=600.0),
    )
    gw = build_operator_gateway(policy, ScriptedLLMClient(script), workspace_base=tmp_path / "rp")
    resource_b64 = base64.b64encode(f"notes\nflag: {flag}\n".encode()).decode()
    sid = gw.ctf_start({"name": "file-pilot", "category": "forensics", "description": "recover flag",
                        "flag_format": "CTF{...}",
                        "resources": [{"resource_id": "notes", "kind": "FILE", "filename": "notes.txt",
                                       "content_b64": resource_b64}]})["session_id"]
    run = gw.ctf_run(sid)
    assert run["status"] == "SOLVED" and run["verified_flag"] == flag
    res = gw.ctf_result(sid)
    assert res["result_type"] == "VERIFIED_FLAG" and res["verified"] is True
    adapters = {r["execution_adapter"] for r in gw.session_journal(sid)}
    assert "read_file" in adapters and "flag_verifier" in adapters   # REAL adapters executed
