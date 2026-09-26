"""CRYSig end-to-end reproduction through the Architecture A MCP path (client harness).

Drives the SAME ``CtfAgentGateway`` methods the FastMCP tools wrap, with driver="kiro" (Kiro is the
reasoner). A real local CRYSig TCP service is stood up on 127.0.0.1 with a RANDOM flag the solver
does not know; the solver must genuinely forge a signature to make the service emit it. The forgery
math lives HERE (the reasoner), never in the adapter — the adapter only provides communication.

Flow: ctf_start -> ctf_observe -> ctf_propose(read_file) -> identify GF(2) linearity ->
ctf_propose(tcp connect/send/recv dialogue) -> reasoner computes forgery -> service emits flag ->
ctf_propose(candidate via verifier_route) -> VERIFIED_FLAG -> ctf_writeup -> ctf_experience ->
close_session. All execution flows through validation -> planner -> TrustKernel -> trusted adapter.
"""

from __future__ import annotations

import base64
import json
import os
import re
import socketserver
import threading
from pathlib import Path

from ctf_agent.autonomy.contracts import EvidenceRule, SolveConstraints
from ctf_runtime.llm_client import ScriptedLLMClient
from ctf_runtime.mcp_gateway import CtfAgentGateway
from ctf_runtime.real_environment import OperatorPolicy, build_operator_environment
from ctf_runtime.tcp_adapter import TcpDestination

REPO = Path(__file__).resolve().parents[2]
CHAL = REPO / "chal.py"

USER = b"babyuser"
ROOT = b"chadr00t"
MESSAGE_SIZE = 8
TAG_SIZE = 16


# ---- the REAL challenge service (operator-hosted locally; flag unknown to the solver) ----------
class _CRYSig:
    def __init__(self) -> None:
        self.matrix = [int.from_bytes(os.urandom(MESSAGE_SIZE), "big") for _ in range(TAG_SIZE * 8)]

    def sign(self, message: bytes) -> bytes:
        msg_vector = int.from_bytes(message, "big")
        res = 0
        for row in self.matrix:
            res <<= 1
            res += (row & msg_vector).bit_count() % 2
        return res.to_bytes(TAG_SIZE, "big")

    def verify(self, message: bytes, signature: bytes) -> bool:
        return len(signature) == TAG_SIZE and self.sign(message) == signature


def _make_handler(flag: str):
    class Handler(socketserver.StreamRequestHandler):
        wbufsize = 0

        def handle(self) -> None:
            sig = _CRYSig()
            self.wfile.write(f"user signature: {sig.sign(USER).hex()}\n> ".encode())
            line = self.rfile.readline().strip()
            try:
                query = bytes.fromhex(line.decode())
            except ValueError:
                self.wfile.write(b"bad hex\n")
                return
            if query == ROOT:
                self.wfile.write(b"holy cheating\n")
                return
            self.wfile.write(f"your signature: {sig.sign(query).hex()}\n> ".encode())
            line2 = self.rfile.readline().strip()
            try:
                attempt = bytes.fromhex(line2.decode())
            except ValueError:
                self.wfile.write(b"bad hex\n")
                return
            self.wfile.write((flag + "\n").encode() if sig.verify(ROOT, attempt) else b"rip\n")

    return Handler


def _start_service(flag: str):
    server = socketserver.ThreadingTCPServer(("127.0.0.1", 0), _make_handler(flag))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, server.server_address


# ---- reasoner helpers (exploit math lives in the reasoner, not the adapter) --------------------
def _xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def _hex_after(text: str, label: str) -> str:
    m = re.search(label + r":\s*([0-9a-fA-F]+)", text)
    return m.group(1) if m else ""


def _observed(gw, sid) -> str:
    return " ".join(o.get("output", "") for o in gw.ctf_observe(sid).get("recent_observations", []))


