from __future__ import annotations

from ctf_agent.adapters import AdapterRegistry, FileAdapter
from ctf_agent.deduplication import fingerprint_action, fingerprint_state
from ctf_agent.hypothesis_engine import HypothesisBoard
from ctf_agent.models import EnvironmentState, RelevantState
from ctf_agent.planner import ActionPlanner
from ctf_agent.proposals import ActionSuggestion
from ctf_agent.specialists.base import analysis_to_suggestions
from ctf_agent.specialists.crypto import CryptoSpecialist

from .conftest import make_specialist_context


STATE = RelevantState(EnvironmentState("env-1", ("decode_tool",)), "guest", "s1", "c1")


def _registry(tmp_path):
    from ctf_agent.adapters.subprocess_adapter import SubprocessAdapter, SubprocessCommand
    import sys

    registry = AdapterRegistry()
    # A real (registered) tool named decode_tool so the planner accepts the specialist's action.
    registry.register(SubprocessAdapter("decode_tool", SubprocessCommand(sys.executable, ("-c", "pass"))))
    return registry


def _specialist_actions(tmp_path):
    context = make_specialist_context(
        category="crypto",
        description="an xor-encoded cipher artifact",
        files=(str(tmp_path / "h.bin"),),
        available_tools=("decode_tool",),
    )
    analysis = CryptoSpecialist().analyze(context)
    _hyps, actions = analysis_to_suggestions(analysis)
    return context, actions


def test_specialist_action_enters_planner_and_produces_a_proposal(tmp_path) -> None:
    context, actions = _specialist_actions(tmp_path)
    board = HypothesisBoard()
    # Seed the specialist's hypotheses (as the loop would via _seed_hypotheses).
    for action in actions:
        if action.hypothesis_id not in {h.hypothesis_id for h in board.all_hypotheses()}:
            board.propose_hypothesis(action.hypothesis_id, f"seeded {action.hypothesis_id}")

    planner = ActionPlanner(_registry(tmp_path))
    diagnostics = planner.propose_with_diagnostics(
        context.challenge, board, actions, completed_fingerprints=set(), state_before=STATE
    )
    assert diagnostics.proposals, "a valid specialist action should become a planner proposal"


def test_specialist_action_naming_unregistered_tool_is_rejected_by_planner(tmp_path) -> None:
    context, _actions = _specialist_actions(tmp_path)
    board = HypothesisBoard()
    board.propose_hypothesis("crypto-xor", "xor")
    planner = ActionPlanner(_registry(tmp_path))  # only decode_tool registered
    rogue = ActionSuggestion(
        hypothesis_id="crypto-xor", objective="probe", tool="ghost_tool", target="x"
    )
    diagnostics = planner.propose_with_diagnostics(
        context.challenge, board, (rogue,), completed_fingerprints=set(), state_before=STATE
    )
    assert diagnostics.proposals == ()


def test_specialist_duplicate_action_is_blocked_by_planner(tmp_path) -> None:
    context, actions = _specialist_actions(tmp_path)
    board = HypothesisBoard()
    for action in actions:
        if action.hypothesis_id not in {h.hypothesis_id for h in board.all_hypotheses()}:
            board.propose_hypothesis(action.hypothesis_id, f"seeded {action.hypothesis_id}")
    planner = ActionPlanner(_registry(tmp_path))
    first = planner.propose_with_diagnostics(
        context.challenge, board, actions, completed_fingerprints=set(), state_before=STATE
    ).proposals[0]
    completed = {(fingerprint_action(first.to_action("probe", STATE)), fingerprint_state(STATE))}

    # Re-propose only that same action; in the same state it must be de-duplicated away.
    same = tuple(a for a in actions if a.objective == first.objective)
    diagnostics = planner.propose_with_diagnostics(
        context.challenge, board, same, completed_fingerprints=completed, state_before=STATE
    )
    assert all(p.objective != first.objective for p in diagnostics.proposals)


def test_specialist_action_with_unmet_prerequisite_is_blocked(tmp_path) -> None:
    context, _actions = _specialist_actions(tmp_path)
    board = HypothesisBoard()
    board.propose_hypothesis("crypto-xor", "xor")
    planner = ActionPlanner(_registry(tmp_path))
    gated = ActionSuggestion(
        hypothesis_id="crypto-xor",
        objective="gated probe",
        tool="decode_tool",
        target="h.bin",
        prerequisites=("service-started",),
    )
    diagnostics = planner.propose_with_diagnostics(
        context.challenge, board, (gated,), completed_fingerprints=set(), state_before=STATE
    )
    assert diagnostics.proposals == ()
    assert diagnostics.blocked_only_by_prerequisites
