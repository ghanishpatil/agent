"""Operator-registered interactive TCP adapter (trusted, bounded, additive).

This adds ONE reusable trusted capability so interactive raw-TCP CTF services (crypto/pwn/network)
can be driven through the EXISTING pipeline. It is a normal trusted adapter: it implements the same
duck-typed ``.name`` / ``.execute(action) -> ExecutionResult`` contract as the frozen
``FileAdapter`` / ``HttpAdapter`` / ``SubprocessAdapter``, and is composed into an
``EnvironmentConfig`` by :func:`ctf_runtime.real_environment.build_operator_environment`. Nothing in
``ctf_agent`` is imported-for-write or modified.

Trust properties (all preserved):

* **No raw socket is exposed to the model.** Kiro only proposes typed actions
  (``tool="tcp"``, ``relevant_parameters={"op": ...}``). Execution happens only after the frozen
  proposal validation -> ActionPlanner -> TrustKernel accept the action.
* **Registered destinations only.** A proposal whose target is not an operator-registered
  destination is refused before any socket is created. There is no allow-all mode, no host
  discovery, no port scanning, no UDP, no raw packets.
* **Bounded.** Per-destination connect/read timeouts, max send/recv sizes, max dialogue turns, max
  concurrent connections, and a max total session duration are all enforced.
* **Session-scoped state.** A fresh adapter instance is built per CTF session, so an open
  connection from one session cannot leak into another.
* **Advisory verification only.** The adapter NEVER manufactures a candidate/verified flag. An
  optional operator :class:`ServiceTranscriptVerifier` (wired as the frozen ``verifier_route``)
  accepts a candidate only if the trusted service itself emitted it during this session — so a
  historical/writeup flag can never verify.
"""

from __future__ import annotations

import socket
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from ctf_agent.models import Action, ExecutionResult

TCP_TOOL_NAME = "tcp"
_OPS = ("connect", "send", "recv", "close")
_ENCODINGS = ("utf-8", "latin-1", "hex")


@dataclass(frozen=True)
class TcpDestination:
    """One operator-authorized TCP service. Deny-by-default: only these may be reached."""

    name: str
    host: str
    port: int
    connect_timeout: float = 5.0
    read_timeout: float = 3.0
    max_send_bytes: int = 4096
    max_recv_bytes: int = 65_536
    max_turns: int = 32
    max_session_seconds: float = 30.0
    max_connections: int = 1
    expected_identity: str = ""          # optional metadata (advisory only)
    protocol: str = "TCP"                # TCP only; UDP/raw are never supported

    def matches(self, target: str) -> bool:
        return target == self.name or target == f"{self.host}:{self.port}"


class TcpProvisioningError(Exception):
    """Destination not registered / operator did not authorize this target."""


@dataclass
class _Conn:
    sock: object
    opened_at: float
    turns: int = 0


# a socket-like factory so tests can inject deterministic timeout/refused behavior; production uses
# a real AF_INET/SOCK_STREAM (TCP) socket only.
SocketFactory = Callable[[], "socket.socket"]


