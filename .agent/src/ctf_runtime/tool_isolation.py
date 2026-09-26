"""Tool isolation — classification of every direct CTF execution surface (Step 4).

This module DELETES NOTHING. It records which execution surfaces exist and how each relates to the
agent's trust boundary, so the runtime bridge can state precisely what is governed and what is not.

The invariant: the agent OWNS execution. The only sanctioned way to execute a CTF action inside a
runtime session is through a trusted ``ToolAdapter`` registered in the agent's ``AdapterRegistry``
and driven by ``ReasoningLoop`` -> ``TrustKernel``. Every other surface is UNGOVERNED and must not be
used to solve a challenge while an ``AgentSession`` is active; where a capability is genuinely needed,
it must be wrapped as a trusted adapter (fixed executable, args-only, classified output) and added to
``EnvironmentConfig.permitted_tools``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class SurfaceClass(str, Enum):
    TRUSTED_ADAPTER = "TRUSTED_ADAPTER"        # governed by the agent (AdapterRegistry + kernel)
    DIRECT_UNGOVERNED = "DIRECT_UNGOVERNED"    # bypasses the agent; must not solve during a session
    WRAPPABLE = "WRAPPABLE"                     # could be exposed only via a trusted adapter


@dataclass(frozen=True)
class ExecutionSurface:
    name: str
    location: str
    classification: SurfaceClass
    rationale: str
    disposition: str


# The known execution surfaces in this repository, classified. Data only — nothing is invoked here.
SURFACES: Tuple[ExecutionSurface, ...] = (
    ExecutionSurface(
        name="Kiro execute_pwsh",
        location="IDE tool surface (outside .agent)",
        classification=SurfaceClass.DIRECT_UNGOVERNED,
        rationale="Arbitrary shell; no allowlist, no fingerprinting, no result classification, "
                  "no evidence binding. This is the surface the AGENT_BYPASSED audit identified.",
        disposition="Do NOT use to solve a challenge while an AgentSession is active. Reserve for "
                     "operator setup only (installing tools, preparing files).",
    ),
    ExecutionSurface(
        name="hexstrike-ai MCP",
        location="hexstrike-ai/hexstrike-ai-mcp.json (MCP server on :8888)",
        classification=SurfaceClass.DIRECT_UNGOVERNED,
        rationale="Autonomous cybersecurity automation server; direct tool execution not routed "
                  "through the agent's kernel/adapters.",
        disposition="Leave in place; do not connect for solving. If a specific capability is needed, "
                     "wrap it as a trusted ToolAdapter.",
    ),
    ExecutionSurface(
        name="ctf_solver_mcp",
        location="ctf_solver_mcp/ (MCP server package)",
        classification=SurfaceClass.DIRECT_UNGOVERNED,
        rationale="Separate MCP solver; ungoverned by the trust kernel.",
        disposition="Leave in place; not used by the runtime bridge.",
    ),
    ExecutionSurface(
        name="ctf_toolkit.py",
        location="hexstrike-ai/ctf_toolkit.py",
        classification=SurfaceClass.WRAPPABLE,
        rationale="A library of CTF helpers; individual pure functions could be wrapped as trusted "
                  "adapters (fixed behavior, classified output) if needed.",
        disposition="Do not import for direct execution during a session; wrap-if-needed only.",
    ),
    ExecutionSurface(
        name="raw subprocess / network / browser",
        location="anywhere outside ctf_agent.adapters",
        classification=SurfaceClass.DIRECT_UNGOVERNED,
        rationale="Any direct subprocess/HTTP/browser call bypasses fingerprinting, classification, "
                  "evidence binding, and verification.",
        disposition="Forbidden as a solving path during a session; use trusted adapters.",
    ),
    ExecutionSurface(
        name="ctf_agent trusted adapters",
        location="ctf_agent/adapters/{subprocess,http,file}_adapter.py via AdapterRegistry",
        classification=SurfaceClass.TRUSTED_ADAPTER,
        rationale="The ONLY sanctioned execution path: fixed/allowlisted, args-only, output flows "
                  "through the Result Classifier -> Evidence -> Impact -> Verification pipeline.",
        disposition="This is where execution belongs. Register needed tools in "
                     "EnvironmentConfig.permitted_tools.",
    ),
)


def classification() -> dict:
    """A serializable view of the tool-isolation classification."""
    return {
        "invariant": "The agent owns execution; the LLM may only propose typed suggestions.",
        "sanctioned_execution_path": "ReasoningLoop -> AdapterRegistry (trusted ToolAdapter) -> "
                                     "TrustKernel (classify -> evidence -> impact -> verify).",
        "surfaces": [
            {
                "name": s.name,
                "location": s.location,
                "classification": s.classification.value,
                "rationale": s.rationale,
                "disposition": s.disposition,
            }
            for s in SURFACES
        ],
    }


def ungoverned_surfaces() -> Tuple[str, ...]:
    return tuple(s.name for s in SURFACES if s.classification is SurfaceClass.DIRECT_UNGOVERNED)
