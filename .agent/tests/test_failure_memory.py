from __future__ import annotations

import json
from pathlib import Path

import pytest

from ctf_agent.failure_memory import FailureMemory, FailureQuery
from ctf_agent.models import MemoryConfidence, ResultClass


AUDIT_FAILURES = Path(__file__).parents[2] / ".agent_audit" / "failures" / "failures.jsonl"


def test_historical_failure_memory_loads_all_records_without_rewriting_source() -> None:
    before = AUDIT_FAILURES.read_bytes()
    memory = FailureMemory.from_jsonl(AUDIT_FAILURES)
    assert len(memory.records) == 12
    assert AUDIT_FAILURES.read_bytes() == before
    assert all(record.confidence is MemoryConfidence.HISTORICAL for record in memory.records)
    assert all(record.last_verified is None for record in memory.records)
    assert all(record.provenance.locator for record in memory.records)
    assert memory.records[0].raw["id"] == "FAIL-001"
    assert next(record for record in memory.records if record.failure_id == "FAIL-012").recovery is None


def test_failure_retrieval_returns_advisory_matches_with_traceability() -> None:
    memory = FailureMemory.from_jsonl(AUDIT_FAILURES)
    matches = memory.retrieve_relevant_failures(
        FailureQuery(
            category="web",
            result_class=ResultClass.RATE_LIMIT,
            keywords=("sql", "timing", "rate"),
        )
    )
    assert matches
    assert any(match.record.failure_id in {"FAIL-005", "FAIL-012"} for match in matches)
    assert all(match.advisory_only for match in matches)
    assert all(match.record.source for match in matches)
    assert all(match.relevance_reasons for match in matches)


def test_empty_query_does_not_dump_all_memory() -> None:
    memory = FailureMemory.from_jsonl(AUDIT_FAILURES)
    assert memory.retrieve_relevant_failures(FailureQuery()) == ()


def test_runtime_failure_memory_appends_without_overwriting(tmp_path: Path) -> None:
    memory = FailureMemory.from_jsonl(AUDIT_FAILURES)
    runtime_path = tmp_path / "failures.jsonl"
    runtime_path.write_text('{"existing":"record"}\n', encoding="utf-8")
    before = runtime_path.read_text(encoding="utf-8")
    memory.append(memory.records[0], runtime_path)
    after = runtime_path.read_text(encoding="utf-8")
    assert after.startswith(before)
    appended = json.loads(after.splitlines()[-1])
    assert appended["failure_id"] == "FAIL-001"
    assert appended["confidence"] == "HISTORICAL"
    assert appended["provenance"]


def test_runtime_append_refuses_to_write_into_phase_one_audit() -> None:
    memory = FailureMemory.from_jsonl(AUDIT_FAILURES)
    with pytest.raises(ValueError, match="read-only"):
        memory.append(memory.records[0], AUDIT_FAILURES)
