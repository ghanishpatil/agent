from __future__ import annotations

from pathlib import Path

from ctf_agent.adapters import AdapterRegistry, FileAdapter
from ctf_agent.context import ChallengeMetadata, build_context
from ctf_agent.deduplication import fingerprint_action, fingerprint_state
from ctf_agent.hypothesis_engine import HypothesisBoard
from ctf_agent.kernel import TrustKernel
from ctf_agent.models import EnvironmentState, RelevantState
from ctf_agent.planner import ActionPlanner
from ctf_agent.proposals import ActionSuggestion


STATE = RelevantState(EnvironmentState("env-1", ("file_read",)), "guest", "s1", "c1")


def make_registry(tmp_path: Path) -> AdapterRegistry:
    registry = AdapterRegistry()
    registry.register(FileAdapter("file_read", tmp_path))
    return registry


def metadata() -> ChallengeMetadata:
    return ChallengeMetadata(name="sample", category="forensics")


def test_planner_prefers_the_more_discriminating_proposal(tmp_path: Path) -> None:
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "The flag is base64 encoded")
    board.propose_hypothesis("h2", "The flag is hidden in EXIF metadata")
    kernel = TrustKernel()
    context = build_context(metadata(), kernel, board)
    planner = ActionPlanner(make_registry(tmp_path))

    discriminating = ActionSuggestion(
        hypothesis_id="h1",
        objective="decode candidate base64",
        tool="file_read",
        target="candidate.b64",
        expected_observation="decodes to readable text",
    )
    vague = ActionSuggestion(
        hypothesis_id="h2", objective="look around", tool="file_read", target="whatever.txt"
    )
    proposals = planner.propose(
        context, board, (vague, discriminating), completed_fingerprints=set(), state_before=STATE
    )
    assert proposals[0].objective == "decode candidate base64"


def test_planner_prefers_cheap_test_when_scores_tie(tmp_path: Path) -> None:
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "hyp one")
    kernel = TrustKernel()
    context = build_context(metadata(), kernel, board)
    planner = ActionPlanner(make_registry(tmp_path))

    cheap = ActionSuggestion(hypothesis_id="h1", objective="cheap probe", tool="file_read", target="a")
    expensive = ActionSuggestion(
        hypothesis_id="h1",
        objective="expensive probe",
        tool="file_read",
        target="b",
        prerequisites=("service-started",),
    )
    proposals = planner.propose(
        context,
        board,
        (expensive, cheap),
        completed_fingerprints=set(),
        state_before=STATE,
        satisfied_prerequisites={"service-started"},
    )
    assert proposals[0].objective == "cheap probe"


def test_planner_rejects_duplicate_action_in_same_state(tmp_path: Path) -> None:
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "hyp one")
    kernel = TrustKernel()
    context = build_context(metadata(), kernel, board)
    planner = ActionPlanner(make_registry(tmp_path))
    suggestion = ActionSuggestion(hypothesis_id="h1", objective="probe", tool="file_read", target="a")

    already_run_action = suggestion
    probe = planner.propose(context, board, (already_run_action,), completed_fingerprints=set(), state_before=STATE)[0]
    fingerprint = fingerprint_action(probe.to_action("probe", STATE))
    completed = {(fingerprint, fingerprint_state(STATE))}

    proposals = planner.propose(
        context, board, (suggestion,), completed_fingerprints=completed, state_before=STATE
    )
    assert proposals == ()


def test_planner_allows_repeat_after_state_change(tmp_path: Path) -> None:
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "hyp one")
    kernel = TrustKernel()
    context = build_context(metadata(), kernel, board)
    planner = ActionPlanner(make_registry(tmp_path))
    suggestion = ActionSuggestion(hypothesis_id="h1", objective="probe", tool="file_read", target="a")

    probe = planner.propose(context, board, (suggestion,), completed_fingerprints=set(), state_before=STATE)[0]
    fingerprint = fingerprint_action(probe.to_action("probe", STATE))
    completed = {(fingerprint, fingerprint_state(STATE))}

    changed_state = RelevantState(STATE.environment, "guest", "s2", "c1")
    proposals = planner.propose(
        context, board, (suggestion,), completed_fingerprints=completed, state_before=changed_state
    )
    assert len(proposals) == 1


def test_planner_rejects_action_with_unmet_prerequisite(tmp_path: Path) -> None:
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "hyp one")
    kernel = TrustKernel()
    context = build_context(metadata(), kernel, board)
    planner = ActionPlanner(make_registry(tmp_path))
    suggestion = ActionSuggestion(
        hypothesis_id="h1",
        objective="probe",
        tool="file_read",
        target="a",
        prerequisites=("service-started",),
    )
    proposals = planner.propose(
        context, board, (suggestion,), completed_fingerprints=set(), state_before=STATE
    )
    assert proposals == ()


def test_planner_rejects_suggestion_for_a_closed_branch(tmp_path: Path) -> None:
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "weak lead")
    board.set_priority("h1", 0)
    kernel = TrustKernel()
    context = build_context(metadata(), kernel, board)
    planner = ActionPlanner(make_registry(tmp_path))
    suggestion = ActionSuggestion(hypothesis_id="h1", objective="probe", tool="file_read", target="a")
    proposals = planner.propose(
        context, board, (suggestion,), completed_fingerprints=set(), state_before=STATE
    )
    assert proposals == ()


