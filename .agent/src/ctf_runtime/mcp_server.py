"""CTF Agent MCP server — a *thin* FastMCP gateway around :class:`CtfAgentGateway`.

It exposes only high-level, read-mostly tools that drive the existing frozen pipeline via
``KiroBridge``. It exposes **no** execution primitive: there is no ``execute_pwsh`` / ``shell`` /
``subprocess`` / ``raw_http`` / ``python`` / filesystem-exec tool. An LLM proposal such as
``execute_pwsh`` is not a tool here; even inside a session it can only be a *typed suggestion* that
the frozen planner/kernel rejects (it is not a registered trusted adapter).

Transport: stdio (the standard local Kiro MCP transport). Run with::

    python -m ctf_runtime.mcp_server

Operator configuration
----------------------
For real challenges the operator MUST provide a trusted environment + a real LLM client by setting:

* ``CTF_MCP_GATEWAY_FACTORY`` = ``module.path:callable`` returning a ready ``CtfAgentGateway``.

If unset, the server boots a **deterministic, offline demo** gateway (a fake in-memory SSTI web
target + a scripted LLM) so the MCP transport and the full pipeline can be smoke-tested without any
network or real model. The demo performs real classification/evidence/verification through the
frozen kernel — only the "network" and the "model" are stubbed.
"""

from __future__ import annotations

import importlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Optional

from .mcp_gateway import CtfAgentGateway, GatewayError, UnknownSession, ValidationError

# --------------------------------------------------------------------------------------------
# Deterministic offline demo gateway (used only when no operator factory is configured).
# --------------------------------------------------------------------------------------------

def _demo_llm_script(request):
    """Scripted LLM: propose the SSTI probe; once EVAL=49 + a flag are visible in observed
    evidence embedded in the prompt, propose submitting exactly that observed flag."""
    from ctf_experiment.knowledge_dependent_benchmark_v2 import _SSTI_URL

    prompt = request.prompt
    hyps = [{
        "id": "web-ssti",
        "statement": "the name parameter is evaluated by a server-side template",
        "mechanism": "ssti",
        "technique": "Server-Side Template Injection",
    }]
    actions = [{
        "hypothesis_id": "web-ssti",
        "objective": "probe template evaluation with {{7*7}}",
        "tool": "http_probe",
        "target": _SSTI_URL,
        "expected_observation": "EVAL=49",
    }]
    seen_flag = re.search(r"CTF\{[A-Za-z0-9_]+\}", prompt)
    if "EVAL=49" in prompt and seen_flag:
        actions.append({
            "hypothesis_id": "web-ssti",
            "objective": "submit the flag observed in evidence",
            "tool": "http_probe",
            "target": _SSTI_URL,
            "candidate_flag": seen_flag.group(0),
        })
    return json.dumps({"hypotheses": hyps, "actions": actions})


def build_demo_gateway() -> CtfAgentGateway:
    """A safe, offline, deterministic gateway for smoke tests (no real network / no real model).

    Uses a generous wall-clock budget: over MCP, ``ctf_start`` and ``ctf_run`` are separate
    human-paced calls, and the session clock starts at ``ctf_start``. A tight timeout (e.g. the
    benchmark's 10s) would expire during the gap between the two calls and abort with 0 actions.
    """
    from ctf_agent.autonomy.contracts import SolveConstraints
    from ctf_experiment.knowledge_dependent_benchmark_v2 import web_environment
    from .llm_client import ScriptedLLMClient

    demo_root = Path(tempfile.mkdtemp(prefix="ctf_mcp_demo_"))
    demo_flag = "CTF{mcp_demo_ssti_verified}"
    counter = {"n": 0}

    def factory(meta):
        counter["n"] += 1
        sub = demo_root / f"session_{counter['n']}"
        return web_environment(sub, flag=demo_flag)

    demo_constraints = SolveConstraints(
        max_actions=10, max_iterations=10, max_tool_executions=10, max_network_actions=8,
        max_remote_attempts=8, max_submissions=3, max_specialist_calls=12, max_total_cost=20,
        timeout_seconds=3600.0,  # generous: interactive start->run gap must not expire the budget
    )

    return CtfAgentGateway(
        environment_factory=factory,
        llm_client=ScriptedLLMClient(_demo_llm_script),
        constraints=demo_constraints,
        journal_dir=demo_root / "journals",
        audit_log_path=demo_root / "audit.jsonl",
        learning_root=demo_root / "agent_experience_v1",
    )