def main() -> None:
    flag = "CTF{" + os.urandom(8).hex() + "}"          # random; the solver never sees it up front
    server, (host, port) = _start_service(flag)
    work = REPO / ".agent" / "_crysig_run"
    work.mkdir(parents=True, exist_ok=True)

    policy = OperatorPolicy(
        enable_file_read=True, file_tool_name="read_file",
        allowed_host_prefixes=(), allowed_executables=(),
        tcp_destinations=(TcpDestination("crysig", host, port, read_timeout=0.5,
                                         max_turns=8, max_session_seconds=30.0),),
        tcp_service_verifier=True, tcp_verifier_tool_name="flag_verifier",
        tcp_verifier_target="service-transcript", tcp_flag_pattern=r"^CTF\{[0-9a-f]+\}$",
        # Operator evidence rule: a forged submission that makes the trusted service emit a flag
        # SUPPORTS the linear-forgery hypothesis; a "rip" response CONTRADICTS it. Authoritative
        # source is the registered TCP destination. (The flag value stays unknown to the solver.)
        evidence_rules=(EvidenceRule("crypto-linear-forgery",
                                     supporting_body_contains=("CTF{",),
                                     contradicting_body_contains=("rip",),
                                     authoritative_sources=("crysig",)),),
        constraints=SolveConstraints(max_actions=10, max_iterations=10, max_tool_executions=10,
                                     max_network_actions=8, max_remote_attempts=8, max_submissions=2,
                                     max_specialist_calls=12, max_total_cost=25, timeout_seconds=60.0),
    )
    counter = {"n": 0}

    def factory(meta):
        counter["n"] += 1
        return build_operator_environment(policy, work / f"session_{counter['n']}")

    gw = CtfAgentGateway(
        environment_factory=factory, llm_client=ScriptedLLMClient(lambda r: "{}"),
        constraints=policy.constraints, journal_dir=work / "journals",
        audit_log_path=work / "audit.jsonl", learning_root=work / "agent_experience_v1",
    )

    challenge = {
        "name": "CRYSig", "category": "crypto",
        "description": "A CRYSig signing service. Forge a signature for 'chadr00t' to read the flag.",
        "flag_format": "CTF{...}", "urls": [],
        "resources": [{"resource_id": "src", "kind": "SOURCE", "filename": "chal.py",
                       "content_b64": base64.b64encode(CHAL.read_bytes()).decode()}],
        "driver": "kiro",
    }
    sid = gw.ctf_start(challenge)["session_id"]
    print("ctf_start:", sid, "tools:", gw.ctf_observe(sid)["available_tools"])

    # 1) inspect source (grounded evidence) + state the mechanism hypothesis
    gw.ctf_propose(sid,
        hypotheses=[{"hypothesis_id": "crypto-linear-forgery",
                     "statement": "CRYSig tag is GF(2)-linear: sign(root)=sign(user) XOR sign(user XOR root)",
                     "mechanism": "linear signature forgery over GF(2)", "technique": "homomorphic forgery"}],
        actions=[{"hypothesis_id": "crypto-linear-forgery", "objective": "inspect challenge source",
                  "tool": "read_file", "target": "resources/src/chal.py",
                  "input_data": "resources/src/chal.py"}])
    src_ok = "CRYSig" in _observed(gw, sid)
    print("read_file source_ok:", src_ok)

    # 2) connect to the live service -> receive the user signature
    gw.ctf_propose(sid, hypotheses=[],
        actions=[{"hypothesis_id": "crypto-linear-forgery", "objective": "connect to CRYSig service",
                  "tool": "tcp", "target": "crysig", "relevant_parameters": {"op": "connect"}}])
    banner = _observed(gw, sid)
    user_sig_hex = _hex_after(banner, "user signature")
    print("connect: user_sig:", user_sig_hex[:16], "...")

    # 3) reasoner computes the oracle query = user XOR root, submits it, receives its signature
    query = _xor(USER, ROOT)
    gw.ctf_propose(sid, hypotheses=[],
        actions=[{"hypothesis_id": "crypto-linear-forgery",
                  "objective": "query oracle signature for user XOR root", "tool": "tcp",
                  "target": "crysig", "input_data": query.hex(),
                  "relevant_parameters": {"op": "send", "newline": True}}])
    resp2 = _observed(gw, sid)
    query_sig_hex = _hex_after(resp2, "your signature")
    print("query: query_sig:", query_sig_hex[:16], "...")

    # 4) reasoner constructs the forgery = user_sig XOR query_sig = sign(root); submits it
    forgery = _xor(bytes.fromhex(user_sig_hex), bytes.fromhex(query_sig_hex))
    gw.ctf_propose(sid, hypotheses=[],
        actions=[{"hypothesis_id": "crypto-linear-forgery", "objective": "submit forged root signature",
                  "tool": "tcp", "target": "crysig", "input_data": forgery.hex(),
                  "relevant_parameters": {"op": "send", "newline": True}}])
    resp3 = _observed(gw, sid)
    m = re.search(r"CTF\{[0-9a-f]+\}", resp3)
    observed_flag = m.group(0) if m else ""
    print("forgery submitted; service emitted flag:", bool(observed_flag))

    # 5) submit the OBSERVED flag through the authoritative verifier route (service-transcript)
    verified = False
    if observed_flag:
        r = gw.ctf_propose(sid, hypotheses=[],
            actions=[{"hypothesis_id": "crypto-linear-forgery", "objective": "verify flag with the service verifier",
                      "tool": "flag_verifier", "target": "service-transcript",
                      "candidate_flag": observed_flag}])
        verified = bool(r.get("verified"))

    result = gw.ctf_result(sid)
    print("ctf_result:", json.dumps(result))
    writeup = gw.get_writeup(sid)
    print("ctf_writeup available:", writeup["available"], "grounded:", writeup.get("grounded"),
          "flag:", writeup.get("flag"))
    gw.close_session(sid)
    experience = gw.get_experience(sid)
    print("ctf_experience learned:", experience["learned"], "source_kind:", experience.get("source_kind"))
    journal = gw.session_journal(sid)
    adapters = sorted({j.get("execution_adapter") for j in journal if j.get("execution_adapter")})
    print("adapters_used:", adapters)
    print("FLAG MATCHES SERVICE SECRET:", result.get("verified_flag") == flag)
    print("RESULT:", "VERIFIED_FLAG" if result["result_type"] == "VERIFIED_FLAG" else result["result_type"])
    server.shutdown()


if __name__ == "__main__":
    main()
