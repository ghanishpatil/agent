"""First REAL CTF live-solve attempt through the Architecture A MCP path (client harness).

This is a CLIENT of the existing runtime — it drives the SAME ``CtfAgentGateway`` methods that the
FastMCP tools (`ctf_start`/`ctf_observe`/`ctf_propose`/`ctf_result`/`ctf_writeup`/`ctf_experience`/
`close_session`) wrap. It introduces NO execution primitive and does NOT touch the frozen solver.

Operator role (trusted environment): read-only file inspection confined to the session workspace,
NO network allow-list, NO executables, and NO authoritative verifier adapter — because the chosen
real challenge provides no local authoritative oracle (its flag lives behind a remote service).

Kiro role (reasoner): observe -> reason -> propose typed hypotheses/actions. All execution,
classification, evidence, and verification remain owned by the frozen pipeline.

Target: ``chal.py`` (crypto). A GF(2)-linear signature scheme (CRYSig) whose tag is linear in the
message, so sign(root) = sign(user) XOR sign(user XOR root) — a classic linear forgery. BUT the flag
is read from a remote ``/flag`` after interacting with the live service, and no local grader exists.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

from ctf_runtime.llm_client import ScriptedLLMClient
from ctf_runtime.mcp_gateway import CtfAgentGateway
from ctf_runtime.real_environment import OperatorPolicy, build_operator_environment
from ctf_agent.autonomy.contracts import SolveConstraints

REPO = Path(__file__).resolve().parents[2]   # f:\mission-git-hackss\mission-git-hackss
CHAL = REPO / "chal.py"


def build_gateway(work: Path) -> CtfAgentGateway:
    # Operator policy: read-only file inspection only. No http, no exec, NO verifier adapter.
    policy = OperatorPolicy(
        enable_file_read=True,
        file_tool_name="read_file",
        allowed_host_prefixes=(),          # no network
        allowed_executables=(),            # no process execution
        verifier_tool_name="",             # no authoritative oracle available for this challenge
        verifier_adapter=None,
        constraints=SolveConstraints(
            max_actions=6, max_iterations=6, max_tool_executions=6, max_network_actions=0,
            max_remote_attempts=0, max_submissions=1, max_specialist_calls=8, max_total_cost=12,
            timeout_seconds=60.0,
        ),
    )
    counter = {"n": 0}

    def factory(meta):
        counter["n"] += 1
        return build_operator_environment(policy, work / f"session_{counter['n']}")

    return CtfAgentGateway(
        environment_factory=factory,
        llm_client=ScriptedLLMClient(lambda r: "{}"),   # unused on the kiro-driven path
        constraints=policy.constraints,
        journal_dir=work / "journals",
        audit_log_path=work / "audit.jsonl",
        learning_root=work / "agent_experience_v1",
    )


def main() -> None:
    work = REPO / ".agent" / "_live_run"
    work.mkdir(parents=True, exist_ok=True)
    gw = build_gateway(work)

    source_b64 = base64.b64encode(CHAL.read_bytes()).decode()
    challenge = {
        "name": "CRYSig",
        "category": "crypto",
        "description": ("A signing service (chal.py). It prints sign('babyuser'), lets you query one "
                        "message's signature, then asks you to produce a valid signature for "
                        "'chadr00t' (root) to read /flag."),
        "flag_format": "",
        "urls": [],
        "resources": [{"resource_id": "src", "kind": "SOURCE", "filename": "chal.py",
                       "content_b64": source_b64}],
        "driver": "kiro",
    }

    started = gw.ctf_start(challenge)
    sid = started["session_id"]
    print("STEP ctf_start:", json.dumps({"session_id": sid, "status": started["status"],
                                          "driver": started["driver"]}))
    print("available_tools:", started["initial_state"].get("available_tools"))

    # --- Kiro reasoning turn 1: inspect the provided source as a grounded discriminating action ---
    obs1 = gw.ctf_observe(sid)
    print("STEP ctf_observe#1 verified:", obs1["verified"], "tools:", obs1["available_tools"])

    r1 = gw.ctf_propose(
        sid,
        hypotheses=[{
            "hypothesis_id": "crypto-linear-forgery",
            "statement": "CRYSig's tag is GF(2)-linear in the message, so sign(root) can be forged "
                         "as sign(user) XOR sign(user XOR root) using one oracle query",
            "mechanism": "linear signature forgery over GF(2)",
            "technique": "linearity / homomorphic forgery",
        }],
        actions=[{
            "hypothesis_id": "crypto-linear-forgery",
            "objective": "inspect the provided challenge source to confirm the signing scheme",
            "tool": "read_file",
            "target": "resources/src/chal.py",
            "input_data": "resources/src/chal.py",
        }],
    )
    print("STEP ctf_propose#1 accepted:", r1["accepted"], "executed:", len(r1["executed"]),
          "rejected:", r1["rejected"])
    for e in r1["executed"]:
        print("  executed:", e["tool"], "->", e["observation_class"], "impact:", e["impact"])

    obs2 = gw.ctf_observe(sid)
    body = " ".join(o.get("output", "") for o in obs2.get("recent_observations", []))
    print("STEP ctf_observe#2 source_read_ok:", "CRYSig" in body, "verified:", obs2["verified"])

    # --- Kiro reasoning turn 2: the exploit REQUIRES the live service (query oracle + submit) and a
    #     remote /flag grader. No such trusted adapter/verifier is provisioned. There is nothing more
    #     that can be legitimately executed toward a verified flag. Do NOT fabricate a flag. ---
    result = gw.ctf_result(sid)
    print("STEP ctf_result:", json.dumps(result))

    # No verified flag => no writeup (writeup is SOLVED-only). For the kiro driver the post-terminal
    # failure experience is emitted AT close_session (a kiro session has no single terminal call).
    writeup = gw.get_writeup(sid)
    print("STEP ctf_writeup available:", writeup["available"])

    closed = gw.close_session(sid)
    print("STEP close_session:", json.dumps(closed))

    experience = gw.get_experience(sid)
    print("STEP ctf_experience learned:", experience["learned"], "source_kind:",
          experience.get("source_kind"), "record_id:", experience.get("record_id"),
          "error:", experience.get("error"))
    if experience.get("record"):
        rec = experience["record"]
        print("  experience.mechanism:", rec.get("mechanism"))
        print("  experience.failure_classes:", rec.get("failure_classes"))
        print("  experience.unresolved:", rec.get("unresolved"))
        print("  experience.disproven:", rec.get("disproven"))
        print("  experience.terminal_reason:", rec.get("terminal_reason"))

    # trace summary for the report
    journal = gw.session_journal(sid)
    adapters_used = sorted({j.get("execution_adapter") for j in journal if j.get("execution_adapter")})
    print("TRACE adapters_used:", adapters_used)
    print("TRACE result_type:", result["result_type"], "verified:", result["verified"])


if __name__ == "__main__":
    main()