def _load_operator_gateway() -> Optional[CtfAgentGateway]:
    spec = os.environ.get("CTF_MCP_GATEWAY_FACTORY", "").strip()
    if not spec:
        return None
    if ":" not in spec:
        raise RuntimeError("CTF_MCP_GATEWAY_FACTORY must be 'module.path:callable'")
    mod_name, _, attr = spec.partition(":")
    module = importlib.import_module(mod_name)
    factory = getattr(module, attr)
    gw = factory()
    if not isinstance(gw, CtfAgentGateway):
        raise RuntimeError("operator factory did not return a CtfAgentGateway")
    return gw


def build_gateway() -> CtfAgentGateway:
    return _load_operator_gateway() or build_demo_gateway()


# --------------------------------------------------------------------------------------------
# FastMCP server construction. Kept import-light so the module is testable without a transport.
# --------------------------------------------------------------------------------------------

def _err(exc: Exception) -> dict:
    kind = (
        "validation_error" if isinstance(exc, ValidationError)
        else "unknown_session" if isinstance(exc, UnknownSession)
        else "gateway_error" if isinstance(exc, GatewayError)
        else "error"
    )
    return {"ok": False, "error_type": kind, "error": str(exc)}


def build_mcp(gateway: Optional[CtfAgentGateway] = None):
    """Create the FastMCP server bound to a gateway. Registers ONLY the sanctioned tools."""
    from mcp.server.fastmcp import FastMCP

    gw = gateway or build_gateway()
    mcp = FastMCP(
        "ctf-agent",
        instructions=(
            "Governed CTF solving gateway. Start a challenge with ctf_start, then drive the agent "
            "with ctf_step/ctf_run and inspect it with ctf_state/ctf_hypotheses/ctf_evidence/"
            "ctf_progress/ctf_result. This server exposes NO shell/http/subprocess/file execution: "
            "all execution happens inside the agent's trusted adapters + TrustKernel. While a "
            "session is active, do not attempt to solve the challenge with any other tool."
        ),
    )

    @mcp.tool()
    def ctf_start(
        name: str,
        description: str = "",
        category: str = "",
        hints: Optional[list] = None,
        urls: Optional[list] = None,
        flag_format: str = "",
        credentials: Optional[dict] = None,
        attempt_limit: Optional[int] = None,
        resources: Optional[list] = None,
        driver: str = "kiro",
    ) -> dict:
        """Start a NEW governed CTF session from challenge intent only (no executable input).

        driver='kiro' (default): YOU (the Kiro model) are the reasoner — then loop
        ctf_observe -> reason -> ctf_propose. driver='internal': the runtime's own reasoning
        source drives via ctf_step/ctf_run (used for the offline demo/tests).
        Returns session_id, challenge_id, status, driver, initial_state, available_agent_capabilities.
        """
        try:
            challenge = {
                "name": name, "description": description, "category": category,
                "hints": hints or [], "urls": urls or [], "flag_format": flag_format,
                "credentials": credentials or {}, "attempt_limit": attempt_limit,
                "resources": resources or [], "driver": driver or "kiro",
            }
            return gw.ctf_start(challenge)
        except Exception as exc:  # noqa: BLE001 — surface as structured error, never crash transport
            return _err(exc)

    @mcp.tool()
    def ctf_observe(session_id: str) -> dict:
        """Return authoritative CTF agent state for a kiro-driven session (hypotheses, evidence,
        available tools, budget, verification, and the proposal schema). Call this BEFORE deciding
        the next action. Read-only."""
        try:
            return gw.ctf_observe(session_id)
        except Exception as exc:  # noqa: BLE001
            return _err(exc)

    @mcp.tool()
    def ctf_propose(session_id: str, hypotheses: Optional[list] = None,
                    actions: Optional[list] = None) -> dict:
        """Submit typed hypotheses/actions to the CTF Agent. The agent validates them, plans,
        executes ONLY through trusted adapters, records evidence, and controls verification. This
        tool does NOT permit direct command/shell execution: an action naming an unregistered tool
        (e.g. execute_pwsh) is rejected. A candidate_flag is verified only by the kernel, never by
        proposing it. See the proposal_schema from ctf_observe."""
        try:
            return gw.ctf_propose(session_id, hypotheses, actions)
        except Exception as exc:  # noqa: BLE001
            return _err(exc)

    @mcp.tool()
    def ctf_step(session_id: str) -> dict:
        """Advance the agent by exactly one reasoning/execution step (delegates to AgentSession.step)."""
        try:
            return gw.ctf_step(session_id)
        except Exception as exc:  # noqa: BLE001
            return _err(exc)

    @mcp.tool()
    def ctf_run(session_id: str, max_steps: Optional[int] = None) -> dict:
        """Run the autonomous solver to a terminal state (delegates to AgentSession.run)."""
        try:
            return gw.ctf_run(session_id, max_steps)
        except Exception as exc:  # noqa: BLE001
            return _err(exc)

    @mcp.tool()
    def ctf_state(session_id: str) -> dict:
        """Read-only: current agent state (steps, hypotheses, evidence, verified)."""
        try:
            return gw.ctf_state(session_id)
        except Exception as exc:  # noqa: BLE001
            return _err(exc)

    @mcp.tool()
    def ctf_hypotheses(session_id: str) -> dict:
        """Read-only: current hypotheses with their fact states (never collapsed to DISPROVEN)."""
        try:
            return gw.ctf_hypotheses(session_id)
        except Exception as exc:  # noqa: BLE001
            return _err(exc)

    @mcp.tool()
    def ctf_evidence(session_id: str) -> dict:
        """Read-only: the evidence ledger for this session."""
        try:
            return gw.ctf_evidence(session_id)
        except Exception as exc:  # noqa: BLE001
            return _err(exc)

    @mcp.tool()
    def ctf_progress(session_id: str) -> dict:
        """Read-only: concise progress (phase, actions, budget, verification, lifecycle)."""
        try:
            return gw.ctf_progress(session_id)
        except Exception as exc:  # noqa: BLE001
            return _err(exc)

    @mcp.tool()
    def ctf_result(session_id: str) -> dict:
        """Read-only final result: distinguishes verified flag / candidate / none / blocked / failed."""
        try:
            return gw.ctf_result(session_id)
        except Exception as exc:  # noqa: BLE001
            return _err(exc)

    @mcp.tool()
    def ctf_writeup(session_id: str) -> dict:
        """Read-only: the grounded Markdown writeup generated after a SOLVED session (if learning is
        enabled and the writeup passed grounding validation). Never fabricates a flag: the flag is
        copied verbatim from the kernel-verified SolveResult. Empty when not available."""
        try:
            return gw.get_writeup(session_id)
        except Exception as exc:  # noqa: BLE001
            return _err(exc)

    @mcp.tool()
    def ctf_experience(session_id: str) -> dict:
        """Read-only: the derived experience record (success or failure) for a terminal session, if
        learning is enabled. Grounded in the authoritative SolveResult + journal; environmental/
        rate-limit/tool failures are recorded as such and never as technique disproof."""
        try:
            return gw.get_experience(session_id)
        except Exception as exc:  # noqa: BLE001
            return _err(exc)

    # -- minimal read-only diagnostics ---------------------------------------------------
    @mcp.tool()
    def ctf_sessions() -> dict:
        """Read-only diagnostic: list active session ids and lifecycle states."""
        try:
            return gw.ctf_sessions()
        except Exception as exc:  # noqa: BLE001
            return _err(exc)

    @mcp.tool()
    def ctf_trust_boundary() -> dict:
        """Read-only diagnostic: the tool-isolation classification (governed vs ungoverned surfaces)."""
        try:
            return gw.ctf_trust_boundary()
        except Exception as exc:  # noqa: BLE001
            return _err(exc)

    return mcp


def main() -> None:
    """Run the MCP server over stdio.

    NOTE: this is a stdio JSON-RPC server. It is meant to be launched by an MCP client (Kiro), which
    connects its stdin/stdout. Running it bare in a terminal will simply block waiting for MCP
    messages; on EOF/Ctrl-C it exits cleanly (no client == nothing to serve).
    """
    import sys

    if sys.stdin is not None and sys.stdin.isatty():
        sys.stderr.write(
            "[ctf-agent MCP] stdio server ready. This process speaks MCP JSON-RPC over stdin/stdout "
            "and is meant to be launched by an MCP client (Kiro), not run interactively.\n"
            "[ctf-agent MCP] Configure it in .kiro/settings/mcp.json (see .agent/kiro-mcp-config.example.json) "
            "or test it with: python scripts/mcp_stdio_smoke.py\n"
        )
        sys.stderr.flush()
    try:
        build_mcp().run()  # FastMCP default transport is stdio
    except (KeyboardInterrupt, EOFError):
        pass
    except BaseException as exc:  # anyio raises CancelledError on stdin close; exit quietly
        if exc.__class__.__name__ != "CancelledError":
            raise


if __name__ == "__main__":
    main()
