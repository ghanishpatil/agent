from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Mapping, Optional, Tuple


class StringEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class ResultClass(StringEnum):
    SUCCESS = "SUCCESS"
    TARGET_RESPONSE = "TARGET_RESPONSE"
    INPUT_REJECTION = "INPUT_REJECTION"
    AUTH_FAILURE = "AUTH_FAILURE"
    AUTHZ_FAILURE = "AUTHZ_FAILURE"
    RATE_LIMIT = "RATE_LIMIT"
    TIMEOUT = "TIMEOUT"
    NETWORK_FAILURE = "NETWORK_FAILURE"
    TOOL_FAILURE = "TOOL_FAILURE"
    ENVIRONMENT_FAILURE = "ENVIRONMENT_FAILURE"
    STATE_CHANGE = "STATE_CHANGE"
    AMBIGUOUS = "AMBIGUOUS"


class HypothesisImpact(StringEnum):
    SUPPORTS = "SUPPORTS"
    WEAKENS = "WEAKENS"
    DISPROVES = "DISPROVES"
    UNRESOLVES = "UNRESOLVES"
    BLOCKS_TEST = "BLOCKS_TEST"
    NO_IMPACT = "NO_IMPACT"


class HypothesisStatus(StringEnum):
    OPEN = "OPEN"
    SUPPORTED = "SUPPORTED"
    DISPROVEN = "DISPROVEN"
    UNRESOLVED = "UNRESOLVED"


class EvidenceStatus(StringEnum):
    VERIFIED = "VERIFIED"
    SUPPORTED = "SUPPORTED"
    PLAUSIBLE = "PLAUSIBLE"
    UNRESOLVED = "UNRESOLVED"
    DISPROVEN = "DISPROVEN"
    BLOCKED = "BLOCKED"
    ENVIRONMENTAL_FAILURE = "ENVIRONMENTAL_FAILURE"
    TOOL_FAILURE = "TOOL_FAILURE"


class EvidenceOrigin(StringEnum):
    CURRENT_OBSERVATION = "CURRENT_OBSERVATION"
    HISTORICAL_MEMORY = "HISTORICAL_MEMORY"


class Freshness(StringEnum):
    CURRENT = "CURRENT"
    STALE = "STALE"


class MemoryConfidence(StringEnum):
    VERIFIED = "VERIFIED"
    SUPPORTED = "SUPPORTED"
    PLAUSIBLE = "PLAUSIBLE"
    HISTORICAL = "HISTORICAL"
    CHALLENGE_SPECIFIC = "CHALLENGE_SPECIFIC"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"


class VerificationStatus(StringEnum):
    CANDIDATE = "CANDIDATE"
    SUPPORTED = "SUPPORTED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    INVALID = "INVALID"


class VerificationMethod(StringEnum):
    AUTHORITATIVE_VERIFIER = "AUTHORITATIVE_VERIFIER"
    AUTHORITATIVE_OUTPUT = "AUTHORITATIVE_OUTPUT"
    DETERMINISTIC_DERIVATION = "DETERMINISTIC_DERIVATION"
    CRYPTOGRAPHIC_PROOF = "CRYPTOGRAPHIC_PROOF"
    GRADING_LOGIC = "GRADING_LOGIC"
    CHALLENGE_SPECIFIC_SELF_CHECK = "CHALLENGE_SPECIFIC_SELF_CHECK"
    SUPPORTING_ANALYSIS = "SUPPORTING_ANALYSIS"
    REGEX_MATCH = "REGEX_MATCH"
    READABLE_TEXT = "READABLE_TEXT"
    WEAK_CHECKER_COLLISION = "WEAK_CHECKER_COLLISION"
    MODEL_SUGGESTION = "MODEL_SUGGESTION"


class ControlDecision(StringEnum):
    ALLOWED = "ALLOWED"
    DUPLICATE = "DUPLICATE"
    CONTINUE = "CONTINUE"
    STOP = "STOP"


