from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Tuple

from ..models import RelevantState, VerificationPolicy


class InputFactState(str, Enum):
    """Epistemic state for challenge-package fields, separate from trusted evidence state."""

    KNOWN = "KNOWN"
    UNKNOWN = "UNKNOWN"
    ASSUMED = "ASSUMED"
    INFERRED = "INFERRED"
    VERIFIED = "VERIFIED"


class ResourceKind(str, Enum):
    FILE = "FILE"
    SOURCE = "SOURCE"
    BINARY = "BINARY"
    ARCHIVE = "ARCHIVE"
    IMAGE = "IMAGE"
    PCAP = "PCAP"
    APK = "APK"
    DOCUMENT = "DOCUMENT"


class SolveStatus(str, Enum):
    SOLVED = "SOLVED"
    BLOCKED = "BLOCKED"
    EXHAUSTED = "EXHAUSTED"
    FAILED = "FAILED"
    INVALID_INPUT = "INVALID_INPUT"
    TIMEOUT = "TIMEOUT"


class KnowledgeSource(str, Enum):
    DIRECT_MECHANISM_REASONING = "DIRECT_MECHANISM_REASONING"
    EXISTING_MEMORY = "EXISTING_MEMORY"
    SPECIALIST_KNOWLEDGE = "SPECIALIST_KNOWLEDGE"
    CHALLENGE_ARTIFACT = "CHALLENGE_ARTIFACT"
    KNOWN_TECHNIQUE = "KNOWN_TECHNIQUE"
    ANALOGY = "ANALOGY"


@dataclass(frozen=True)
class InputFact:
    name: str
    value: Any
    state: InputFactState
    origin: str


@dataclass(frozen=True)
class ChallengeUnderstanding:
    facts: Tuple[InputFact, ...]
    likely_categories: Tuple[str, ...]
    attack_surfaces: Tuple[str, ...]
    unknowns: Tuple[str, ...]
    constraints: Tuple[str, ...]

    def fact(self, name: str) -> InputFact:
        for item in self.facts:
            if item.name == name:
                return item
        raise KeyError(name)


@dataclass(frozen=True)
class ChallengeInput:
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    points: Optional[int] = None
    solves: Optional[int] = None
    hints: Tuple[str, ...] = ()
    flag_format: Optional[str] = None
    urls: Tuple[str, ...] = ()
    credentials: Mapping[str, str] = field(default_factory=dict)
    attempt_limit: Optional[int] = None
    known_constraints: Tuple[str, ...] = ()
    revision: str = "initial"


@dataclass(frozen=True)
class ChallengeResource:
    resource_id: str
    kind: ResourceKind
    path: Optional[Path] = None
    content: bytes | str | None = None
    filename: str = ""
    media_type: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PermittedTool:
    """One explicitly permitted Phase 3 adapter plus accounting/trust metadata."""

    name: str
    adapter: object
    authoritative_sources: Tuple[str, ...] = ()
    authoritative_output: bool = False
    verifier: bool = False
    deterministic: bool = False
    network: bool = False
    remote: bool = False
    destructive: bool = False
    cost: int = 1


@dataclass(frozen=True)
class EvidenceRule:
    hypothesis_id: str
    supporting_body_contains: Tuple[str, ...] = ()
    contradicting_body_contains: Tuple[str, ...] = ()
    authoritative_sources: Tuple[str, ...] = ()
    prerequisites_met: bool = True


