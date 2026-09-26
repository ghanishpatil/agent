from __future__ import annotations

from ctf_agent.deduplication import ActionRegistry, fingerprint_action
from ctf_agent.models import (
    Action,
    ControlDecision,
    EnvironmentState,
    RelevantState,
    ResultClass,
)


def state(*, session: str = "s1", environment_revision: str = "env-1") -> RelevantState:
    return RelevantState(
        environment=EnvironmentState(
            revision=environment_revision,
            available_tools=("http_request",),
        ),
        authentication_context="user",
        session_context=session,
        challenge_revision="challenge-1",
    )


def action(action_id: str, *, current_state: RelevantState, input_data: object = None) -> Action:
    return Action(
        action_id=action_id,
        objective="Probe SQL injection",
        tool="http_request",
        target="https://ctf.local/item",
        input_data={"id": "1'"} if input_data is None else input_data,
        relevant_parameters={"method": "GET"},
        prerequisites=("target-online",),
        state_before=current_state,
    )


def test_action_fingerprint_ignores_ids_and_dictionary_order() -> None:
    first = action("a1", current_state=state(), input_data={"a": 1, "b": 2})
    second = action("different-id", current_state=state(), input_data={"b": 2, "a": 1})
    assert fingerprint_action(first) == fingerprint_action(second)


def test_identical_action_in_identical_state_is_duplicate() -> None:
    registry = ActionRegistry()
    assert registry.register(action("a1", current_state=state())) is ControlDecision.ALLOWED
    assert registry.register(action("a2", current_state=state())) is ControlDecision.DUPLICATE


def test_same_action_after_session_state_change_is_allowed() -> None:
    registry = ActionRegistry()
    registry.register(action("a1", current_state=state(session="s1")))
    assert registry.register(action("a2", current_state=state(session="s2"))) is ControlDecision.ALLOWED


def test_same_action_after_environment_change_is_allowed() -> None:
    registry = ActionRegistry()
    registry.register(action("a1", current_state=state(environment_revision="env-1")))
    assert registry.register(action("a2", current_state=state(environment_revision="env-2"))) is ControlDecision.ALLOWED


def test_timestamp_metadata_does_not_change_action_identity() -> None:
    registry = ActionRegistry()
    first = action("a1", current_state=state(), input_data={"id": "1", "timestamp": "ignored"})
    second = action("a2", current_state=state(), input_data={"id": "1", "timestamp": "ignored"})
    assert registry.register(first) is ControlDecision.ALLOWED
    assert registry.register(second) is ControlDecision.DUPLICATE


def test_action_registry_keeps_auditable_identity_and_result_record() -> None:
    registry = ActionRegistry()
    attempted = action("a-track", current_state=state())
    registry.register(attempted)
    registry.record_result(
        "a-track", result_class=ResultClass.RATE_LIMIT, state_after=state(session="s2")
    )
    record = registry.records[0]
    assert record.action_id == "a-track"
    assert record.fingerprint == fingerprint_action(attempted)
    assert record.registered_at is not None
    assert record.status is ControlDecision.ALLOWED
    assert record.result_class is ResultClass.RATE_LIMIT
    assert record.state_before == state()
    assert record.state_after == state(session="s2")