def _default_socket_factory() -> "socket.socket":
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class InteractiveTcpAdapter:
    """A bounded, stateful TCP dialogue adapter for operator-registered CTF services."""

    def __init__(
        self,
        name: str,
        destinations: Tuple[TcpDestination, ...],
        *,
        socket_factory: Optional[SocketFactory] = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.name = name
        self._destinations: Tuple[TcpDestination, ...] = tuple(destinations)
        self._socket_factory = socket_factory or _default_socket_factory
        self._clock = clock
        self._conns: Dict[str, _Conn] = {}
        self._connect_counts: Dict[str, int] = {}
        self._received: List[bytes] = []     # full session receive transcript (bytes preserved)

    # -- transcript / verification support (read-only) -----------------------------------
    def received_text(self) -> str:
        return b"".join(self._received).decode("latin-1", errors="replace")

    def service_emitted(self, needle: str) -> bool:
        if not needle:
            return False
        return needle in self.received_text()

    # -- adapter contract ----------------------------------------------------------------
    def execute(self, action: Action) -> ExecutionResult:
        if action.tool != self.name:
            raise ValueError(f"InteractiveTcpAdapter '{self.name}' cannot execute tool '{action.tool}'")

        params = dict(action.relevant_parameters or {})
        op = str(params.get("op", "")).lower()
        if op not in _OPS:
            return self._reject(action, f"unknown or missing tcp op {op!r}; allowed: {list(_OPS)}")

        dest = self._resolve(action.target)
        if dest is None:
            # operator-provisioning failure — distinct from any exploit/service failure
            return ExecutionResult(
                action_id=action.action_id, tool=action.tool, tool_available=False,
                metadata={"op": op, "target": action.target,
                          "reason": "destination not registered (operator must authorize host:port)"},
            )

        try:
            if op == "connect":
                return self._connect(action, dest, params)
            if op == "send":
                return self._send(action, dest, params)
            if op == "recv":
                return self._recv_op(action, dest, params)
            return self._close(action, dest)
        except _Bounded as exc:
            return self._reject(action, str(exc), op=op, dest=dest.name)

    # -- ops -----------------------------------------------------------------------------
    def _connect(self, action: Action, dest: TcpDestination, params: dict) -> ExecutionResult:
        if dest.name in self._conns:
            conn = self._conns[dest.name]           # idempotent: reuse the open connection
        else:
            if self._connect_counts.get(dest.name, 0) >= dest.max_connections:
                raise _Bounded(f"connection budget exhausted (max_connections={dest.max_connections})")
            sock = self._socket_factory()
            try:
                sock.settimeout(dest.connect_timeout)
                sock.connect((dest.host, dest.port))
            except (socket.timeout, TimeoutError):
                _safe_close(sock)
                return ExecutionResult(action_id=action.action_id, tool=action.tool, timed_out=True,
                                       metadata={"op": "connect", "dest": dest.name,
                                                 "reason": "connect timeout"})
            except (ConnectionRefusedError, OSError) as exc:
                _safe_close(sock)
                return ExecutionResult(action_id=action.action_id, tool=action.tool,
                                       network_state="connection_refused",
                                       metadata={"op": "connect", "dest": dest.name,
                                                 "reason": f"connection failed: {type(exc).__name__}"})
            conn = _Conn(sock=sock, opened_at=self._clock())
            self._conns[dest.name] = conn
            self._connect_counts[dest.name] = self._connect_counts.get(dest.name, 0) + 1
        received = self._read(conn, dest)
        return self._observation(action, dest, "connect", direction="recv", sent=b"", received=received,
                                 identity_ok=self._identity_ok(dest, received))

    def _send(self, action: Action, dest: TcpDestination, params: dict) -> ExecutionResult:
        conn = self._require_conn(dest)
        self._check_lifetime(conn, dest)
        if conn.turns >= dest.max_turns:
            raise _Bounded(f"turn budget exhausted (max_turns={dest.max_turns})")
        payload = self._encode(action.input_data, params)
        if payload is None:
            return self._reject(action, "send requires input_data (str)", op="send", dest=dest.name)
        if params.get("newline"):
            payload = payload + b"\n"
        if len(payload) > dest.max_send_bytes:
            return ExecutionResult(action_id=action.action_id, tool=action.tool, input_rejected=True,
                                   metadata={"op": "send", "dest": dest.name,
                                             "reason": f"send exceeds max_send_bytes={dest.max_send_bytes}",
                                             "attempted_bytes": len(payload)})
        try:
            conn.sock.sendall(payload)
        except (socket.timeout, TimeoutError):
            return ExecutionResult(action_id=action.action_id, tool=action.tool, timed_out=True,
                                   metadata={"op": "send", "dest": dest.name, "reason": "send timeout"})
        except OSError as exc:
            return ExecutionResult(action_id=action.action_id, tool=action.tool,
                                   network_state="connection_reset",
                                   metadata={"op": "send", "dest": dest.name,
                                             "reason": f"send failed: {type(exc).__name__}"})
        conn.turns += 1
        received = self._read(conn, dest)
        return self._observation(action, dest, "send", direction="send+recv", sent=payload,
                                 received=received, identity_ok=True)

    def _recv_op(self, action: Action, dest: TcpDestination, params: dict) -> ExecutionResult:
        conn = self._require_conn(dest)
        self._check_lifetime(conn, dest)
        received = self._read(conn, dest)
        return self._observation(action, dest, "recv", direction="recv", sent=b"", received=received,
                                 identity_ok=True)

    def _close(self, action: Action, dest: TcpDestination) -> ExecutionResult:
        conn = self._conns.pop(dest.name, None)
        if conn is not None:
            _safe_close(conn.sock)
        return ExecutionResult(
            action_id=action.action_id, tool=action.tool, exit_code=0,
            stdout="", metadata={"op": "close", "dest": dest.name, "closed": conn is not None},
        )

    # -- helpers -------------------------------------------------------------------------
    def _resolve(self, target: str) -> Optional[TcpDestination]:
        for dest in self._destinations:
            if dest.matches(target):
                return dest
        return None

    def _require_conn(self, dest: TcpDestination) -> _Conn:
        conn = self._conns.get(dest.name)
        if conn is None:
            raise _Bounded("no open connection; propose op=connect first")
        return conn

    def _check_lifetime(self, conn: _Conn, dest: TcpDestination) -> None:
        if (self._clock() - conn.opened_at) > dest.max_session_seconds:
            _safe_close(conn.sock)
            self._conns.pop(dest.name, None)
            raise _Bounded(f"session lifetime exceeded (max_session_seconds={dest.max_session_seconds})")

    def _read(self, conn: _Conn, dest: TcpDestination) -> bytes:
        """Read until the peer goes quiet for one read_timeout, EOF, or max_recv_bytes."""
        conn.sock.settimeout(dest.read_timeout)
        chunks: List[bytes] = []
        total = 0
        while total < dest.max_recv_bytes:
            try:
                chunk = conn.sock.recv(min(4096, dest.max_recv_bytes - total))
            except (socket.timeout, TimeoutError):
                break                       # quiet: end of this turn's response
            except OSError:
                break
            if not chunk:
                break                       # EOF
            chunks.append(chunk)
            total += len(chunk)
        data = b"".join(chunks)[: dest.max_recv_bytes]
        if data:
            self._received.append(data)
        return data

    def _observation(self, action: Action, dest: TcpDestination, op: str, *, direction: str,
                     sent: bytes, received: bytes, identity_ok: bool) -> ExecutionResult:
        text = received.decode("utf-8", errors="replace")
        truncated = len(received) >= dest.max_recv_bytes
        return ExecutionResult(
            action_id=action.action_id, tool=action.tool,
            exit_code=0, stdout=text,
            authoritative_success=True,      # a real service response is an authoritative observation
            metadata={
                "op": op, "dest": dest.name, "direction": direction,
                "sent_bytes": len(sent), "received_bytes": len(received),
                "received_hex": received.hex(),           # binary-safe representation
                "truncated": truncated,
                "identity_ok": identity_ok,
                "expected_identity": dest.expected_identity,
            },
        )

    def _identity_ok(self, dest: TcpDestination, received: bytes) -> bool:
        if not dest.expected_identity:
            return True
        return dest.expected_identity in received.decode("latin-1", errors="replace")

    @staticmethod
    def _encode(input_data: object, params: dict) -> Optional[bytes]:
        encoding = str(params.get("encoding", "utf-8")).lower()
        if isinstance(input_data, bytes):
            return input_data
        if not isinstance(input_data, str) or input_data == "":
            if input_data == "":
                return b""
            return None
        if encoding == "hex":
            try:
                return bytes.fromhex(input_data.strip())
            except ValueError as exc:
                raise _Bounded(f"invalid hex payload: {exc}")
        if encoding not in _ENCODINGS:
            raise _Bounded(f"unsupported encoding {encoding!r}; allowed: {list(_ENCODINGS)}")
        return input_data.encode("latin-1" if encoding == "latin-1" else "utf-8", errors="strict")

    def _reject(self, action: Action, reason: str, *, op: str = "", dest: str = "") -> ExecutionResult:
        return ExecutionResult(
            action_id=action.action_id, tool=action.tool, input_rejected=True,
            metadata={"op": op, "dest": dest, "reason": reason},
        )

    def close_all(self) -> None:
        for conn in self._conns.values():
            _safe_close(conn.sock)
        self._conns.clear()


class _Bounded(Exception):
    """A bounded-control violation (turn/lifetime/encoding); surfaced as INPUT_REJECTION."""


def _safe_close(sock: object) -> None:
    try:
        sock.close()
    except Exception:  # noqa: BLE001
        pass


class ServiceTranscriptVerifier:
    """Authoritative verifier whose authority is the TRUSTED SERVICE's own emitted output.

    Wired as the frozen ``verifier_route`` (the same mechanism the demo verifier uses). It accepts a
    candidate flag if and only if that exact string was emitted by the registered TCP service during
    this session. It never hardcodes a flag and never manufactures verification: a historical /
    writeup flag that the live service did not emit is rejected. An optional ``flag_pattern`` adds a
    format guard.
    """

    def __init__(self, name: str, tcp_adapter: InteractiveTcpAdapter, *, flag_pattern: str = "") -> None:
        self.name = name
        self._tcp = tcp_adapter
        import re
        self._pattern = re.compile(flag_pattern) if flag_pattern else None

    def execute(self, action: Action) -> ExecutionResult:
        if action.tool != self.name:
            raise ValueError(f"ServiceTranscriptVerifier '{self.name}' cannot execute tool '{action.tool}'")
        candidate = self._candidate(action)
        accepted = bool(candidate) and self._tcp.service_emitted(candidate)
        if accepted and self._pattern is not None:
            accepted = self._pattern.search(candidate) is not None
        reason = "" if accepted else "candidate was not emitted by the trusted service this session"
        return ExecutionResult(
            action_id=action.action_id, tool=action.tool, exit_code=0,
            metadata={
                "submitted_candidate": candidate,
                "verifier_accepted": accepted,
                "rejection_reason": reason,
                "verification_basis": "service_transcript",
            },
        )

    @staticmethod
    def _candidate(action: Action) -> str:
        if isinstance(action.input_data, dict):
            value = action.input_data.get("flag", "")
            return str(value) if value is not None else ""
        if action.input_data:
            return str(action.input_data)
        return str(getattr(action, "candidate_flag", "") or "")
