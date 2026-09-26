"""External CTF writeup ingestion subsystem.

Pipeline: crawler (sources) -> parser/normalize -> extraction (metadata, technique,
reasoning trajectory, failure/correction) -> deduplication -> provenance -> knowledge
store. Additive and standalone; ``ctf_agent`` does not import this package. Retrieval
into the frozen solver is a separate, later, explicitly-approved integration step.
"""

from __future__ import annotations

from .dedup import DedupDecision, Deduplicator, jaccard
from .models import (
    INGEST_SCHEMA_VERSION,
    ChallengeMetadata,
    FailureCorrection,
    KnowledgeRecord,
    MediaType,
    NormalizedWriteup,
    Provenance,
    RawDocument,
    ReasoningTrajectory,
    SourceType,
    Technique,
    TrajectoryStep,
    TrajectoryStepKind,
    WriteupSection,
)
from .normalize import normalize
from .pipeline import (
    IngestionPipeline,
    IngestReport,
    build_record,
    ingest_local_directory,
)
from .retrieval import (
    KnowledgeRetriever,
    RetrievalQuery,
    RetrievalResult,
    records_from_store,
)
from .advisory_projection import build_augmented_memory, write_external_memory
from .sources import (
    CachedHttpSource,
    GitRepositorySource,
    HttpSource,
    LocalDirectorySource,
    Source,
)
from .store import KnowledgeStore

__all__ = [
    "INGEST_SCHEMA_VERSION",
    "CachedHttpSource",
    "ChallengeMetadata",
    "DedupDecision",
    "Deduplicator",
    "FailureCorrection",
    "GitRepositorySource",
    "HttpSource",
    "IngestReport",
    "IngestionPipeline",
    "KnowledgeRecord",
    "KnowledgeRetriever",
    "KnowledgeStore",
    "LocalDirectorySource",
    "RetrievalQuery",
    "RetrievalResult",
    "build_augmented_memory",
    "records_from_store",
    "write_external_memory",
    "MediaType",
    "NormalizedWriteup",
    "Provenance",
    "RawDocument",
    "ReasoningTrajectory",
    "Source",
    "SourceType",
    "Technique",
    "TrajectoryStep",
    "TrajectoryStepKind",
    "WriteupSection",
    "build_record",
    "ingest_local_directory",
    "jaccard",
    "normalize",
]
