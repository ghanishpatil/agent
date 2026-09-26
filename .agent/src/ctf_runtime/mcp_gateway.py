"""CtfAgentGateway — the thin, transport-agnostic gateway that sits between an MCP server and the
existing :class:`KiroBridge`.

Design constraints (from the integration spec):

* **No CTF intelligence lives here.** The gateway performs protocol-shaped work only: input
  validation, session lookup/isolation, ``KiroBridge`` calls, structured serialization, audit
  logging. All reasoning/planning/execution/verification stays inside the frozen ``ctf_agent``
  pipeline reached through ``KiroBridge`` -> ``AgentSession``.
* **No execution primitive is exposed.** There is no shell/http/subprocess/file method. The gateway
  cannot execute an action; only the frozen ``ReasoningLoop`` -> ``TrustKernel`` -> trusted adapters
  can.
* **The trusted environment is operator-owned.** The ``environment_factory`` and ``llm_client`` are
  supplied at construction by the operator. The MCP client (Kiro) supplies only *challenge intent*
  (text + optional in-memory resource content); it can never inject a tool, adapter, environment,
  verification policy, or model handle.
* **Untrusted input.** Everything arriving from the MCP client is validated (type, size, unexpected
  fields, path-traversal-safe resource filenames) before it reaches the bridge.

This module has no dependency on the ``mcp`` package, so it is fully unit-testable without a
transport. The FastMCP server in ``mcp_server.py`` is a thin adapter over this class.
"""

from __future__ import annotations

import base64
import json
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional

from ctf_agent.autonomy.contracts import (
    ChallengeInput,
    ChallengeResource,
    EnvironmentConfig,
    ResourceKind,
    SolveConstraints,
)

from .kiro_bridge import KiroBridge
from .learning import PostTerminalObserver
from .llm_client import LLMClient
from .routing import ModelRouter
from .tool_isolation import classification as _tool_classification

# ---- validation limits (defensive; untrusted MCP input) --------------------------------------
_MAX_TEXT = 20_000
_MAX_NAME = 256
_MAX_LIST = 64
_MAX_RESOURCES = 32
_MAX_RESOURCE_BYTES = 8 * 1024 * 1024  # 8 MiB per resource
_ALLOWED_START_KEYS = frozenset(
    {"name", "category", "description", "hints", "urls", "flag_format",
     "credentials", "attempt_limit", "resources", "challenge_id", "driver"}
)
# Keys that would attempt to cross the trust boundary — explicitly forbidden from the client.
_FORBIDDEN_START_KEYS = frozenset(
    {"permitted_tools", "tools", "adapter", "adapters", "environment", "environment_config",
     "verification_policy", "policy", "verifier_route", "evidence_rules", "llm_client",
     "model", "router", "kernel", "command", "shell", "exec", "input_data"}
)

# Lifecycle states (mirrors the spec; derived from the existing session semantics).
CREATED = "CREATED"
RUNNING = "RUNNING"
VERIFIED = "VERIFIED"
BLOCKED = "BLOCKED"
FAILED = "FAILED"
CLOSED = "CLOSED"

# The agent capabilities the gateway advertises — read-only description, NOT executable handles.
AGENT_CAPABILITIES = {
    "reasoning": "LLM proposes typed hypotheses/actions only; it holds no execution authority.",
    "planning": "ActionPlanner validates, ranks, and de-duplicates proposals (frozen).",
    "execution": "Only trusted adapters registered by the operator run, via TrustKernel (frozen).",
    "verification": "Kernel verification is authoritative; a candidate never auto-becomes a flag.",
    "failure_handling": "rate-limit/timeout/network/tool/environment failures never auto-disprove.",
    "journaling": "every executed step is recorded in the runtime session journal.",
    "exposed_execution_primitive": None,  # deliberately none
}

# The environment factory receives validated challenge *intent* and returns an operator-trusted env.
EnvironmentFactory = Callable[[Mapping[str, object]], EnvironmentConfig]


class GatewayError(Exception):
    """Base class for gateway-level errors (serialized to structured MCP errors)."""


class ValidationError(GatewayError):
    """Untrusted input failed validation."""


class UnknownSession(GatewayError):
    """A session id was not found in this gateway's registry."""


