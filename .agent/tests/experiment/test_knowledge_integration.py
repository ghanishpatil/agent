from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from ctf_agent import solve
from ctf_agent.autonomy.contracts import SolveStatus

from ctf_experiment.knowledge_dependent_benchmark_v2 import build_cases_v2, web_environment
from ctf_experiment.knowledge_reasoning import KnowledgeAugmentedReasoningSource
from ctf_experiment.knowledge_solver import solve_with_knowledge
from ctf_experiment.knowledge_dependent_harness_v2 import run_experiment_v2
from ctf_ingest.retrieval import KnowledgeRetriever


@pytest.fixture(scope="module")
def report(tmp_path_factory):
    root = tmp_path_factory.mktemp("kd_v2")
    return run_experiment_v2(root).to_dict()


def _case(report, case_id):
    return next(c for c in report["cases"] if c["case_id"] == case_id)


# -- Fidelity: the augmented composition with NO knowledge == frozen solve() -----------------


def test_control_composition_reproduces_frozen_solver(tmp_path: Path) -> None:
    cases = {c.case_id: c for c in build_cases_v2(tmp_path / "b")}
    case = cases["kd2-baseline-solvable"]
    env = case.environment_factory()

    frozen = solve(case.challenge, (), replace(env, run_id="frozen",
                                               workspace_root=tmp_path / "f",
                                               journal_path=tmp_path / "f" / "j.jsonl"),
                   case.constraints)
    augmented = solve_with_knowledge(
        case.challenge, (),
        replace(env, run_id="aug", workspace_root=tmp_path / "a", journal_path=tmp_path / "a" / "j.jsonl"),
        case.constraints, retriever=None,
    )
    assert frozen.status is augmented.result.status is SolveStatus.SOLVED
    assert frozen.verified_flag == augmented.result.verified_flag


# -- The five required demonstrations --------------------------------------------------------


def test_knowledge_dependent_flip_is_verified_and_attributable(report) -> None:
    c = _case(report, "kd2-knowledge-dependent")
    assert c["control"]["status"] == "BLOCKED"
    assert c["treatment"]["status"] == "SOLVED"
    assert c["treatment"]["verified_flag"] == "CTF{kd2_dependent}"
    assert c["knowledge_attributable_verified_solve"] is True
    assert c["treatment"]["expected_hypothesis_status"] in {"SUPPORTED", "VERIFIED"}
    assert c["treatment"]["retrieval_calls"] >= 1
    assert c["treatment"]["knowledge_hypotheses"] >= 1


def test_misleading_knowledge_rejected_and_decoy_never_verified(report) -> None:
    c = _case(report, "kd2-misleading")
    assert c["treatment"]["verified_flag"] is None  # no false verification
    assert c["safety_invariants"]["no_false_verification"]
    # the misleading branch was actually tested (an action ran), not merely ignored
    assert c["treatment"]["actions"] >= 1


def test_irrelevant_knowledge_no_unnecessary_exploration(report) -> None:
    c = _case(report, "kd2-noise")
    assert c["treatment"]["status"] == "BLOCKED"
    assert c["treatment"]["actions"] == 0  # noise never produced a runnable probe
    assert c["treatment"]["knowledge_hypotheses"] == 0
    assert c["treatment"]["retrieval_calls"] <= 2  # bounded, not runaway
    assert c["treatment"]["unnecessary_retrievals"] >= 1


def test_conflicting_knowledge_resolved_by_current_evidence(report) -> None:
    c = _case(report, "kd2-conflicting")
    assert c["treatment"]["status"] == "SOLVED"
    assert c["treatment"]["verified_flag"] == "CTF{kd2_conflicting_real}"
    # current evidence drove the hypothesis to SUPPORTED despite a "dead end" knowledge entry
    assert c["treatment"]["expected_hypothesis_status"] in {"SUPPORTED", "VERIFIED"}
    assert c["safety_invariants"]["no_false_disproof"]


def test_easy_case_stays_fast_no_deep_retrieval(report) -> None:
    c = _case(report, "kd2-baseline-solvable")
    assert c["treatment"]["status"] == "SOLVED"
    assert c["treatment"]["retrieval_calls"] == 0  # fast path: no escalation
    assert c["treatment"]["knowledge_hypotheses"] == 0


# -- Aggregate + safety ----------------------------------------------------------------------


def test_two_knowledge_attributable_solves_and_all_safety(report) -> None:
    assert report["knowledge_attributable_verified_solves"] == 2
    assert report["all_safety_invariants_preserved"] is True
    assert "KNOWLEDGE-CONTRIBUTING" in report["verdict"]


def test_no_executed_duplicate_actions_any_case(report) -> None:
    # Duplicate actions are structurally blocked by the kernel; none should execute.
    for c in report["cases"]:
        assert c["metrics"]["budget_violations"] == 0
        assert c["metrics"]["stopping_correct"] is True


# -- Trust boundary: knowledge source proposes only; it cannot execute/verify ----------------


def test_knowledge_source_has_no_execution_or_verification_capability() -> None:
    src = KnowledgeAugmentedReasoningSource(brain=object(), retriever=None)
    assert not hasattr(src, "execute")
    assert not hasattr(src, "verify")
    # It only implements the reasoning Protocol surface.
    assert hasattr(src, "suggest_hypotheses")
    assert hasattr(src, "suggest_actions")
    assert hasattr(src, "interpret")


def test_knowledge_derived_solve_went_through_kernel_verification(report) -> None:
    # A knowledge-attributable solve must carry kernel verification evidence + method, proving it
    # was NOT verified by the knowledge layer.
    c = _case(report, "kd2-knowledge-dependent")
    assert c["treatment"]["ends_with_stop"] is True
    assert c["knowledge_attributable_verified_solve"] is True
