from __future__ import annotations

import pytest

from ctf_agent.adapters import AdapterRegistry, FileAdapter
from ctf_agent.llm_boundary import ScriptedReasoningSource
from ctf_agent.proposals import (
    ActionSuggestion,
    HypothesisSuggestion,
    InterpretationNote,
    ProposalRejected,
    validate_action_suggestion,
    validate_hypothesis_suggestion,
    validate_interpretation_note,
)


def registry(tmp_path) -> AdapterRegistry:
    reg = AdapterRegistry()
    reg.register(FileAdapter("file_read", tmp_path))
    return reg


def test_valid_hypothesis_suggestion_passes() -> None:
    suggestion = HypothesisSuggestion("h1", "SQL injection may exist", technique="sqli")
    assert validate_hypothesis_suggestion(suggestion) is suggestion


def test_hypothesis_suggestion_rejects_empty_statement() -> None:
    with pytest.raises(ProposalRejected, match="statement"):
        validate_hypothesis_suggestion(HypothesisSuggestion("h1", "   "))


def test_hypothesis_suggestion_rejects_attempt_to_assert_disproven() -> None:
    suggestion = HypothesisSuggestion(
        "h1", "mark disproven because the tool failed once", technique="sqli"
    )
    with pytest.raises(ProposalRejected, match="state transition"):
        validate_hypothesis_suggestion(suggestion)


def test_hypothesis_suggestion_rejects_attempt_to_assert_verified() -> None:
    suggestion = HypothesisSuggestion("h1", "reasonable", rationale="I'll just declare verified")
    with pytest.raises(ProposalRejected, match="state transition"):
        validate_hypothesis_suggestion(suggestion)


def test_valid_action_suggestion_passes_when_tool_registered(tmp_path) -> None:
    suggestion = ActionSuggestion(
        hypothesis_id="h1",
        objective="read the extracted handout",
        tool="file_read",
        target="handout.txt",
    )
    assert validate_action_suggestion(suggestion, registry(tmp_path)) is suggestion


def test_action_suggestion_rejects_unregistered_tool(tmp_path) -> None:
    suggestion = ActionSuggestion(
        hypothesis_id="h1", objective="probe", tool="totally_made_up_tool", target="x"
    )
    with pytest.raises(ProposalRejected, match="not registered"):
        validate_action_suggestion(suggestion, registry(tmp_path))


def test_action_suggestion_rejects_empty_objective(tmp_path) -> None:
    suggestion = ActionSuggestion(hypothesis_id="h1", objective="  ", tool="file_read", target="x")
    with pytest.raises(ProposalRejected, match="objective"):
        validate_action_suggestion(suggestion, registry(tmp_path))


def test_interpretation_note_rejects_forbidden_phrase() -> None:
    note = InterpretationNote("h1", "based on this I will treat as verified")
    with pytest.raises(ProposalRejected, match="state transition"):
        validate_interpretation_note(note)


def test_interpretation_note_is_advisory_and_has_no_state_mutation_method() -> None:
    note = validate_interpretation_note(InterpretationNote("h1", "the 429 suggests rate limiting"))
    # An InterpretationNote is plain data -- there is no method on it (or anywhere reachable from
    # it) that could set Hypothesis/Evidence/FlagCandidate state. This assertion documents that.
    assert not hasattr(note, "apply")
    assert not hasattr(note, "commit")


def test_scripted_reasoning_source_returns_fixed_suggestions() -> None:
    source = ScriptedReasoningSource(
        hypothesis_script=(HypothesisSuggestion("h1", "SQLi may exist"),),
    )
    suggestions = source.suggest_hypotheses(context=None)  # context unused by the double
    assert suggestions == (HypothesisSuggestion("h1", "SQLi may exist"),)
    assert source.suggest_actions(context=None) == ()
