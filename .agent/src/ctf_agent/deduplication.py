from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, is_dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from .models import Action, ControlDecision, RelevantState, ResultClass


def _canonical(value: Any) -> Any:
    if is_dataclass(value):
        return _canonical(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, bytes):
        return {"__bytes__": value.hex()}
    if isinstance(value, dict):
        sorted_items = sorted(value.items(), key=lambda pair: str(pair[0]))
        return {str(key): _canonical(item) for key, item in sorted_items}
    if isinstance(value, (list, tuple, set, frozenset)):
        values = [_canonical(item) for item in value]
        if isinstance(value, (set, frozenset)):
            return sorted(values, key=lambda item: json.dumps(item, sort_keys=True))
        return values
    return value


def _digest(payload: Any) -> str:
    encoded = json.dumps(_canonical(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def fingerprint_action(action: Action) -> str:
    """Fingerprint semantic action identity, excluding IDs, timestamps, and execution metadata."""
    return _digest(
        {
            "objective": action.objective.strip().lower(),
            "tool": action.tool.strip().lower(),
            "target": action.target.strip(),
            "input": action.input_data,
            "parameters": action.relevant_parameters,
            "prerequisites": action.prerequisites,
        }
    )


def fingerprint_state(state: RelevantState) -> str:
    return _digest(state)


@dataclass(frozen=True)
class ActionRecord:
    action_id: str
    fingerprint: str
    registered_at: datetime
    status: ControlDecision
    result_class: ResultClass | None
    state_before: RelevantState
    state_after: RelevantState | None


class ActionRegistry:
    def __init__(self) -> None:
        self._seen: set[tuple[str, str]] = set()
        self._records: list[ActionRecord] = []

    @property
    def records(self) -> tuple[ActionRecord, ...]:
        return tuple(self._records)

    def register(self, action: Action) -> ControlDecision:
        fingerprint = fingerprint_action(action)
        identity = (fingerprint, fingerprint_state(action.state_before))
        status = ControlDecision.DUPLICATE if identity in self._seen else ControlDecision.ALLOWED
        if status is ControlDecision.ALLOWED:
            self._seen.add(identity)
        self._records.append(
            ActionRecord(
                action_id=action.action_id,
                fingerprint=fingerprint,
                registered_at=datetime.now(timezone.utc),
                status=status,
                result_class=None,
                state_before=action.state_before,
                state_after=action.state_after,
            )
        )
        return status

    def record_result(
        self,
        action_id: str,
        *,
        result_class: ResultClass,
        state_after: RelevantState | None,
    ) -> None:
        for index in range(len(self._records) - 1, -1, -1):
            record = self._records[index]
            if record.action_id == action_id:
                self._records[index] = replace(
                    record, result_class=result_class, state_after=state_after
                )
                return
        raise KeyError(f"unknown action_id: {action_id}")
