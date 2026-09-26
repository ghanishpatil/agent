from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Mapping


class JournalEventKind(str, Enum):
    SOLVE_STARTED = "solve_started"
    CONTEXT_UPDATED = "context_updated"
    SPECIALIST_SELECTED = "specialist_selected"
    SPECIALIST_INVOKED = "specialist_invoked"
    SPECIALIST_PROPOSAL = "specialist_proposal"
    PLANNER_DECISION = "planner_decision"
    DEDUPLICATION_REJECTED = "deduplication_rejected"
    ACTION_PROPOSED = "action_proposed"
    ACTION_EXECUTED = "action_executed"
    RESULT_CLASSIFIED = "result_classified"
    FAILURE_CLASSIFIED = "failure_classified"
    EVIDENCE_RECORDED = "evidence_recorded"
    EVIDENCE_IMPACT = "evidence_impact"
    HYPOTHESIS_PROPOSED = "hypothesis_proposed"
    HYPOTHESIS_TRANSITIONED = "hypothesis_transitioned"
    DEAD_END_CLOSED = "dead_end_closed"
    CANDIDATE_CREATED = "candidate_created"
    VERIFICATION_ATTEMPTED = "verification_attempted"
    VERIFICATION_COMPLETED = "verification_completed"
    CONTROL_DECISION = "control_decision"
    STATE_CHANGED = "state_changed"
    BUDGET_UPDATED = "budget_updated"
    RECOVERY_DECISION = "recovery_decision"
    STOP_REACHED = "stop_reached"
    SOLVE_FINISHED = "solve_finished"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class JournalEvent:
    run_id: str
    kind: JournalEventKind
    timestamp: datetime
    payload: Mapping[str, Any]


class RuntimeJournal:
    """Append-only single-process JSONL journal under ``.agent/runtime/``.

    Every append is one JSON line. Writes use ``O_APPEND | O_CREAT`` so concurrent appends within
    this process cannot interleave partial lines, guarded additionally by a lock (single-process
    atomicity; multi-process file locking is explicitly out of scope, matching the existing
    ``FailureMemory.append`` local-only pattern from Phase 2). The journal refuses any path whose
    parts contain ``.agent_audit`` -- historical Phase 1 data is never a valid journal target.
    """

    def __init__(self, path: Path) -> None:
        if ".agent_audit" in path.parts:
            raise ValueError("the runtime journal must never write into .agent_audit")
        self._path = path
        self._lock = threading.Lock()
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        return self._path

    def append(self, event: JournalEvent) -> None:
        line = json.dumps(
            {
                "run_id": event.run_id,
                "kind": event.kind.value,
                "timestamp": event.timestamp.isoformat(),
                "payload": event.payload,
            },
            sort_keys=True,
            ensure_ascii=False,
        )
        encoded = (line + "\n").encode("utf-8")
        with self._lock:
            fd = None
            try:
                import os

                fd = os.open(str(self._path), os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o644)
                os.write(fd, encoded)
            finally:
                if fd is not None:
                    import os

                    os.close(fd)

    def read_all(self) -> tuple[Mapping[str, Any], ...]:
        if not self._path.exists():
            return ()
        records = []
        for line in self._path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
        return tuple(records)