@dataclass
class _Session:
    session_id: str
    challenge_id: str
    challenge_name: str
    bridge: object                 # KiroBridge (internal driver) or KiroDrivenController (kiro driver)
    lifecycle: str = CREATED
    last_status: str = ""
    created_at: str = ""
    driver: str = "internal"       # "internal" (ctf_step/ctf_run) or "kiro" (ctf_observe/ctf_propose)
    learned: bool = False          # post-terminal observer has fired once for this session
    learning: Optional[dict] = None  # cached observer summary (writeup/experience artifacts)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _require_str(value: object, field_name: str, *, max_len: int = _MAX_TEXT, allow_empty: bool = True) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValidationError(f"field '{field_name}' must be a string")
    if len(value) > max_len:
        raise ValidationError(f"field '{field_name}' exceeds {max_len} characters")
    if not allow_empty and not value.strip():
        raise ValidationError(f"field '{field_name}' must not be empty")
    return value


def _require_str_list(value: object, field_name: str) -> tuple:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)):
        raise ValidationError(f"field '{field_name}' must be a list of strings")
    if len(value) > _MAX_LIST:
        raise ValidationError(f"field '{field_name}' has too many items (max {_MAX_LIST})")
    out = []
    for i, item in enumerate(value):
        out.append(_require_str(item, f"{field_name}[{i}]"))
    return tuple(out)


def _safe_filename(name: str) -> str:
    """Reject any path-traversal or absolute/relative path in a client-supplied filename."""
    name = _require_str(name, "resources[].filename", max_len=_MAX_NAME)
    if not name:
        return ""
    if "/" in name or "\\" in name or name in (".", "..") or ".." in name or ":" in name:
        raise ValidationError(f"unsafe resource filename: {name!r}")
    return name


