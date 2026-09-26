from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .models import (
    EvidenceOrigin,
    HypothesisImpact,
    MemoryConfidence,
    Provenance,
    ResultClass,
)


_CAUSE_ALIASES = {
    "AUTH": "AUTH_FAILURE",
    "AUTHZ": "AUTHZ_FAILURE",
    "NETWORK": "NETWORK_FAILURE",
    "ENV_FAILURE": "ENVIRONMENT_FAILURE",
}


@dataclass(frozen=True)
class FailureRecord:
    failure_id: str
    challenge: str
    category: str
    action: str
    observation: str
    initial_interpretation: str
    correct_interpretation: str
    root_causes: tuple[str, ...]
    diagnostic_evidence: str
    hypothesis_update_narrative: str
    recovery: Optional[str]
    lesson: str
    confidence: MemoryConfidence
    source: str
    last_verified: Optional[datetime]
    provenance: Provenance
    raw: Mapping[str, Any]
    result_class: Optional[ResultClass] = None
    hypothesis_impact: Optional[HypothesisImpact] = None


@dataclass(frozen=True)
class FailureQuery:
    category: Optional[str] = None
    result_class: Optional[ResultClass] = None
    keywords: tuple[str, ...] = ()


@dataclass(frozen=True)
class FailureMatch:
    record: FailureRecord
    relevance_reasons: tuple[str, ...]
    advisory_only: bool = True


class FailureMemory:
    def __init__(self, records: tuple[FailureRecord, ...]) -> None:
        self.records = records

    @classmethod
    def from_jsonl(cls, path: Path) -> "FailureMemory":
        records: list[FailureRecord] = []
        with path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                raw = json.loads(line)
                required = {
                    "id", "challenge", "category", "failed_action", "observed_result",
                    "initial_interpretation", "correct_diagnosis", "cause", "evidence",
                    "correct_hypothesis_update", "lesson", "source",
                }
                missing = required.difference(raw)
                if missing:
                    raise ValueError(f"{path}:{line_number} missing fields: {sorted(missing)}")
                causes = tuple(_CAUSE_ALIASES.get(item, item) for item in raw["cause"])
                records.append(
                    FailureRecord(
                        failure_id=raw["id"],
                        challenge=raw["challenge"],
                        category=raw["category"],
                        action=raw["failed_action"],
                        observation=raw["observed_result"],
                        initial_interpretation=raw["initial_interpretation"],
                        correct_interpretation=raw["correct_diagnosis"],
                        root_causes=causes,
                        diagnostic_evidence=raw["evidence"],
                        hypothesis_update_narrative=raw["correct_hypothesis_update"],
                        recovery=raw.get("recovery"),
                        lesson=raw["lesson"],
                        confidence=MemoryConfidence.HISTORICAL,
                        source=raw["source"],
                        last_verified=None,
                        provenance=Provenance(
                            EvidenceOrigin.HISTORICAL_MEMORY,
                            f"{path.as_posix()}:{line_number}#{raw['id']}",
                            "failure-memory-loader-v1",
                        ),
                        raw=MappingProxyType(dict(raw)),
                    )
                )
        return cls(tuple(records))

    def retrieve_relevant_failures(self, query: FailureQuery) -> tuple[FailureMatch, ...]:
        if query.category is None and query.result_class is None and not query.keywords:
            return ()
        matches: list[tuple[int, FailureMatch]] = []
        for record in self.records:
            score = 0
            reasons: list[str] = []
            if query.category and record.category.lower() == query.category.lower():
                score += 2
                reasons.append(f"category={query.category}")
            if query.result_class and query.result_class.value in record.root_causes:
                score += 3
                reasons.append(f"failure_class={query.result_class.value}")
            corpus = " ".join(
                (
                    record.challenge,
                    record.action,
                    record.observation,
                    record.correct_interpretation,
                    record.lesson,
                )
            ).lower()
            for keyword in query.keywords:
                if keyword.lower() in corpus:
                    score += 1
                    reasons.append(f"keyword={keyword.lower()}")
            if score:
                matches.append((score, FailureMatch(record, tuple(reasons))))
        matches.sort(key=lambda item: (-item[0], item[1].record.failure_id))
        return tuple(match for _, match in matches)


    def append(self, record: FailureRecord, path: Path) -> None:
        """Append one normalized runtime failure; Phase 1 audit data is always read-only."""
        if ".agent_audit" in path.parts:
            raise ValueError("Phase 1 audit memory is read-only")
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "failure_id": record.failure_id,
            "challenge": record.challenge,
            "category": record.category,
            "action": record.action,
            "observation": record.observation,
            "result_class": record.result_class.value if record.result_class else None,
            "initial_interpretation": record.initial_interpretation,
            "correct_interpretation": record.correct_interpretation,
            "root_causes": list(record.root_causes),
            "hypothesis_impact": (
                record.hypothesis_impact.value if record.hypothesis_impact else None
            ),
            "recovery": record.recovery,
            "lesson": record.lesson,
            "confidence": record.confidence.value,
            "source": record.source,
            "last_verified": (
                record.last_verified.isoformat() if record.last_verified else None
            ),
            "provenance": record.provenance.locator,
        }
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(payload, sort_keys=True, ensure_ascii=False) + "\n")