def test_planner_rejects_suggestion_for_unregistered_tool(tmp_path: Path) -> None:
    board = HypothesisBoard()
    board.propose_hypothesis("h1", "hyp one")
    kernel = TrustKernel()
    context = build_context(metadata(), kernel, board)
    planner = ActionPlanner(make_registry(tmp_path))
    suggestion = ActionSuggestion(hypothesis_id="h1", objective="probe", tool="ghost_tool", target="a")
    proposals = planner.propose(
        context, board, (suggestion,), completed_fingerprints=set(), state_before=STATE
    )
    assert proposals == ()


def test_planner_produces_nothing_once_context_is_verified(tmp_path: Path) -> None:
    from ctf_agent.classifier import classify_result
    from ctf_agent.models import (
        ExecutionResult,
        FlagCandidate,
        HypothesisImpact,
        Observation,
        VerificationPolicy,
    )
    from ctf_agent.context import build_context as _build

    kernel = TrustKernel(
        verification_policy=VerificationPolicy(authoritative_output_tools=("challenge_service",))
    )
    board = HypothesisBoard()
    hypothesis = board.propose_hypothesis("h1", "Candidate is intended flag")
    derive_execution = ExecutionResult("derive-1", "analysis", exit_code=0, stdout="CTF{real}")
    from datetime import datetime, timezone

    now = datetime(2026, 9, 24, tzinfo=timezone.utc)
    prior = kernel.evidence.record_current(
        observation=Observation("obs-derive", "derive-1", now, "analysis", derive_execution),
        classification=classify_result(derive_execution),
        impact=HypothesisImpact.NO_IMPACT,
        affected_hypotheses=("h1",),
    )
    from ctf_agent.models import Action

    stop_action = Action(
        "a-stop",
        "submit",
        "challenge_service",
        "https://ctf.local/submit",
        None,
        {},
        (),
        STATE,
    )
    result = kernel.process(
        action=stop_action,
        execution=ExecutionResult(
            "a-stop", "challenge_service", exit_code=0, response_body="accepted CTF{real}"
        ),
        hypothesis=hypothesis,
        observed_at=now,
        source="challenge-service",
        candidate=FlagCandidate("CTF{real}", "derived"),
        candidate_evidence_ids=(prior.evidence_id,),
        verifier="ctfd",
    )
    board.record(result)
    verified_context = _build(metadata(), kernel, board)

    planner = ActionPlanner(make_registry(tmp_path))
    suggestion = ActionSuggestion(hypothesis_id="h1", objective="probe", tool="file_read", target="a")
    proposals = planner.propose(
        verified_context, board, (suggestion,), completed_fingerprints=set(), state_before=STATE
    )
    assert proposals == ()


def _make_supported_hypothesis(tmp_path: Path):
    """Real evidence -> real SUPPORTS impact -> apply_evidence -> board.record(), matching how
    every other SUPPORTED hypothesis in this test suite is produced (never hand-constructed)."""
    from dataclasses import replace as dataclasses_replace
    from datetime import datetime, timezone

    from ctf_agent.hypothesis import apply_evidence
    from ctf_agent.models import Action, ExecutionResult, HypothesisImpact

    now = datetime(2026, 9, 24, tzinfo=timezone.utc)
    kernel = TrustKernel()
    board = HypothesisBoard()
    hypothesis = board.propose_hypothesis("h1", "candidate is correct")
    action = Action("a1", "probe", "file_read", "a", "a", {}, (), STATE)
    result = kernel.process(
        action=action,
        execution=ExecutionResult("a1", "file_read", exit_code=0, stdout="flag observed"),
        hypothesis=hypothesis,
        observed_at=now,
        source="live",
    )
    supported = apply_evidence(hypothesis, result.evidence, HypothesisImpact.SUPPORTS, now)
    board.record(dataclasses_replace(result, hypothesis=supported))
    context = build_context(metadata(), kernel, board)
    return board, context


def test_planner_allows_a_submission_suggestion_for_an_already_supported_hypothesis(
    tmp_path: Path,
) -> None:
    """A SUPPORTED hypothesis is no longer 'open' for further discriminating testing, but a
    suggestion carrying candidate_flag is a distinct submission step, not more testing -- it must
    remain proposable, otherwise the loop could never actually submit a flag it already has strong
    evidence for."""
    board, context = _make_supported_hypothesis(tmp_path)
    planner = ActionPlanner(make_registry(tmp_path))
    submit_suggestion = ActionSuggestion(
        hypothesis_id="h1",
        objective="submit the flag",
        tool="file_read",
        target="a",
        candidate_flag="CTF{whatever}",
    )
    proposals = planner.propose(
        context, board, (submit_suggestion,), completed_fingerprints=set(), state_before=STATE
    )
    assert len(proposals) == 1
    assert proposals[0].candidate_flag == "CTF{whatever}"


def test_planner_rejects_a_plain_non_submission_suggestion_for_a_supported_hypothesis(
    tmp_path: Path,
) -> None:
    """The exception is narrow: a suggestion for a SUPPORTED hypothesis that does NOT carry a
    candidate_flag is still just more testing of an already-resolved question, and must be
    rejected the same way it would be for a DISPROVEN hypothesis."""
    board, context = _make_supported_hypothesis(tmp_path)
    planner = ActionPlanner(make_registry(tmp_path))
    plain_suggestion = ActionSuggestion(
        hypothesis_id="h1", objective="probe some more", tool="file_read", target="a"
    )
    proposals = planner.propose(
        context, board, (plain_suggestion,), completed_fingerprints=set(), state_before=STATE
    )
    assert proposals == ()
