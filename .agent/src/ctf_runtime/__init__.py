"""ctf_runtime — the production runtime bridge that makes the frozen ctf_agent the authority for
real CTF solving.

This package is ADDITIVE. It never modifies ctf_agent; it composes the frozen pipeline (via the
frozen ``solve()`` helper functions) and substitutes only the reasoning source with an
``LLMReasoningSource``. The external model can only emit typed proposals; the frozen kernel/planner/
adapters/verification retain all authority.
"""

from __future__ import annotations

from .journal import RuntimeSessionJournal
from .kiro_bridge import KiroBridge
from .mcp_gateway import (
    CtfAgentGateway,
    GatewayError,
    UnknownSession,
    ValidationError,
)
from .llm_client import (
    CallableLLMClient,
    FakeLLMClient,
    LLMClient,
    LLMRequest,
    LLMResponse,
    ScriptedLLMClient,
)
from .kiro_driven import KiroDrivenController, QueuedReasoningSource
from .experience_store import (
    EXPERIENCE_SCHEMA_VERSION,
    SOURCE_FAILURE,
    SOURCE_SUCCESS,
    ExperienceProvenance,
    ExperienceRecord,
    ExperienceStore,
)
from .experience import extract_failure_experience, extract_success_experience
from .writeup import WriteupResult, generate_writeup, validate_writeup
from .learning import PostTerminalObserver
from .reasoning_source import LLMReasoningSource
from .real_environment import (
    AllowedExecutable,
    OperatorPolicy,
    build_operator_environment,
    build_operator_gateway,
)
from .tcp_adapter import (
    TCP_TOOL_NAME,
    InteractiveTcpAdapter,
    ServiceTranscriptVerifier,
    TcpDestination,
)
from .routing import ModelRouter, ModelTier, RouteDecision, RoutingSignals, TIER_MODELS
from .session import AgentSession, StepReport
from .smoke import RealChallengeSpec, prepare_real_session
from .tool_isolation import SURFACES, SurfaceClass, classification, ungoverned_surfaces

__all__ = [
    "AgentSession",
    "StepReport",
    "KiroBridge",
    "CtfAgentGateway",
    "GatewayError",
    "UnknownSession",
    "ValidationError",
    "LLMReasoningSource",
    "KiroDrivenController",
    "QueuedReasoningSource",
    "ExperienceStore",
    "ExperienceRecord",
    "ExperienceProvenance",
    "SOURCE_SUCCESS",
    "SOURCE_FAILURE",
    "EXPERIENCE_SCHEMA_VERSION",
    "extract_success_experience",
    "extract_failure_experience",
    "WriteupResult",
    "generate_writeup",
    "validate_writeup",
    "PostTerminalObserver",
    "OperatorPolicy",
    "AllowedExecutable",
    "build_operator_environment",
    "build_operator_gateway",
    "InteractiveTcpAdapter",
    "ServiceTranscriptVerifier",
    "TcpDestination",
    "TCP_TOOL_NAME",
    "LLMClient",
    "LLMRequest",
    "LLMResponse",
    "CallableLLMClient",
    "ScriptedLLMClient",
    "FakeLLMClient",
    "ModelRouter",
    "ModelTier",
    "RouteDecision",
    "RoutingSignals",
    "TIER_MODELS",
    "RuntimeSessionJournal",
    "RealChallengeSpec",
    "prepare_real_session",
    "SURFACES",
    "SurfaceClass",
    "classification",
    "ungoverned_surfaces",
]