@dataclass(frozen=True)
class CandidateVerifierRoute:
    """Optional explicit hard-verifier route for candidate submissions.

    Phase 5 may rewrite a specialist's inert submit proposal to this permitted tool/target, but the
    candidate still needs prior bound evidence and Phase 2 performs the acceptance decision.
    """

    tool: str
    target: str
    method: str = "POST"
    input_field: str = "flag"
    relevant_parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EnvironmentConfig:
    permitted_tools: Tuple[PermittedTool, ...] = ()
    evidence_rules: Tuple[EvidenceRule, ...] = ()
    verifier_route: Optional[CandidateVerifierRoute] = None
    verification_policy: Optional[VerificationPolicy] = None
    initial_state: Optional[RelevantState] = None
    satisfied_prerequisites: Tuple[str, ...] = ()
    memory_root: Optional[Path] = None
    workspace_root: Optional[Path] = None
    journal_path: Optional[Path] = None
    run_id: str = ""
    model_configuration: str = "deterministic-specialist-brain"
    clock: Optional[Callable[[], datetime]] = None
    monotonic: Optional[Callable[[], float]] = None


@dataclass(frozen=True)
class SolveConstraints:
    max_actions: int = 20
    max_iterations: int = 20
    max_tool_executions: int = 20
    max_network_actions: int = 10
    max_remote_attempts: int = 10
    max_submissions: int = 3
    max_expensive_actions: int = 5
    max_specialist_calls: int = 40
    max_total_cost: int = 50
    timeout_seconds: float = 30.0


@dataclass(frozen=True)
class BudgetUsage:
    iterations: int = 0
    total_actions: int = 0
    tool_executions: int = 0
    network_actions: int = 0
    remote_attempts: int = 0
    submissions: int = 0
    expensive_actions: int = 0
    specialist_calls: int = 0
    total_cost: int = 0
    blind_retries: int = 0
    duplicate_proposals: int = 0
    budget_violations: int = 0


@dataclass(frozen=True)
class ActionTrace:
    action_id: str
    objective: str
    tool: str
    target: str
    result_class: str
    impact: str
    decision: str
    cost: int


@dataclass(frozen=True)
class EvidenceTrace:
    evidence_id: str
    source: str
    result_class: str
    status: str
    affected_hypotheses: Tuple[str, ...]
    provenance: str


@dataclass(frozen=True)
class HypothesisTrace:
    hypothesis_id: str
    statement: str
    status: str
    supporting_evidence: Tuple[str, ...]
    conflicting_evidence: Tuple[str, ...]
    unresolved_evidence: Tuple[str, ...]
    priority: int


@dataclass(frozen=True)
class SpecialistContribution:
    specialist: str
    relevance: float
    hypotheses: Tuple[str, ...]
    proposed_actions: Tuple[str, ...]
    memory_references: Tuple[str, ...]
    reasoning_summary: str


@dataclass(frozen=True)
class SolveResult:
    status: SolveStatus
    run_id: str
    challenge_name: str
    understanding: ChallengeUnderstanding
    terminal_reason: str
    verified_flag: Optional[str] = None
    verification_evidence_ids: Tuple[str, ...] = ()
    final_verification_method: Optional[str] = None
    solution_path_summary: str = ""
    actions: Tuple[ActionTrace, ...] = ()
    key_hypotheses: Tuple[HypothesisTrace, ...] = ()
    specialist_contributions: Tuple[SpecialistContribution, ...] = ()
    important_evidence: Tuple[EvidenceTrace, ...] = ()
    remaining_hypotheses: Tuple[str, ...] = ()
    unresolved_blockers: Tuple[str, ...] = ()
    budget_usage: BudgetUsage = field(default_factory=BudgetUsage)
    knowledge_sources: Tuple[KnowledgeSource, ...] = ()
    reasoning_iterations: int = 0
    duration_ms: int = 0
    journal_path: str = ""

    def __post_init__(self) -> None:
        if self.status is SolveStatus.SOLVED:
            if not self.verified_flag:
                raise ValueError("SOLVED requires a verified flag")
            if not self.verification_evidence_ids:
                raise ValueError("SOLVED requires verification evidence")
            if not self.final_verification_method:
                raise ValueError("SOLVED requires a verification method")
        elif self.verified_flag is not None:
            raise ValueError("non-SOLVED results must not contain a flag")