@dataclass(frozen=True)
class ExecutionResult:
    action_id: str
    tool: str
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    http_status: Optional[int] = None
    response_headers: Mapping[str, str] = field(default_factory=dict)
    response_body: str = ""
    timed_out: bool = False
    process_state: Optional[str] = None
    network_state: Optional[str] = None
    tool_available: Optional[bool] = None
    environment_available: Optional[bool] = None
    input_rejected: bool = False
    state_changed: bool = False
    authoritative_success: bool = False
    duration_ms: Optional[int] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ResultClassification:
    result_class: ResultClass
    rationale: str
    matched_fields: Tuple[str, ...]


@dataclass(frozen=True)
class ImpactContext:
    hypothesis_id: str
    prerequisites_met: bool = True
    valid_discriminating_test: bool = False
    authoritative_observation: bool = False
    expected_observation_seen: bool = False
    contradiction_observed: bool = False
    test_inconclusive: bool = False
    observation_available: bool = True


@dataclass(frozen=True)
class TestSpecification:
    __test__ = False

    hypothesis_id: str
    supporting_body_contains: Tuple[str, ...] = ()
    contradicting_body_contains: Tuple[str, ...] = ()
    authoritative_sources: Tuple[str, ...] = ()
    prerequisites_met: bool = True


@dataclass(frozen=True)
class EnvironmentState:
    revision: str
    available_tools: Tuple[str, ...] = ()
    network_available: Optional[bool] = None


@dataclass(frozen=True)
class RelevantState:
    environment: EnvironmentState
    authentication_context: str
    session_context: str
    challenge_revision: str


@dataclass(frozen=True)
class ChallengeState:
    challenge_id: str
    name: str
    grading_model: str = "unknown"
    attempts_remaining: Optional[int] = None
    revision: str = "initial"


@dataclass(frozen=True)
class Action:
    action_id: str
    objective: str
    tool: str
    target: str
    input_data: Any
    relevant_parameters: Mapping[str, Any]
    prerequisites: Tuple[str, ...]
    state_before: RelevantState
    state_after: Optional[RelevantState] = None
    execution_metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Observation:
    observation_id: str
    action_id: str
    timestamp: datetime
    source: str
    execution: ExecutionResult


@dataclass(frozen=True)
class Provenance:
    origin: EvidenceOrigin
    locator: str
    recorded_by: str = "ctf-agent-trust-kernel"


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    action_id: str
    timestamp: datetime
    source: str
    observation: Observation
    result_class: ResultClass
    status: EvidenceStatus
    strength: float
    affected_hypotheses: Tuple[str, ...]
    freshness: Freshness
    provenance: Provenance


@dataclass(frozen=True)
class Hypothesis:
    hypothesis_id: str
    statement: str
    status: HypothesisStatus = HypothesisStatus.OPEN
    supporting_evidence: Tuple[str, ...] = ()
    contradicting_evidence: Tuple[str, ...] = ()
    unresolved_evidence: Tuple[str, ...] = ()
    last_updated: Optional[datetime] = None


@dataclass(frozen=True)
class VerificationPolicy:
    authoritative_output_tools: Tuple[str, ...] = ()
    verifier_tools: Tuple[str, ...] = ()
    deterministic_tools: Tuple[str, ...] = ()


@dataclass(frozen=True)
class VerificationEvidence:
    evidence_id: str
    method: VerificationMethod
    summary: str
    provenance: str
    accepted: bool
    challenge_relevant: bool
    timestamp: datetime


@dataclass(frozen=True)
class FlagAttempt:
    value: str
    verifier: str
    evidence_ids: Tuple[str, ...]
    state_digest: str
    attempted_at: datetime
    source: str = ""


@dataclass(frozen=True)
class FlagCandidate:
    value: str
    source: str
    supporting_evidence: Tuple[str, ...] = field(default=(), init=False)
    verification_status: VerificationStatus = field(
        default=VerificationStatus.CANDIDATE, init=False
    )
    attempts: Tuple[FlagAttempt, ...] = field(default=(), init=False)
    verified_at: Optional[datetime] = field(default=None, init=False)
    rejection_reason: Optional[str] = field(default=None, init=False)


@dataclass(frozen=True)
class VerificationState:
    candidates: Tuple[FlagCandidate, ...] = ()
    decision: ControlDecision = ControlDecision.CONTINUE


@dataclass(frozen=True)
class VerificationDecision:
    candidate: FlagCandidate
    decision: ControlDecision
    reason: str
