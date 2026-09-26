"""InteractiveTcpAdapter tests (checklist items 1-25).

Adapter-level tests use deterministic fake sockets (timeout/refused/bounded) and a real localhost
server (round-trip). A couple of items are validated at the frozen boundary (proposal validator)
and via the gateway kiro path (planner dedup). The adapter never bypasses TrustKernel/planner and
never manufactures verification.
"""

from __future__ import annotations

import socket
import socketserver
import threading

import pytest

from ctf_agent.adapters import AdapterRegistry
from ctf_agent.classifier import classify_result
from ctf_agent.models import Action, EnvironmentState, RelevantState, ResultClass
from ctf_agent.proposals import ActionSuggestion, ProposalRejected, validate_action_suggestion

from ctf_runtime.tcp_adapter import (
    InteractiveTcpAdapter,
    ServiceTranscriptVerifier,
    TcpDestination,
)

_STATE = RelevantState(EnvironmentState("r"), "", "", "r")


def _act(op, *, target="svc", data=None, params=None, tool="tcp"):
    p = {"op": op}
    p.update(params or {})
    return Action(f"a-{op}", "obj", tool, target, data, p, (), _STATE)


# ---- fake sockets (deterministic) --------------------------------------------------------------
class _TimeoutSock:
    def settimeout(self, t): pass
    def connect(self, addr): raise socket.timeout()
    def close(self): pass


class _RefusedSock:
    def settimeout(self, t): pass
    def connect(self, addr): raise ConnectionRefusedError()
    def close(self): pass


class _FakeConn:
    """A connected socket that yields ``to_send`` on recv (then times out) and records sent bytes."""
    def __init__(self, to_send=b""):
        self._buf = bytearray(to_send)
        self.sent = bytearray()
        self.connected = False
    def settimeout(self, t): pass
    def connect(self, addr): self.connected = True
    def sendall(self, d): self.sent += d
    def recv(self, n):
        if not self._buf:
            raise socket.timeout()
        chunk = bytes(self._buf[:n]); del self._buf[:n]; return chunk
    def close(self): pass


def _adapter(dest, *, socket_factory=None, clock=None):
    kw = {}
    if socket_factory is not None:
        kw["socket_factory"] = socket_factory
    if clock is not None:
        kw["clock"] = clock
    return InteractiveTcpAdapter("tcp", (dest,), **kw)


def _dest(**ov):
    base = dict(name="svc", host="127.0.0.1", port=9999)
    base.update(ov)
    return TcpDestination(**base)


# ---- real localhost server ---------------------------------------------------------------------
def _serve(handler_fn):
    class H(socketserver.StreamRequestHandler):
        wbufsize = 0
        def handle(self):
            handler_fn(self)
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


# =========================================================================================
# 1-3: registration
# =========================================================================================

def test_1_registered_host_port_succeeds():
    def handler(h):
        h.wfile.write(b"BANNER\n")
    srv = _serve(handler)
    host, port = srv.server_address
    ad = _adapter(_dest(host=host, port=port, read_timeout=0.4))
    r = ad.execute(_act("connect"))
    assert r.exit_code == 0 and "BANNER" in r.stdout
    assert classify_result(r).result_class is ResultClass.SUCCESS
    ad.execute(_act("close")); srv.shutdown()


def test_2_unregistered_host_rejected():
    called = {"n": 0}
    def factory():
        called["n"] += 1
        return _FakeConn()
    ad = _adapter(_dest(), socket_factory=factory)
    r = ad.execute(_act("connect", target="evil.example.com:1337"))
    assert r.tool_available is False
    assert called["n"] == 0                               # NO socket created for unregistered dest
    assert classify_result(r).result_class is ResultClass.TOOL_FAILURE


def test_3_wrong_port_rejected():
    ad = _adapter(_dest(host="127.0.0.1", port=5000), socket_factory=lambda: _FakeConn())
    r = ad.execute(_act("connect", target="127.0.0.1:6000"))   # right host, wrong port
    assert r.tool_available is False


# =========================================================================================
# 4-9: bounded network safety
# =========================================================================================

def test_4_connect_timeout():
    ad = _adapter(_dest(connect_timeout=0.1), socket_factory=_TimeoutSock)
    r = ad.execute(_act("connect"))
    assert r.timed_out is True
    assert classify_result(r).result_class is ResultClass.TIMEOUT


def test_5_read_timeout_returns_bounded_response():
    # server sends nothing; recv times out cleanly (empty response, not a crash)
    ad = _adapter(_dest(read_timeout=0.2), socket_factory=lambda: _FakeConn(to_send=b""))
    r = ad.execute(_act("connect"))
    assert r.exit_code == 0 and r.stdout == ""            # quiet peer -> empty, bounded


def test_6_send_size_limit():
    ad = _adapter(_dest(max_send_bytes=4), socket_factory=lambda: _FakeConn(b"hi"))
    ad.execute(_act("connect"))
    r = ad.execute(_act("send", data="toolongpayload"))
    assert r.input_rejected is True
    assert classify_result(r).result_class is ResultClass.INPUT_REJECTION


