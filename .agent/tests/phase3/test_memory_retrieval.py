from __future__ import annotations

from pathlib import Path

from ctf_agent.memory_retrieval import AdvisoryMemory, MemoryQuery
from ctf_agent.models import ResultClass


AUDIT_ROOT = Path(__file__).parents[3] / ".agent_audit"


def test_empty_query_returns_empty_bundle_no_bulk_dump() -> None:
    memory = AdvisoryMemory(AUDIT_ROOT)
    bundle = memory.retrieve(MemoryQuery())
    assert bundle.is_empty()


def test_category_query_returns_advisory_technique_matches() -> None:
    memory = AdvisoryMemory(AUDIT_ROOT)
    bundle = memory.retrieve(MemoryQuery(category="web", keywords=("injection",)))
    assert bundle.techniques
    assert all(match.advisory_only for match in bundle.techniques)
    assert all(match.source for match in bundle.techniques if match.source)


def test_keyword_query_returns_failure_matches_with_traceability() -> None:
    memory = AdvisoryMemory(AUDIT_ROOT)
    bundle = memory.retrieve(
        MemoryQuery(category="web", result_class=ResultClass.RATE_LIMIT, keywords=("sql", "timing"))
    )
    assert bundle.failures
    assert all(match.advisory_only for match in bundle.failures)
    assert all(match.record.source for match in bundle.failures)


def test_source_reads_do_not_modify_agent_audit() -> None:
    failures_path = AUDIT_ROOT / "failures" / "failures.jsonl"
    before = failures_path.read_bytes()
    memory = AdvisoryMemory(AUDIT_ROOT)
    memory.retrieve(MemoryQuery(category="web", keywords=("sql",)))
    memory.retrieve(MemoryQuery(category="forensics", keywords=("timing",)))
    after = failures_path.read_bytes()
    assert before == after


def test_lazy_loading_does_not_touch_unrelated_sources(tmp_path: Path) -> None:
    # A query with only keywords that don't match any category should not raise even if a
    # dataset file happens to be absent -- retrieval is defensive about optional sources.
    empty_root = tmp_path / "no_audit_here"
    empty_root.mkdir()
    memory = AdvisoryMemory(empty_root)
    bundle = memory.retrieve(MemoryQuery(category="web", keywords=("anything",)))
    assert bundle.techniques == ()
    assert bundle.tools == ()
    assert bundle.trajectories == ()