class CtfAgentGateway:
    """Owns session lifecycle and delegates all solving to the existing ``KiroBridge``.

    The operator supplies the trusted seam (``environment_factory`` + ``llm_client``); the MCP
    client supplies only challenge intent through the tool methods below.
    """

    def __init__(
        self,
        *,
        environment_factory: EnvironmentFactory,
        llm_client: LLMClient,
        constraints: Optional[SolveConstraints] = None,
        router: Optional[ModelRouter] = None,
        journal_dir: Optional[Path] = None,
        audit_log_path: Optional[Path] = None,
        learning_root: Optional[Path] = None,
    ) -> None:
        if not callable(environment_factory):
            raise ValueError("environment_factory must be callable and operator-owned")
        if llm_client is None:
            raise ValueError("llm_client must be operator-owned and non-None")
        self._environment_factory = environment_factory
        self._llm_client = llm_client
        self._constraints = constraints
        self._router = router
        self._journal_dir = Path(journal_dir) if journal_dir else None
        self._audit_log_path = Path(audit_log_path) if audit_log_path else None
        # Continuous Experience Learning is OFF unless the operator supplies a learning_root.
        # When None, no experiences are written and behaviour is byte-identical to before — this is
        # why the existing suite (which never passes learning_root) is unaffected.
        self._observer: Optional[PostTerminalObserver] = (
            PostTerminalObserver(Path(learning_root)) if learning_root else None
        )
        self._sessions: Dict[str, _Session] = {}
        self._audit: List[dict] = []
        self._lock = threading.RLock()

    # -- audit -----------------------------------------------------------------------------
    def _audit_record(self, tool: str, session_id: str, outcome: str, **extra) -> None:
        rec = {"timestamp": _now(), "tool": tool, "session_id": session_id, "outcome": outcome}
        rec.update(extra)
        self._audit.append(rec)
        if self._audit_log_path is not None:
            try:
                self._audit_log_path.parent.mkdir(parents=True, exist_ok=True)
                with self._audit_log_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, sort_keys=True) + "\n")
            except OSError:
                pass  # audit logging must never break solving

    def audit_records(self) -> List[dict]:
        return list(self._audit)

    # -- session lookup --------------------------------------------------------------------
    def _get(self, session_id: object) -> _Session:
        if not isinstance(session_id, str) or not session_id:
            raise ValidationError("session_id must be a non-empty string")
        with self._lock:
            session = self._sessions.get(session_id)
        if session is None:
            raise UnknownSession(f"unknown session_id: {session_id}")
        return session

    def _refresh_lifecycle(self, session: _Session) -> None:
        if session.bridge.is_verified():
            session.lifecycle = VERIFIED

    # -- post-terminal learning (failure-safe; fires at most once per session) --------------
    def _fire_observer(self, session: _Session) -> None:
        """Run the post-terminal observer exactly once. Failure-safe: never raises, never affects
        the solve result, the verified flag, or verification state."""
        if self._observer is None or session.learned:
            return
        session.learned = True  # set first, so a learning error can never cause a re-fire loop
        try:
            result = session.bridge.get_result()
            journal = session.bridge.session_journal()
            observations = session.bridge.recent_observations(50)
            summary = self._observer.observe(
                result, session_id=session.session_id, driver=session.driver,
                session_journal=journal, observations=observations,
            )
            session.learning = summary
            self._audit_record(
                "learning", session.session_id,
                "ok" if summary.get("learned") else "soft_error",
                source_kind=summary.get("source_kind"), record_id=summary.get("record_id"),
                writeup_grounded=summary.get("writeup_grounded"), learn_error=summary.get("error"),
            )
        except Exception as exc:  # noqa: BLE001 — learning must never break the gateway
            session.learning = {"learned": False, "error": f"{type(exc).__name__}: {exc}"}
            self._audit_record("learning", session.session_id, "soft_error",
                               learn_error=f"{type(exc).__name__}: {exc}")

    # -- tool: ctf_start -------------------------------------------------------------------
    def ctf_start(self, challenge: Mapping[str, object]) -> dict:
        """Create a NEW isolated session from challenge intent only. No executable input accepted."""
        if not isinstance(challenge, Mapping):
            raise ValidationError("challenge must be an object/dict")
        forbidden = _FORBIDDEN_START_KEYS & set(challenge.keys())
        if forbidden:
            raise ValidationError(
                "challenge must not carry execution/environment fields "
                f"(forbidden: {sorted(forbidden)}); the trusted environment is operator-owned"
            )
        unexpected = set(challenge.keys()) - _ALLOWED_START_KEYS
        if unexpected:
            raise ValidationError(f"unexpected field(s): {sorted(unexpected)}")

        name = _require_str(challenge.get("name"), "name", max_len=_MAX_NAME, allow_empty=False)
        category = _require_str(challenge.get("category"), "category", max_len=_MAX_NAME)
        description = _require_str(challenge.get("description"), "description")
        flag_format = _require_str(challenge.get("flag_format"), "flag_format", max_len=_MAX_NAME)
        hints = _require_str_list(challenge.get("hints"), "hints")
        urls = _require_str_list(challenge.get("urls"), "urls")

        credentials_in = challenge.get("credentials") or {}
        if not isinstance(credentials_in, Mapping):
            raise ValidationError("field 'credentials' must be an object")
        credentials: Dict[str, str] = {}
        for k, v in credentials_in.items():
            credentials[_require_str(k, "credentials.key", max_len=_MAX_NAME)] = _require_str(
                v, "credentials.value", max_len=_MAX_TEXT
            )

        attempt_limit = challenge.get("attempt_limit")
        if attempt_limit is not None and (not isinstance(attempt_limit, int) or isinstance(attempt_limit, bool) or attempt_limit < 0):
            raise ValidationError("attempt_limit must be a non-negative integer")

        resources = self._validate_resources(challenge.get("resources"))

        driver = _require_str(challenge.get("driver"), "driver", max_len=16) or "internal"
        if driver not in ("internal", "kiro"):
            raise ValidationError("driver must be 'internal' or 'kiro'")

        # Build the operator-trusted environment from intent (factory owns tools/adapters/policy).
        meta = {"name": name, "category": category, "flag_format": flag_format, "urls": urls}
        env = self._environment_factory(meta)
        if not isinstance(env, EnvironmentConfig):
            raise GatewayError("environment_factory did not return an EnvironmentConfig")

        session_id = uuid.uuid4().hex
        journal_path = (self._journal_dir / f"{session_id}.jsonl") if self._journal_dir else None

        if driver == "kiro":
            # Architecture A: Kiro is the reasoner. No LLM client is used inside the runtime.
            from .kiro_driven import KiroDrivenController
            ch = ChallengeInput(
                name=name, category=category or None, description=description or None,
                hints=hints, flag_format=flag_format or None, urls=urls,
                credentials=credentials, attempt_limit=attempt_limit,
            )
            res_tuple = tuple(
                ChallengeResource(resource_id=r["resource_id"], kind=r["kind"],
                                  content=r["content"], filename=r["filename"])
                for r in resources
            )
            holder = KiroDrivenController(
                ch, environment=env, constraints=self._constraints,
                resources=res_tuple, session_journal_path=journal_path,
            )
            initial_state = holder.get_state()
            chain = "MCP->CtfAgentGateway->KiroDrivenController->AgentSession(QueuedReasoningSource)"
        else:
            holder = KiroBridge(
                environment=env, llm_client=self._llm_client, constraints=self._constraints,
                router=self._router, session_journal_path=journal_path,
            )
            for res in resources:
                holder.provide_resource(
                    res["resource_id"], res["kind"], content=res["content"], filename=res["filename"]
                )
            initial_state = holder.start_challenge(
                name=name, category=category, description=description, hints=hints,
                urls=urls, flag_format=flag_format, credentials=credentials,
                attempt_limit=attempt_limit,
            )
            chain = "MCP->CtfAgentGateway->KiroBridge->AgentSession"

        challenge_id = str(initial_state.get("run_id", session_id))
        with self._lock:
            self._sessions[session_id] = _Session(
                session_id=session_id, challenge_id=challenge_id, challenge_name=name,
                bridge=holder, lifecycle=CREATED, created_at=_now(), driver=driver,
            )
        self._audit_record(
            "ctf_start", session_id, "ok", challenge_id=challenge_id, driver=driver,
            chain=chain, challenge_name=name,
        )
        return {
            "session_id": session_id,
            "challenge_id": challenge_id,
            "status": CREATED,
            "driver": driver,
            "initial_state": initial_state,
            "available_agent_capabilities": dict(AGENT_CAPABILITIES),
        }

    def _validate_resources(self, raw: object) -> List[dict]:
        if raw is None:
            return []
        if not isinstance(raw, (list, tuple)):
            raise ValidationError("field 'resources' must be a list")
        if len(raw) > _MAX_RESOURCES:
            raise ValidationError(f"too many resources (max {_MAX_RESOURCES})")
        out: List[dict] = []
        for i, item in enumerate(raw):
            if not isinstance(item, Mapping):
                raise ValidationError(f"resources[{i}] must be an object")
            if "path" in item:
                raise ValidationError(
                    f"resources[{i}] must not supply a filesystem 'path'; provide 'content_b64' instead"
                )
            rid = _require_str(item.get("resource_id"), f"resources[{i}].resource_id",
                               max_len=_MAX_NAME, allow_empty=False)
            kind_str = _require_str(item.get("kind"), f"resources[{i}].kind", max_len=_MAX_NAME,
                                    allow_empty=False)
            try:
                kind = ResourceKind(kind_str)
            except ValueError:
                raise ValidationError(
                    f"resources[{i}].kind '{kind_str}' invalid; allowed: {[k.value for k in ResourceKind]}"
                )
            filename = _safe_filename(item.get("filename", ""))
            b64 = item.get("content_b64")
            if b64 is None:
                raise ValidationError(f"resources[{i}] requires 'content_b64'")
            b64 = _require_str(b64, f"resources[{i}].content_b64", max_len=_MAX_RESOURCE_BYTES * 2)
            try:
                content = base64.b64decode(b64, validate=True)
            except Exception:
                raise ValidationError(f"resources[{i}].content_b64 is not valid base64")
            if len(content) > _MAX_RESOURCE_BYTES:
                raise ValidationError(f"resources[{i}] exceeds {_MAX_RESOURCE_BYTES} bytes")
            out.append({"resource_id": rid, "kind": kind, "filename": filename, "content": content})
        return out

    # -- tool: ctf_step --------------------------------------------------------------------
    def ctf_step(self, session_id: str) -> dict:
        session = self._get(session_id)
        if session.driver == "kiro":
            raise ValidationError("this session is kiro-driven; use ctf_observe/ctf_propose instead of ctf_step")
        report = session.bridge.next_step()
        if session.lifecycle == CREATED:
            session.lifecycle = RUNNING
        self._refresh_lifecycle(session)
        evidence = session.bridge.get_evidence()
        pending = session.bridge.get_pending_actions()
        self._audit_record("ctf_step", session_id, "ok", step=report.step_index,
                           executed=report.executed)
        return {
            "session_id": session_id,
            "step": report.step_index,
            "executed": report.executed,
            "model": report.model,
            "escalation_reason": report.escalation_reason,
            "hypothesis_id": report.hypothesis_id,
            "hypothesis_state": report.hypothesis_state,
            "pending_actions": pending,
            "latest_observation": {
                "action_tool": report.action_tool,
                "action_objective": report.action_objective,
                "planner_decision": report.planner_decision,
                "observation_class": report.observation_class,
                "impact": report.impact,
            },
            "latest_evidence": evidence[-1] if evidence else None,
            "verification_state": VERIFIED if report.verified else session.lifecycle,
            "progress": session.bridge.progress(),
        }

    # -- tool: ctf_run ---------------------------------------------------------------------
    def ctf_run(self, session_id: str, max_steps: Optional[int] = None) -> dict:
        session = self._get(session_id)
        if session.driver == "kiro":
            raise ValidationError("this session is kiro-driven; use ctf_observe/ctf_propose instead of ctf_run")
        if max_steps is not None and (not isinstance(max_steps, int) or isinstance(max_steps, bool) or max_steps <= 0):
            raise ValidationError("max_steps must be a positive integer")
        result = session.bridge.run(max_steps)
        session.last_status = str(result.get("status", ""))
        session.lifecycle = self._lifecycle_from_status(session, session.last_status)
        self._audit_record("ctf_run", session_id, "ok", status=session.last_status,
                           verified=session.bridge.is_verified())
        # Post-terminal learning for the internal driver: only when a terminal lifecycle is reached.
        if session.lifecycle in (VERIFIED, BLOCKED, FAILED):
            self._fire_observer(session)
        return {
            "session_id": session_id,
            "status": result.get("status"),
            "lifecycle": session.lifecycle,
            "verified_flag": result.get("verified_flag"),
            "terminal_reason": result.get("terminal_reason"),
            "actions": result.get("actions"),
            "journal_path": result.get("journal_path"),
        }

    def _lifecycle_from_status(self, session: _Session, status: str) -> str:
        if session.bridge.is_verified():
            return VERIFIED
        mapping = {
            "SOLVED": VERIFIED,
            "BLOCKED": BLOCKED,
            "EXHAUSTED": BLOCKED,
            "TIMEOUT": FAILED,
            "FAILED": FAILED,
            "INVALID_INPUT": FAILED,
        }
        return mapping.get(status, RUNNING)

    # -- read-only tools -------------------------------------------------------------------
    def ctf_state(self, session_id: str) -> dict:
        session = self._get(session_id)
        state = session.bridge.get_state()
        state["session_id"] = session_id
        state["lifecycle"] = VERIFIED if session.bridge.is_verified() else session.lifecycle
        return state

    def ctf_hypotheses(self, session_id: str) -> dict:
        session = self._get(session_id)
        return {"session_id": session_id, "hypotheses": session.bridge.get_hypotheses()}

    def ctf_evidence(self, session_id: str) -> dict:
        session = self._get(session_id)
        return {"session_id": session_id, "evidence": session.bridge.get_evidence()}

    def ctf_progress(self, session_id: str) -> dict:
        session = self._get(session_id)
        progress = session.bridge.progress()
        progress["session_id"] = session_id
        progress["lifecycle"] = VERIFIED if session.bridge.is_verified() else session.lifecycle
        progress["last_status"] = session.last_status
        return progress

    def ctf_result(self, session_id: str) -> dict:
        """Read-only final result. Distinguishes verified / candidate / none / blocked / failed.

        A candidate string is NEVER promoted to a verified flag here — verification is owned by the
        frozen kernel, and ``get_flag()`` only returns a value on a kernel VERIFIED + STOP.
        """
        session = self._get(session_id)
        verified = session.bridge.is_verified()
        flag = session.bridge.get_flag() if verified else None
        # Candidate (proposed but NOT verified) flags, surfaced transparently and never as the flag.
        candidates = [
            a.get("candidate_flag")
            for a in session.bridge.get_pending_actions()
            if a.get("candidate_flag")
        ]
        if verified and flag:
            result_type = "VERIFIED_FLAG"
        elif session.lifecycle == BLOCKED:
            result_type = "BLOCKED"
        elif session.lifecycle == FAILED:
            result_type = "FAILED"
        elif candidates:
            result_type = "CANDIDATE_ONLY"
        else:
            result_type = "NO_FLAG"
        return {
            "session_id": session_id,
            "result_type": result_type,
            "verified": verified,
            "verified_flag": flag,                       # None unless kernel-verified
            "candidate_flags": candidates,               # never authoritative
            "lifecycle": session.lifecycle,
            "last_status": session.last_status,
        }

    # -- read-only diagnostics -------------------------------------------------------------
    def ctf_sessions(self) -> dict:
        with self._lock:
            sessions = [
                {"session_id": s.session_id, "challenge_id": s.challenge_id,
                 "challenge_name": s.challenge_name,
                 "lifecycle": VERIFIED if s.bridge.is_verified() else s.lifecycle}
                for s in self._sessions.values()
            ]
        return {"sessions": sessions, "count": len(sessions)}

    def ctf_trust_boundary(self) -> dict:
        """Read-only: the static tool-isolation classification (what is governed vs ungoverned)."""
        return _tool_classification()

    # -- Architecture A: Kiro-driven observe/propose ---------------------------------------
    def ctf_observe(self, session_id: str) -> dict:
        """Read-only authoritative state for a KIRO-DRIVEN session, plus the proposal schema."""
        session = self._get(session_id)
        if session.driver != "kiro":
            raise ValidationError("ctf_observe is only valid for a kiro-driven session (start with driver='kiro')")
        obs = session.bridge.observe()
        obs["session_id"] = session_id
        obs["lifecycle"] = VERIFIED if session.bridge.is_verified() else session.lifecycle
        self._audit_record("ctf_observe", session_id, "ok")
        return obs

    def ctf_propose(self, session_id: str, hypotheses: object = None, actions: object = None) -> dict:
        """Submit Kiro's typed hypotheses/actions; they flow through the frozen validate->plan->
        kernel->adapter->evidence->verify pipeline. Kiro never executes anything directly."""
        session = self._get(session_id)
        if session.driver != "kiro":
            raise ValidationError("ctf_propose is only valid for a kiro-driven session (start with driver='kiro')")
        if session.lifecycle == CREATED:
            session.lifecycle = RUNNING
        result = session.bridge.propose(hypotheses, actions)
        if session.bridge.is_verified():
            session.lifecycle = VERIFIED
            # Kiro-driven success is terminal the moment the kernel verifies the flag.
            self._fire_observer(session)
        result["session_id"] = session_id
        result["lifecycle"] = session.lifecycle
        self._audit_record("ctf_propose", session_id, "ok",
                           accepted_actions=len(result.get("accepted", {}).get("actions", [])),
                           executed=len(result.get("executed", [])),
                           verified=session.bridge.is_verified())
        return result

    def session_journal(self, session_id: str) -> List[dict]:
        """Read-only: the agent's runtime session journal (proves the executed pipeline chain)."""
        return self._get(session_id).bridge.session_journal()

    def close_session(self, session_id: str) -> dict:
        session = self._get(session_id)
        # Kiro-driven sessions have no single terminal call, so a session that closed without a
        # verified flag is captured as a failure experience here (fires at most once).
        if session.driver == "kiro" and not session.learned:
            self._fire_observer(session)
        session.lifecycle = CLOSED
        self._audit_record("close_session", session_id, "ok")
        return {"session_id": session_id, "lifecycle": CLOSED}

    # -- read-only learning artifact accessors ---------------------------------------------
    def get_writeup(self, session_id: str) -> dict:
        """Read-only: the grounded writeup generated for a terminal SOLVED session (if any)."""
        session = self._get(session_id)
        learning = session.learning or {}
        return {
            "session_id": session_id,
            "available": bool(learning.get("writeup_markdown")),
            "grounded": learning.get("writeup_grounded"),
            "writeup_ref": learning.get("writeup_ref", ""),
            "markdown": learning.get("writeup_markdown", ""),
            "flag": (learning.get("record") or {}).get("verified_flag"),
            "errors": learning.get("writeup_errors", []),
        }

    def get_experience(self, session_id: str) -> dict:
        """Read-only: the experience record derived for a terminal session (success or failure)."""
        session = self._get(session_id)
        learning = session.learning or {}
        return {
            "session_id": session_id,
            "learned": bool(learning.get("learned")),
            "source_kind": learning.get("source_kind"),
            "record_id": learning.get("record_id"),
            "record": learning.get("record"),
            "manifest": learning.get("manifest"),
            "error": learning.get("error"),
        }