def test_7_receive_size_limit_truncates():
    ad = _adapter(_dest(max_recv_bytes=8, read_timeout=0.2),
                  socket_factory=lambda: _FakeConn(b"0123456789ABCDEF"))
    r = ad.execute(_act("connect"))
    assert r.metadata["received_bytes"] == 8 and r.metadata["truncated"] is True


def test_8_turn_limit():
    ad = _adapter(_dest(max_turns=1), socket_factory=lambda: _FakeConn(b"x"))
    ad.execute(_act("connect"))
    assert ad.execute(_act("send", data="a")).input_rejected in (False, None)  # turn 1 ok
    r = ad.execute(_act("send", data="b"))
    assert r.input_rejected is True and "turn budget" in r.metadata["reason"]


def test_9_session_lifetime_and_connection_budget():
    clock = {"t": 0.0}
    ad = _adapter(_dest(max_session_seconds=5.0, max_connections=1),
                  socket_factory=lambda: _FakeConn(b"x"), clock=lambda: clock["t"])
    ad.execute(_act("connect"))
    clock["t"] = 100.0                                    # advance past lifetime
    r = ad.execute(_act("send", data="a"))
    assert r.input_rejected is True and "lifetime" in r.metadata["reason"]
    # connection budget: after the lifetime close, a reconnect exceeds max_connections=1
    r2 = ad.execute(_act("connect"))
    assert r2.input_rejected is True and "connection budget" in r2.metadata["reason"]


# =========================================================================================
# 10-12: session model + binary
# =========================================================================================

def test_10_session_isolation():
    a1 = _adapter(_dest(), socket_factory=lambda: _FakeConn(b"flag{one}"))
    a2 = _adapter(_dest(), socket_factory=lambda: _FakeConn(b"flag{two}"))
    a1.execute(_act("connect"))
    assert a1.service_emitted("flag{one}") and not a2.service_emitted("flag{one}")


def test_11_explicit_close():
    ad = _adapter(_dest(), socket_factory=lambda: _FakeConn(b"x"))
    ad.execute(_act("connect"))
    c = ad.execute(_act("close"))
    assert c.metadata["closed"] is True
    r = ad.execute(_act("send", data="a"))
    assert r.input_rejected is True and "no open connection" in r.metadata["reason"]


def test_12_binary_data_round_trip():
    fake = _FakeConn(bytes([0x00, 0xFF, 0x80, 0x7F]))
    ad = _adapter(_dest(read_timeout=0.2), socket_factory=lambda: fake)
    r = ad.execute(_act("connect"))
    assert r.metadata["received_hex"] == "00ff807f"       # non-utf8 preserved as hex
    ad.execute(_act("send", data="deadbeef", params={"encoding": "hex"}))
    assert fake.sent == bytes.fromhex("deadbeef")         # hex payload sent as raw bytes


# =========================================================================================
# 13-14: malformed / duplicate
# =========================================================================================

def test_13_malformed_request_rejected():
    ad = _adapter(_dest(), socket_factory=lambda: _FakeConn(b"x"))
    assert ad.execute(_act("frobnicate")).input_rejected is True     # unknown op
    ad.execute(_act("connect"))
    r = ad.execute(_act("send", data="nothex!!", params={"encoding": "hex"}))
    assert r.input_rejected is True and "invalid hex" in r.metadata["reason"]


def test_14_duplicate_action_handling_is_the_planners_job(tmp_path):
    # planner dedup: an identical tcp action proposed twice executes at most once
    from ctf_runtime.mcp_gateway import CtfAgentGateway
    from ctf_runtime.real_environment import OperatorPolicy, build_operator_environment
    from ctf_runtime.llm_client import ScriptedLLMClient

    def handler(h):
        h.wfile.write(b"HELLO\n")
        try:
            h.rfile.readline()
        except Exception:
            pass
    srv = _serve(handler)
    host, port = srv.server_address
    policy = OperatorPolicy(enable_file_read=False,
                            tcp_destinations=(TcpDestination("svc", host, port, read_timeout=0.3),))
    gw = CtfAgentGateway(
        environment_factory=lambda meta: build_operator_environment(policy, tmp_path / "s"),
        llm_client=ScriptedLLMClient(lambda r: "{}"), constraints=policy.constraints,
        journal_dir=tmp_path / "j", audit_log_path=tmp_path / "a.jsonl",
    )
    sid = gw.ctf_start({"name": "svc", "category": "misc", "description": "d",
                        "urls": [], "driver": "kiro"})["session_id"]
    act = [{"hypothesis_id": "h", "objective": "connect", "tool": "tcp", "target": "svc",
            "relevant_parameters": {"op": "connect"}}]
    gw.ctf_propose(sid, hypotheses=[{"hypothesis_id": "h", "statement": "svc"}], actions=act)
    r2 = gw.ctf_propose(sid, hypotheses=[], actions=act)     # identical, unchanged state
    assert r2["executed"] == []                              # deduped by the planner, not the adapter
    srv.shutdown()


# =========================================================================================
# 15-18: authority boundaries
# =========================================================================================

