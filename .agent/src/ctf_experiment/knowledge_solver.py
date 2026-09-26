"""Composition root that runs the FROZEN pipeline with a knowledge-augmented reasoning source.

This is `ctf_agent.autonomy.solve()`'s happy-path composition, reusing the frozen helper
functions verbatim, with exactly one substitution: the reasoning source is wrapped by
``KnowledgeAugmentedReasoningSource`` before the existing ``RoutedReasoningSource``. The
TrustKernel, EvidenceManager, VerificationController, planner, adapters, journal, board, and
result projection are all the frozen components — nothing in `ctf_agent` is modified.

With an empty retriever this reproduces frozen `solve()` behaviour (the augmented source adds
nothing when the brain is productive and retrieval finds nothing). With a populated retriever
it may seed typed candidate hypotheses that still must be proven and verified by the kernel.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

from ctf_agent.autonomy.contracts import (
    ChallengeInput,
    ChallengeResource,
    EnvironmentConfig,
    SolveConstraints,
    SolveResult,
    SolveStatus,
)
from ctf_agent.autonomy.reasoning import RoutedReasoningSource
from ctf_agent.autonomy.control import AutonomyController
from ctf_agent.autonomy.resources import materialize_resources
from ctf_agent.autonomy.understanding import understand_challenge, to_metadata
from ctf_agent.autonomy import solver as _solver
from ctf_agent.hypothesis_engine import HypothesisBoard
from ctf_agent.journal import JournalEvent, JournalEventKind, RuntimeJournal
from ctf_agent.kernel import TrustKernel
from ctf_agent.loop import ReasoningLoop
from ctf_agent.planner import ActionPlanner
from ctf_agent.specialists import SpecialistRegistry, SpecialistReasoningSource
from ctf_agent.models import ChallengeState

from ctf_ingest.retrieval import KnowledgeRetriever
from .knowledge_reasoning import KnowledgeAugmentedReasoningSource, KnowledgeMetrics


@dataclass
class KnowledgeSolveOutput:
    result: SolveResult
    knowledge: KnowledgeMetrics


def solve_with_knowledge(
    challenge: ChallengeInput,
    resources: Tuple[ChallengeResource, ...] = (),
    environment: Optional[EnvironmentConfig] = None,
    constraints: Optional[SolveConstraints] = None,
    *,
    retriever: Optional[KnowledgeRetriever] = None,
    max_retrievals: int = 2,
    max_candidates: int = 2,
    reasoning_source_factory=None,
) -> KnowledgeSolveOutput:
    environment = environment if isinstance(environment, EnvironmentConfig) else EnvironmentConfig()
    constraints = constraints if isinstance(constraints, SolveConstraints) else SolveConstraints()
    clock = environment.clock if callable(environment.clock) else (lambda: datetime.now(timezone.utc))
    monotonic = environment.monotonic if callable(environment.monotonic) else _solver.time.monotonic
    run_id = environment.run_id or _solver._run_id(challenge.name)
    workspace = (
        environment.workspace_root
        if isinstance(environment.workspace_root, Path)
        else _solver._default_runtime_root() / run_id
    )
    journal_path = (
        environment.journal_path
        if isinstance(environment.journal_path, Path)
        else workspace / "journal.jsonl"
    )
    journal = RuntimeJournal(journal_path)
    started = monotonic()
    raw_paths = tuple(str(r.path) for r in resources if r.path is not None)
    metrics = KnowledgeMetrics()

    try:
        resource_paths = materialize_resources(resources, workspace)
        understanding = understand_challenge(challenge, resource_paths)
        metadata = to_metadata(challenge, understanding, resource_paths)
        registry = _solver._adapter_registry(environment.permitted_tools)
        effective_constraints = _solver._apply_attempt_limit(constraints, challenge.attempt_limit)
        policy = environment.verification_policy or _solver._verification_policy(
            environment.permitted_tools
        )
        trusted_sources = {
            tool.name: tool.authoritative_sources
            for tool in environment.permitted_tools
            if tool.authoritative_sources
        }
        kernel = TrustKernel(
            challenge=ChallengeState(
                challenge_id=run_id,
                name=metadata.name,
                attempts_remaining=challenge.attempt_limit,
                revision=challenge.revision,
            ),
            verification_policy=policy,
            trusted_sources=trusted_sources,
        )
        journal.append(
            JournalEvent(
                run_id,
                JournalEventKind.SOLVE_STARTED,
                clock(),
                {"challenge": metadata.name, "category": metadata.category,
                 "tools": registry.available_tools(), "knowledge_augmented": retriever is not None},
            )
        )
        controller = AutonomyController(
            effective_constraints, environment.permitted_tools, journal, run_id, clock, monotonic
        )
        memory = _solver._memory(environment.memory_root)
        brain = SpecialistReasoningSource(
            SpecialistRegistry.default(),
            available_tools=registry.available_tools(),
            memory=memory,
            invocation_guard=controller.allow_specialist_invocation,
            event_sink=lambda kind, payload: _solver._brain_event(journal, run_id, clock, kind, payload),
        )
        verifier_tool = environment.verifier_route.tool if environment.verifier_route else ""
        # Injection hook (additive, default-None => byte-identical to prior behavior): an experiment
        # arm may substitute a different advisory reasoning source (e.g. the translation-backed one).
        # It must expose the same ReasoningSource protocol AND a ``.metrics`` KnowledgeMetrics.
        _factory = reasoning_source_factory or (
            lambda brain, retriever, **kw: KnowledgeAugmentedReasoningSource(brain, retriever, **kw)
        )
        augmented = _factory(
            brain,
            retriever,
            available_tools=registry.available_tools(),
            verifier_tool=verifier_tool,
            flag_format=challenge.flag_format,
            max_retrievals=max_retrievals,
            max_candidates=max_candidates,
            event_sink=lambda kind, payload: journal.append(
                JournalEvent(run_id, JournalEventKind.SPECIALIST_PROPOSAL, clock(), dict(payload, kind=kind))
            ),
        )
        reasoning_source = RoutedReasoningSource(augmented, environment.verifier_route)
        board = HypothesisBoard()
        loop = ReasoningLoop(
            metadata=metadata,
            kernel=kernel,
            adapters=registry,
            planner=ActionPlanner(registry, memory),
            reasoning_source=reasoning_source,
            journal=journal,
            run_id=run_id,
            clock=clock,
            board=board,
            satisfied_prerequisites=set(environment.satisfied_prerequisites),
            trusted_sources_for_disproof=_solver._test_specs(environment.evidence_rules),
            controller=controller,
        )
        state = environment.initial_state or _solver._initial_state(
            challenge, environment.permitted_tools
        )
        loop_result = loop.run(state, max_actions=effective_constraints.max_actions)
        metrics = augmented.metrics
        result = _solver._project_result(
            challenge=challenge,
            understanding=understanding,
            environment=environment,
            run_id=run_id,
            loop_result=loop_result,
            board=board,
            brain=brain,
            controller=controller,
            policy=policy,
            journal=journal,
            clock=clock,
            duration_ms=_solver._duration_ms(started, monotonic),
        )
        return KnowledgeSolveOutput(result=result, knowledge=metrics)
    except Exception as error:  # controlled FAILED terminal state, mirroring frozen solve()
        understanding = understand_challenge(challenge, raw_paths)
        return KnowledgeSolveOutput(
            result=SolveResult(
                status=SolveStatus.FAILED,
                run_id=run_id,
                challenge_name=challenge.name or "unnamed-challenge",
                understanding=understanding,
                terminal_reason=f"orchestration failure: {type(error).__name__}: {error}",
                duration_ms=_solver._duration_ms(started, monotonic),
                journal_path=str(journal.path),
            ),
            knowledge=metrics,
        )
