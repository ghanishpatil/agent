"""Data model for the external CTF writeup ingestion subsystem.

These types are the contract between ingestion stages. Everything is JSON-serialisable
(see ``to_dict``) so the knowledge store is a plain, auditable artifact. This package is
additive and is never imported by ``ctf_agent``; retrieval into the solver is a separate,
later, explicitly-approved step.

The central ambition (from the project brief) is to capture not merely
``challenge -> solution -> flag`` but the reasoning trajectory:

    challenge context -> observed clue -> candidate mechanisms -> hypothesis ->
    discriminating test -> observation -> interpretation -> hypothesis update ->
    next action -> exploit/solution -> verification

Extraction is heuristic. When a stage cannot be recovered it is simply absent or
low-confidence; nothing is fabricated.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Tuple

INGEST_SCHEMA_VERSION = "1.0"


class SourceType(str, Enum):
    LOCAL_DIRECTORY = "LOCAL_DIRECTORY"
    GIT_REPOSITORY = "GIT_REPOSITORY"
    HTTP = "HTTP"


class MediaType(str, Enum):
    MARKDOWN = "MARKDOWN"
    TEXT = "TEXT"
    HTML = "HTML"
    UNKNOWN = "UNKNOWN"


class TrajectoryStepKind(str, Enum):
    CHALLENGE_CONTEXT = "CHALLENGE_CONTEXT"
    OBSERVED_CLUE = "OBSERVED_CLUE"
    CANDIDATE_MECHANISM = "CANDIDATE_MECHANISM"
    HYPOTHESIS = "HYPOTHESIS"
    DISCRIMINATING_TEST = "DISCRIMINATING_TEST"
    OBSERVATION = "OBSERVATION"
    INTERPRETATION = "INTERPRETATION"
    HYPOTHESIS_UPDATE = "HYPOTHESIS_UPDATE"
    NEXT_ACTION = "NEXT_ACTION"
    EXPLOIT_SOLUTION = "EXPLOIT_SOLUTION"
    VERIFICATION = "VERIFICATION"


# Canonical ordering of the reasoning trajectory used for completeness scoring.
TRAJECTORY_ORDER: Tuple[TrajectoryStepKind, ...] = (
    TrajectoryStepKind.CHALLENGE_CONTEXT,
    TrajectoryStepKind.OBSERVED_CLUE,
    TrajectoryStepKind.CANDIDATE_MECHANISM,
    TrajectoryStepKind.HYPOTHESIS,
    TrajectoryStepKind.DISCRIMINATING_TEST,
    TrajectoryStepKind.OBSERVATION,
    TrajectoryStepKind.INTERPRETATION,
    TrajectoryStepKind.HYPOTHESIS_UPDATE,
    TrajectoryStepKind.NEXT_ACTION,
    TrajectoryStepKind.EXPLOIT_SOLUTION,
    TrajectoryStepKind.VERIFICATION,
)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(v) for v in value]
    return value


@dataclass(frozen=True)
class Provenance:
    """Where a document came from and how to attribute/verify it."""

    source_type: SourceType
    source_uri: str
    document_path: str = ""
    retrieved_at: str = ""
    revision: str = ""
    content_sha256: str = ""
    license_note: str = ""
    extra: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return _jsonable(asdict(self))


@dataclass(frozen=True)
class RawDocument:
    doc_id: str
    media_type: MediaType
    text: str
    provenance: Provenance
    byte_length: int = 0

    def to_dict(self) -> Dict[str, Any]:
        data = _jsonable(asdict(self))
        return data


@dataclass(frozen=True)
class WriteupSection:
    order: int
    heading: str
    level: int
    body: str

    def to_dict(self) -> Dict[str, Any]:
        return _jsonable(asdict(self))


@dataclass(frozen=True)
class NormalizedWriteup:
    doc_id: str
    title: str
    sections: Tuple[WriteupSection, ...]
    body_text: str
    provenance: Provenance
    normalized_sha256: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return _jsonable(asdict(self))


@dataclass(frozen=True)
class ChallengeMetadata:
    name: str = ""
    category: str = ""
    event: str = ""
    points: Optional[int] = None
    difficulty: str = ""
    flag_format: str = ""
    flags: Tuple[str, ...] = ()
    tags: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return _jsonable(asdict(self))


@dataclass(frozen=True)
class Technique:
    technique_id: str
    name: str
    category: str
    keywords: Tuple[str, ...] = ()
    confidence: float = 0.0
    evidence: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return _jsonable(asdict(self))


@dataclass(frozen=True)
class TrajectoryStep:
    order: int
    kind: TrajectoryStepKind
    text: str
    confidence: float = 0.0
    source_heading: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return _jsonable(asdict(self))


@dataclass(frozen=True)
class ReasoningTrajectory:
    steps: Tuple[TrajectoryStep, ...] = ()
    completeness: float = 0.0

    def kinds(self) -> Tuple[TrajectoryStepKind, ...]:
        return tuple(step.kind for step in self.steps)

    def to_dict(self) -> Dict[str, Any]:
        return _jsonable(asdict(self))


@dataclass(frozen=True)
class FailureCorrection:
    failed_approach: str
    failure_reason: str = ""
    correction: str = ""
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return _jsonable(asdict(self))


@dataclass(frozen=True)
class KnowledgeRecord:
    """One ingested, normalized, extracted writeup with provenance and dedup linkage."""

    record_id: str
    content_hash: str
    provenance: Provenance
    metadata: ChallengeMetadata
    techniques: Tuple[Technique, ...] = ()
    trajectory: ReasoningTrajectory = field(default_factory=ReasoningTrajectory)
    failures: Tuple[FailureCorrection, ...] = ()
    title: str = ""
    summary: str = ""
    schema_version: str = INGEST_SCHEMA_VERSION
    duplicate_of: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _jsonable(asdict(self))