def test_15_trustkernel_authorization_required_unregistered_tool_rejected():
    # a tcp action naming a tool that is NOT registered is rejected by the frozen validator
    registry = AdapterRegistry()
    sug = ActionSuggestion(hypothesis_id="h", objective="connect", tool="tcp", target="svc")
    with pytest.raises(ProposalRejected):
        validate_action_suggestion(sug, registry)          # tcp not registered -> rejected


def test_16_planner_authorization_registered_tool_accepted():
    class _Stub:
        name = "tcp"
        def execute(self, a): raise AssertionError("not executed by the validator")
    registry = AdapterRegistry(); registry.register(_Stub())
    sug = ActionSuggestion(hypothesis_id="h", objective="connect", tool="tcp", target="svc")
    assert validate_action_suggestion(sug, registry) is sug   # accepted for planning


def test_17_direct_invocation_cannot_bypass_destination_policy():
    # even calling the adapter directly, an unregistered destination is refused (no socket opened)
    opened = {"n": 0}
    def factory():
        opened["n"] += 1
        return _FakeConn()
    ad = _adapter(_dest(), socket_factory=factory)
    r = ad.execute(_act("connect", target="10.0.0.1:22"))
    assert r.tool_available is False and opened["n"] == 0


def test_18_arbitrary_internet_destination_rejected():
    opened = {"n": 0}
    ad = _adapter(_dest(host="127.0.0.1", port=9), socket_factory=lambda: (_ for _ in ()).throw(
        AssertionError("must not connect")))
    for target in ("attacker.com:443", "8.8.8.8:53", "169.254.169.254:80"):
        assert ad.execute(_act("connect", target=target)).tool_available is False


# =========================================================================================
# 19-21: no UDP / no scan / no discovery
# =========================================================================================

def test_19_no_udp():
    from ctf_runtime.tcp_adapter import _default_socket_factory
    s = _default_socket_factory()
    try:
        assert s.type == socket.SOCK_STREAM              # TCP only; never SOCK_DGRAM
    finally:
        s.close()


def test_20_no_port_scanning_only_registered():
    ad = _adapter(_dest(host="127.0.0.1", port=1234), socket_factory=lambda: _FakeConn(b"x"))
    for port in (1, 22, 80, 443, 8080):
        assert ad.execute(_act("connect", target=f"127.0.0.1:{port}")).tool_available is False


def test_21_no_host_discovery_surface():
    ad = _adapter(_dest(), socket_factory=lambda: _FakeConn(b"x"))
    for attr in ("scan", "discover", "enumerate", "sweep", "probe_range"):
        assert not hasattr(ad, attr)


# =========================================================================================
# 22-23: verification cannot be self-created / historical flag cannot verify
# =========================================================================================

def test_22_verifier_cannot_self_create_verification():
    ad = _adapter(_dest(), socket_factory=lambda: _FakeConn(b"no flag here"))
    ad.execute(_act("connect"))
    v = ServiceTranscriptVerifier("flag_verifier", ad)
    r = v.execute(Action("v", "o", "flag_verifier", "g", {"flag": "CTF{anything}"}, {}, (), _STATE))
    assert r.metadata["verifier_accepted"] is False       # service never emitted it


def test_23_historical_flag_cannot_become_current():
    ad = _adapter(_dest(read_timeout=0.2), socket_factory=lambda: _FakeConn(b"CTF{real_from_service}\n"))
    ad.execute(_act("connect"))
    v = ServiceTranscriptVerifier("flag_verifier", ad)
    good = v.execute(Action("v", "o", "flag_verifier", "g", {"flag": "CTF{real_from_service}"}, {}, (), _STATE))
    hist = v.execute(Action("v", "o", "flag_verifier", "g", {"flag": "CTF{historical_from_writeup}"}, {}, (), _STATE))
    assert good.metadata["verifier_accepted"] is True
    assert hist.metadata["verifier_accepted"] is False


# =========================================================================================
# 24-25: failure classification / provisioning vs exploit
# =========================================================================================

def test_24_tcp_failure_classified_correctly():
    refused = _adapter(_dest(), socket_factory=_RefusedSock).execute(_act("connect"))
    assert classify_result(refused).result_class is ResultClass.NETWORK_FAILURE
    timeout = _adapter(_dest(connect_timeout=0.1), socket_factory=_TimeoutSock).execute(_act("connect"))
    assert classify_result(timeout).result_class is ResultClass.TIMEOUT


def test_25_provisioning_failure_distinct_from_exploit_failure():
    # provisioning failure (unregistered dest) -> TOOL_FAILURE
    prov = _adapter(_dest(), socket_factory=lambda: _FakeConn()).execute(
        _act("connect", target="unregistered:1"))
    assert classify_result(prov).result_class is ResultClass.TOOL_FAILURE
    # exploit failure (service responds "rip") is a normal SUCCESS observation, not a tool failure
    ad = _adapter(_dest(read_timeout=0.2), socket_factory=lambda: _FakeConn(b"rip\n"))
    exploit = ad.execute(_act("connect"))
    assert classify_result(exploit).result_class is ResultClass.SUCCESS
    assert "rip" in exploit.stdout
