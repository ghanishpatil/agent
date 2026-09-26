from __future__ import annotations

from pathlib import Path

import pytest

from ctf_agent import ChallengeInput, EnvironmentConfig, SolveConstraints, SolveStatus, solve
from ctf_agent.autonomy.contracts import InputFactState, SolveResult


def test_invalid_input_returns_invalid_without_a_flag(tmp_path: Path) -> None:
    result = solve(
        ChallengeInput(),
        environment=EnvironmentConfig(
            workspace_root=tmp_path, journal_path=tmp_path / "invalid.jsonl", run_id="invalid"
        ),
    )
    assert result.status is SolveStatus.INVALID_INPUT
    assert result.verified_flag is None
    assert "requires at least" in result.terminal_reason


def test_missing_category_is_inferred_not_silently_known(crypto_package) -> None:
    challenge, resources, environment, constraints, _flag, _verifier = crypto_package
    result = solve(challenge, resources, environment, constraints)
    category = result.understanding.fact("category")
    assert category.value == "crypto"
    assert category.state is InputFactState.INFERRED


def test_autonomous_solve_returns_only_kernel_verified_flag(crypto_package) -> None:
    challenge, resources, environment, constraints, flag, verifier = crypto_package
    result = solve(challenge, resources, environment, constraints)

    assert result.status is SolveStatus.SOLVED
    assert result.verified_flag == flag
    assert result.verification_evidence_ids
    assert result.final_verification_method == "AUTHORITATIVE_VERIFIER"
    assert result.actions[-1].decision == "STOP"
    assert verifier.calls == 1
    assert result.specialist_contributions
    assert any(item.specialist == "crypto" for item in result.specialist_contributions)
    assert result.budget_usage.submissions == 1
    assert result.budget_usage.budget_violations == 0


def test_non_solved_result_cannot_contain_a_flag() -> None:
    from ctf_agent.autonomy.contracts import ChallengeUnderstanding

    understanding = ChallengeUnderstanding((), (), (), (), ())
    with pytest.raises(ValueError, match="must not contain"):
        SolveResult(
            status=SolveStatus.BLOCKED,
            run_id="r",
            challenge_name="x",
            understanding=understanding,
            terminal_reason="blocked",
            verified_flag="CTF{fabricated}",
        )


def test_no_permitted_tools_returns_controlled_blocked(tmp_path: Path) -> None:
    result = solve(
        ChallengeInput(name="no-tools", description="an xor cipher", flag_format="CTF{...}"),
        environment=EnvironmentConfig(
            workspace_root=tmp_path, journal_path=tmp_path / "blocked.jsonl", run_id="blocked"
        ),
        constraints=SolveConstraints(max_actions=3),
    )
    assert result.status is SolveStatus.BLOCKED
    assert result.verified_flag is None
    assert "no useful" in result.terminal_reason


def test_journal_reconstructs_key_lifecycle(crypto_package) -> None:
    challenge, resources, environment, constraints, _flag, _verifier = crypto_package
    result = solve(challenge, resources, environment, constraints)
    from ctf_agent.journal import RuntimeJournal

    kinds = {item["kind"] for item in RuntimeJournal(Path(result.journal_path)).read_all()}
    required = {
        "solve_started",
        "context_updated",
        "specialist_selected",
        "specialist_invoked",
        "specialist_proposal",
        "hypothesis_proposed",
        "planner_decision",
        "action_executed",
        "result_classified",
        "evidence_recorded",
        "evidence_impact",
        "candidate_created",
        "verification_attempted",
        "verification_completed",
        "stop_reached",
        "solve_finished",
    }
    assert required <= kinds


def test_failed_tool_output_is_not_a_candidate_origin() -> None:
    from datetime import datetime, timezone

    from ctf_agent.classifier import classify_result
    from ctf_agent.context import ChallengeMetadata, build_context
    from ctf_agent.hypothesis_engine import HypothesisBoard
    from ctf_agent.kernel import TrustKernel
    from ctf_agent.models import ExecutionResult, HypothesisImpact, Observation
    from ctf_agent.specialists.base import SpecialistContext, extract_flag_candidates

    kernel = TrustKernel()
    execution = ExecutionResult(
        "a1", "decode_tool", exit_code=1, stdout="crash log CTF{decoy}"
    )
    kernel.evidence.record_current(
        observation=Observation(
            "obs1", "a1", datetime(2026, 1, 1, tzinfo=timezone.utc), "x.bin", execution
        ),
        classification=classify_result(execution),
        impact=HypothesisImpact.UNRESOLVES,
        affected_hypotheses=("crypto-xor",),
    )
    context = SpecialistContext(
        build_context(
            ChallengeMetadata("x", "crypto", flag_format="CTF{...}"),
            kernel,
            HypothesisBoard(),
        )
    )
    assert extract_flag_candidates(context) == ()


def test_solved_result_requires_evidence_and_method() -> None:
    from ctf_agent.autonomy.contracts import ChallengeUnderstanding, SolveResult

    understanding = ChallengeUnderstanding((), (), (), (), ())
    with pytest.raises(ValueError, match="verification evidence"):
        SolveResult(
            status=SolveStatus.SOLVED,
            run_id="r",
            challenge_name="x",
            understanding=understanding,
            terminal_reason="claimed",
            verified_flag="CTF{x}",
        )


def test_malformed_public_values_return_invalid_input(tmp_path: Path) -> None:
    malformed = ChallengeInput(name=123, description="x")  # type: ignore[arg-type]
    result = solve(
        malformed,
        environment=EnvironmentConfig(
            workspace_root=tmp_path,
            journal_path=tmp_path / "malformed.jsonl",
            run_id="malformed",
        ),
        constraints=SolveConstraints(max_actions="many"),  # type: ignore[arg-type]
    )
    assert result.status is SolveStatus.INVALID_INPUT
    assert result.verified_flag is None
    assert "name must be a string" in result.terminal_reason
    assert "max_actions must be an integer" in result.terminal_reason


def test_content_resources_with_same_filename_do_not_overwrite(tmp_path: Path) -> None:
    from ctf_agent import ChallengeResource, ResourceKind
    from ctf_agent.autonomy.resources import materialize_resources

    resources = (
        ChallengeResource("one", ResourceKind.FILE, content=b"first", filename="same.bin"),
        ChallengeResource("two", ResourceKind.FILE, content=b"second", filename="same.bin"),
    )
    paths = materialize_resources(resources, tmp_path)
    assert paths[0] != paths[1]
    assert Path(paths[0]).read_bytes() == b"first"
    assert Path(paths[1]).read_bytes() == b"second"
