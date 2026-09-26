"""Operator-controlled REAL CTF environment builder.

This is the seam that turns the offline demo into a real, operator-authorized runtime WITHOUT
touching the frozen solver. It composes the **frozen** trusted adapters
(`ctf_agent.adapters.{FileAdapter, HttpAdapter, SubprocessAdapter}`) into an ``EnvironmentConfig``
according to an explicit :class:`OperatorPolicy`.

Security model (all enforced by the frozen adapters + the strict `AdapterRegistry`):

* **File**: read-only, confined to one ``resource_root``; any path escaping the root is refused
  (path-traversal safe); size-capped.
* **HTTP**: only requests whose target matches an operator ``allowed_host_prefixes`` allow-list run;
  everything else is refused *before* any network I/O.
* **Process**: one fixed executable per registered adapter (args-only). There is NO
  ``execute_anything(cmd)`` — an executable the operator did not register simply has no adapter and
  is rejected by the registry (``REJECTED_TOOL``).
* **Registry**: unknown/unregistered tool names cannot execute.

The LLM never receives any of these adapter objects — only the reasoning source (inside the frozen
loop) is handed the registry, and the LLM boundary passes text only.

Nothing here executes anything on import or construction; adapters run only when the frozen
``ReasoningLoop`` -> ``TrustKernel`` drives a validated action.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional, Tuple

from ctf_agent import CandidateVerifierRoute
from ctf_agent.adapters.file_adapter import FileAdapter
from ctf_agent.adapters.http_adapter import HttpAdapter, HttpPolicy
from ctf_agent.adapters.subprocess_adapter import SubprocessAdapter, SubprocessCommand
from ctf_agent.autonomy.contracts import (
    EnvironmentConfig,
    EvidenceRule,
    PermittedTool,
    SolveConstraints,
)

from .tcp_adapter import (
    TCP_TOOL_NAME,
    InteractiveTcpAdapter,
    ServiceTranscriptVerifier,
    TcpDestination,
)


@dataclass(frozen=True)
class AllowedExecutable:
    """One operator-approved local executable, exposed as a fixed-executable process adapter."""

    tool_name: str
    executable: str
    fixed_args: Tuple[str, ...] = ()
    timeout_seconds: float = 10.0
    network: bool = False


@dataclass(frozen=True)
class OperatorPolicy:
    """Everything the operator explicitly authorizes for a real run. Deny-by-default: anything not
    listed here has no adapter and cannot be executed."""

    # Read-only file inspection confined to the per-session workspace (where resources materialize).
    enable_file_read: bool = True
    file_tool_name: str = "read_file"
    max_file_bytes: int = 1_048_576

    # HTTP: explicit scheme://host allow-list. Empty => no HTTP adapter registered at all.
    http_tool_name: str = "http_probe"
    allowed_host_prefixes: Tuple[str, ...] = ()
    http_timeout_seconds: float = 5.0
    http_max_body_bytes: int = 65_536

    # Process: explicit list of fixed executables. Empty => no process execution possible.
    allowed_executables: Tuple[AllowedExecutable, ...] = ()

    # Interactive TCP: explicit list of operator-registered destinations. Empty => no TCP adapter.
    tcp_destinations: Tuple[TcpDestination, ...] = ()
    tcp_tool_name: str = TCP_TOOL_NAME
    tcp_socket_factory: object = None      # test injection; None => real AF_INET/SOCK_STREAM socket
    # When True, an authoritative verifier is wired whose authority is the trusted TCP service's own
    # emitted output (a candidate verifies only if the live service emitted it this session). This is
    # the explicit operator registration of "the live service response is the verification route".
    tcp_service_verifier: bool = False
    tcp_verifier_tool_name: str = "flag_verifier"
    tcp_verifier_target: str = "service-transcript"
    tcp_flag_pattern: str = ""

    # Verification: optional operator/challenge verifier. Without it, a candidate can NEVER be
    # verified (VERIFIED_FLAG is impossible) — which is the correct behavior for a challenge that
    # provides no authoritative check.
    verifier_tool_name: str = ""
    verifier_target: str = ""
    verifier_adapter: object = None  # must implement ToolAdapter.execute; operator-supplied

    # Challenge-specific evidence rules (what body substrings support/contradict which hypothesis).
    evidence_rules: Tuple[EvidenceRule, ...] = ()

    # Per-tool authoritative observation sources. For an observation to SUPPORT a hypothesis, its
    # source must appear BOTH here (operator-trusted per tool) AND in the matching evidence rule's
    # authoritative_sources. This is what lets a real adapter's output become authoritative.
    authoritative_sources_by_tool: Mapping[str, Tuple[str, ...]] = field(default_factory=dict)

    # Budgets.
    constraints: SolveConstraints = field(default_factory=SolveConstraints)

    def summary(self) -> dict:
        return {
            "file_read": self.enable_file_read,
            "http_targets": list(self.allowed_host_prefixes),
            "executables": [e.executable for e in self.allowed_executables],
            "verifier": bool(self.verifier_adapter),
            "evidence_rules": [r.hypothesis_id for r in self.evidence_rules],
        }


def build_operator_environment(policy: OperatorPolicy, workspace_root: Path) -> EnvironmentConfig:
    """Compose a frozen-adapter-based :class:`EnvironmentConfig` from an operator policy.

    ``workspace_root`` is the per-session sandbox: challenge resources materialize here and the
    read-only file adapter is confined to it.
    """
    workspace_root = Path(workspace_root)
    workspace_root.mkdir(parents=True, exist_ok=True)

    permitted: list[PermittedTool] = []

    auth = policy.authoritative_sources_by_tool

    if policy.enable_file_read:
        permitted.append(PermittedTool(
            policy.file_tool_name,
            FileAdapter(policy.file_tool_name, workspace_root, max_bytes=policy.max_file_bytes),
            authoritative_sources=tuple(auth.get(policy.file_tool_name, ())),
        ))

    if policy.allowed_host_prefixes:
        permitted.append(PermittedTool(
            policy.http_tool_name,
            HttpAdapter(policy.http_tool_name, HttpPolicy(
                allowed_host_prefixes=tuple(policy.allowed_host_prefixes),
                timeout_seconds=policy.http_timeout_seconds,
                max_body_bytes=policy.http_max_body_bytes,
            )),
            authoritative_sources=tuple(auth.get(policy.http_tool_name, ())),
            network=True, remote=True,
        ))

    for exe in policy.allowed_executables:
        permitted.append(PermittedTool(
            exe.tool_name,
            SubprocessAdapter(exe.tool_name, SubprocessCommand(exe.executable, exe.fixed_args),
                              timeout_seconds=exe.timeout_seconds),
            authoritative_sources=tuple(auth.get(exe.tool_name, ())),
            network=exe.network,
        ))

    # Interactive TCP adapter (registered destinations only; bounded). One session-scoped instance;
    # its output is NOT marked authoritative_output, so it can never self-verify a flag.
    tcp_adapter: Optional[InteractiveTcpAdapter] = None
    if policy.tcp_destinations:
        tcp_adapter = InteractiveTcpAdapter(
            policy.tcp_tool_name, tuple(policy.tcp_destinations),
            socket_factory=policy.tcp_socket_factory,
        )
        permitted.append(PermittedTool(
            policy.tcp_tool_name, tcp_adapter,
            authoritative_sources=tuple(d.name for d in policy.tcp_destinations),
            network=True, remote=True,
        ))

    verifier_route: Optional[CandidateVerifierRoute] = None
    # Preferred for TCP challenges: an authoritative verifier bound to the trusted service transcript.
    if policy.tcp_service_verifier and tcp_adapter is not None:
        verifier = ServiceTranscriptVerifier(
            policy.tcp_verifier_tool_name, tcp_adapter, flag_pattern=policy.tcp_flag_pattern,
        )
        permitted.append(PermittedTool(
            policy.tcp_verifier_tool_name, verifier, verifier=True, remote=True,
        ))
        verifier_route = CandidateVerifierRoute(
            policy.tcp_verifier_tool_name, policy.tcp_verifier_target or "service-transcript"
        )
    elif policy.verifier_adapter is not None and policy.verifier_tool_name:
        permitted.append(PermittedTool(
            policy.verifier_tool_name, policy.verifier_adapter, verifier=True, remote=True,
        ))
        verifier_route = CandidateVerifierRoute(
            policy.verifier_tool_name, policy.verifier_target or "operator-grader"
        )

    return EnvironmentConfig(
        permitted_tools=tuple(permitted),
        evidence_rules=tuple(policy.evidence_rules),
        verifier_route=verifier_route,
        workspace_root=workspace_root,
        journal_path=workspace_root / "journal.jsonl",
        run_id=workspace_root.name,
        model_configuration="operator-real-runtime",
    )


# --------------------------------------------------------------------------------------------
# Operator gateway factory: wires the operator policy + a real LLM client + the frozen router
# into a CtfAgentGateway the MCP server can serve. Point CTF_MCP_GATEWAY_FACTORY at an operator
# module that calls build_operator_gateway(policy, llm_client) with a REAL LLMClient.
# --------------------------------------------------------------------------------------------

import tempfile
import uuid


def build_operator_gateway(
    policy: "OperatorPolicy",
    llm_client,
    *,
    router=None,
    workspace_base: Optional[Path] = None,
    journal_dir: Optional[Path] = None,
    audit_log_path: Optional[Path] = None,
    learning_root: Optional[Path] = None,
    enable_learning: bool = True,
):
    """Build a real, operator-controlled gateway. ``llm_client`` MUST be an operator-owned
    ``LLMClient`` (e.g. ``CallableLLMClient`` wrapping the operator's model API). The frozen
    ``ModelRouter`` (FAST/DEEP/FALLBACK/HIGH_END) is preserved unless the operator supplies one.

    Continuous Experience Learning is enabled by default and writes only under
    ``learning_root`` (defaults to ``<workspace_base>/agent_experience_v1``). Set
    ``enable_learning=False`` to disable it entirely.
    """
    from .mcp_gateway import CtfAgentGateway
    from .routing import ModelRouter

    base = Path(workspace_base) if workspace_base else Path(tempfile.mkdtemp(prefix="ctf_real_"))
    base.mkdir(parents=True, exist_ok=True)

    def factory(meta):
        session_dir = base / ("session_" + uuid.uuid4().hex[:12])
        return build_operator_environment(policy, session_dir)

    if enable_learning:
        learn = Path(learning_root) if learning_root else (base / "agent_experience_v1")
    else:
        learn = None

    return CtfAgentGateway(
        environment_factory=factory,
        llm_client=llm_client,
        constraints=policy.constraints,
        router=router or ModelRouter(),
        journal_dir=journal_dir or (base / "journals"),
        audit_log_path=audit_log_path or (base / "audit.jsonl"),
        learning_root=learn,
    )
