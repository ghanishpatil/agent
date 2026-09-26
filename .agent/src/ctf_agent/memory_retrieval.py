from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

from .failure_memory import FailureMatch, FailureMemory, FailureQuery
from .models import ResultClass


@dataclass(frozen=True)
class MemoryQuery:
    category: str = ""
    keywords: Tuple[str, ...] = ()
    result_class: ResultClass | None = None


@dataclass(frozen=True)
class TechniqueMatch:
    technique_id: str
    technique: str
    category: str
    confidence: str
    cheap_tests: Tuple[str, ...]
    discriminating_tests: Tuple[str, ...]
    indicators: Tuple[str, ...]
    source: str
    advisory_only: bool = True


@dataclass(frozen=True)
class ToolMatch:
    tool_id: str
    tool: str
    category: str
    availability: str
    when_to_use: str
    source: str
    advisory_only: bool = True


@dataclass(frozen=True)
class TrajectoryMatch:
    trajectory_id: str
    challenge: str
    category: str
    key_insight: str
    generalizes: str
    source: str
    advisory_only: bool = True


@dataclass(frozen=True)
class AdvisoryBundle:
    """Everything memory has to offer for one query. Every field is advisory_only.

    Nothing in this bundle can be handed to ``TrustKernel``, ``HypothesisBoard.record()``, or
    ``EvidenceManager``. It only feeds the planner's *ranking* of proposals it already built from
    current context; the bundle itself never becomes a hypothesis, an action, or evidence.
    """

    techniques: Tuple[TechniqueMatch, ...] = ()
    tools: Tuple[ToolMatch, ...] = ()
    trajectories: Tuple[TrajectoryMatch, ...] = ()
    failures: Tuple[FailureMatch, ...] = ()

    def is_empty(self) -> bool:
        return not (self.techniques or self.tools or self.trajectories or self.failures)


def _matches_query(corpus: str, category_field: str, query: MemoryQuery) -> bool:
    if not query.category and not query.keywords:
        return False
    if query.category and query.category.lower() != category_field.lower():
        if not query.keywords:
            return False
    text = corpus.lower()
    keyword_hit = any(keyword.lower() in text for keyword in query.keywords)
    category_hit = query.category and query.category.lower() == category_field.lower()
    return keyword_hit or category_hit


class AdvisoryMemory:
    """Lazy, read-only retrieval over the Phase 1 `.agent_audit` corpus.

    Loading is lazy per-source so an empty/never-queried memory never bulk-parses everything.
    Retrieval is deterministic keyword/category matching -- no embeddings, no vector index.
    """

    def __init__(self, audit_root: Path) -> None:
        self._audit_root = audit_root
        self._techniques: Tuple[dict, ...] | None = None
        self._tools: Tuple[dict, ...] | None = None
        self._trajectories: Tuple[dict, ...] | None = None
        self._failure_memory: FailureMemory | None = None

    def retrieve(self, query: MemoryQuery) -> AdvisoryBundle:
        if not query.category and not query.keywords and query.result_class is None:
            return AdvisoryBundle()
        return AdvisoryBundle(
            techniques=self._match_techniques(query),
            tools=self._match_tools(query),
            trajectories=self._match_trajectories(query),
            failures=self._match_failures(query),
        )

    def _load_jsonl(self, relative: str) -> Tuple[dict, ...]:
        path = self._audit_root / relative
        if not path.exists():
            return ()
        records = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
        return tuple(records)

    def _techniques_data(self) -> Tuple[dict, ...]:
        if self._techniques is None:
            self._techniques = self._load_jsonl("knowledge/technique_memory.jsonl")
        return self._techniques

    def _tools_data(self) -> Tuple[dict, ...]:
        if self._tools is None:
            self._tools = self._load_jsonl("tools/tool_memory.jsonl")
        return self._tools

    def _trajectories_data(self) -> Tuple[dict, ...]:
        if self._trajectories is None:
            self._trajectories = self._load_jsonl("trajectories/trajectories.jsonl")
        return self._trajectories

    def _failure_memory_data(self) -> FailureMemory | None:
        if self._failure_memory is None:
            path = self._audit_root / "failures" / "failures.jsonl"
            if not path.exists():
                return None
            self._failure_memory = FailureMemory.from_jsonl(path)
        return self._failure_memory

    def _match_techniques(self, query: MemoryQuery) -> Tuple[TechniqueMatch, ...]:
        matches = []
        for record in self._techniques_data():
            corpus = " ".join(
                (record.get("technique", ""), *record.get("indicators", []))
            )
            if _matches_query(corpus, record.get("category", ""), query):
                matches.append(
                    TechniqueMatch(
                        technique_id=record["id"],
                        technique=record["technique"],
                        category=record.get("category", ""),
                        confidence=record.get("confidence", ""),
                        cheap_tests=tuple(record.get("cheap_tests", [])),
                        discriminating_tests=tuple(record.get("discriminating_tests", [])),
                        indicators=tuple(record.get("indicators", [])),
                        source=str(record.get("examples", [""])[0]) if record.get("examples") else "",
                    )
                )
        return tuple(matches)

    def _match_tools(self, query: MemoryQuery) -> Tuple[ToolMatch, ...]:
        matches = []
        for record in self._tools_data():
            corpus = " ".join((record.get("tool", ""), record.get("purpose", "")))
            if _matches_query(corpus, record.get("category", ""), query):
                matches.append(
                    ToolMatch(
                        tool_id=record["id"],
                        tool=record["tool"],
                        category=record.get("category", ""),
                        availability=record.get("availability", ""),
                        when_to_use=record.get("when_to_use", ""),
                        source=record.get("purpose", ""),
                    )
                )
        return tuple(matches)

    def _match_trajectories(self, query: MemoryQuery) -> Tuple[TrajectoryMatch, ...]:
        matches = []
        for record in self._trajectories_data():
            corpus = " ".join(
                (
                    record.get("challenge", ""),
                    record.get("key_insight", ""),
                    record.get("generalizes", ""),
                )
            )
            if _matches_query(corpus, record.get("category", ""), query):
                matches.append(
                    TrajectoryMatch(
                        trajectory_id=record["id"],
                        challenge=record.get("challenge", ""),
                        category=record.get("category", ""),
                        key_insight=record.get("key_insight", ""),
                        generalizes=record.get("generalizes", ""),
                        source=record.get("source", ""),
                    )
                )
        return tuple(matches)

    def _match_failures(self, query: MemoryQuery) -> Tuple[FailureMatch, ...]:
        memory = self._failure_memory_data()
        if memory is None:
            return ()
        return memory.retrieve_relevant_failures(
            FailureQuery(
                category=query.category or None,
                result_class=query.result_class,
                keywords=query.keywords,
            )
        )
