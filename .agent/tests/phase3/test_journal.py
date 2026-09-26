from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from ctf_agent.journal import JournalEvent, JournalEventKind, RuntimeJournal


NOW = datetime(2026, 9, 24, tzinfo=timezone.utc)


def test_append_writes_one_json_line(tmp_path: Path) -> None:
    journal = RuntimeJournal(tmp_path / "run.jsonl")
    journal.append(
        JournalEvent("run-1", JournalEventKind.ACTION_PROPOSED, NOW, {"tool": "http_request"})
    )
    records = journal.read_all()
    assert len(records) == 1
    assert records[0]["kind"] == "action_proposed"
    assert records[0]["payload"]["tool"] == "http_request"


def test_append_is_additive_across_multiple_events(tmp_path: Path) -> None:
    journal = RuntimeJournal(tmp_path / "run.jsonl")
    journal.append(JournalEvent("run-1", JournalEventKind.ACTION_PROPOSED, NOW, {"n": 1}))
    journal.append(JournalEvent("run-1", JournalEventKind.ACTION_EXECUTED, NOW, {"n": 2}))
    journal.append(JournalEvent("run-1", JournalEventKind.CONTROL_DECISION, NOW, {"n": 3}))
    records = journal.read_all()
    assert [record["payload"]["n"] for record in records] == [1, 2, 3]


def test_append_never_overwrites_existing_content(tmp_path: Path) -> None:
    path = tmp_path / "run.jsonl"
    path.write_text('{"existing": true}\n', encoding="utf-8")
    journal = RuntimeJournal(path)
    journal.append(JournalEvent("run-1", JournalEventKind.STATE_CHANGED, NOW, {}))
    content = path.read_text(encoding="utf-8")
    assert content.startswith('{"existing": true}')
    assert content.count("\n") == 2


def test_journal_refuses_any_path_under_agent_audit(tmp_path: Path) -> None:
    forbidden = tmp_path / ".agent_audit" / "runtime.jsonl"
    with pytest.raises(ValueError, match="agent_audit"):
        RuntimeJournal(forbidden)


def test_read_all_on_nonexistent_journal_returns_empty(tmp_path: Path) -> None:
    journal = RuntimeJournal(tmp_path / "never_written.jsonl")
    assert journal.read_all() == ()


def test_journal_creates_parent_directories(tmp_path: Path) -> None:
    nested = tmp_path / "runtime" / "nested" / "run.jsonl"
    journal = RuntimeJournal(nested)
    journal.append(JournalEvent("run-1", JournalEventKind.ACTION_PROPOSED, NOW, {}))
    assert nested.exists()
