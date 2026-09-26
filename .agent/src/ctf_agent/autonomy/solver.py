from __future__ import annotations

import math
import re
import time
import uuid
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Tuple

from ..adapters import AdapterRegistry
from ..adapters.base import ToolAdapter
from ..context import ChallengeMetadata
from ..hypothesis_engine import HypothesisBoard
from ..journal import JournalEvent, JournalEventKind, RuntimeJournal
from ..kernel import TrustKernel
from ..loop import LoopOutcome, LoopResult, ReasoningLoop
from ..memory_retrieval import AdvisoryMemory
from ..models import (
    ChallengeState,
    ControlDecision,
    EnvironmentState,
    HypothesisStatus,
    RelevantState,
    TestSpecification,
    VerificationMethod,
    VerificationPolicy,
    VerificationStatus,
)
from ..planner import ActionPlanner
from ..specialists import SpecialistRegistry, SpecialistReasoningSource
from .contracts import (
    ActionTrace,
    BudgetUsage,
    CandidateVerifierRoute,
    ChallengeInput,
    ChallengeResource,
    EnvironmentConfig,
    EvidenceRule,
    EvidenceTrace,
    HypothesisTrace,
    InputFactState,
    KnowledgeSource,
    PermittedTool,
    ResourceKind,
    SolveConstraints,
    SolveResult,
    SolveStatus,
    SpecialistContribution,
)
from .control import AutonomyController
from .reasoning import RoutedReasoningSource
from .resources import materialize_resources
from .understanding import understand_challenge, to_metadata, validate_challenge_input


def solve(
    challenge: ChallengeInput,
    resources: Tuple[ChallengeResource, ...] = (),
    environment: EnvironmentConfig | None = None,
    constraints: SolveConstraints | None = None,
) -> SolveResult:
    """Solve an authorized CTF challenge without human-directed action sequencing.

    The facade composes existing specialists, planner, trusted adapters, and TrustKernel. It never
    executes a tool directly and returns a flag only when the kernel snapshot contains a VERIFIED
    candidate and global STOP.
    """
    public_errors = _public_input_errors(challenge, resources, environment, constraints)
    safe_challenge = _sanitized_challenge(challenge)
    safe_resources = (
        resources
        if isinstance(resources, tuple)
        and all(isinstance(item, ChallengeResource) for item in resources)
        else ()
    )
    safe_environment = (
        environment if isinstance(environment, EnvironmentConfig) else EnvironmentConfig()
    )
    safe_constraints = (
        constraints if isinstance(constraints, SolveConstraints) else SolveConstraints()
    )
    challenge = safe_challenge
    resources = safe_resources
    environment = safe_environment
    constraints = safe_constraints
    clock = environment.clock if callable(environment.clock) else (
        lambda: datetime.now(timezone.utc)
    )
    monotonic = environment.monotonic if callable(environment.monotonic) else time.monotonic
    run_id = environment.run_id or _run_id(challenge.name)
    workspace = (
        environment.workspace_root
        if isinstance(environment.workspace_root, Path)
        else _default_runtime_root() / run_id
    )
    journal_path = (
        environment.journal_path
        if isinstance(environment.journal_path, Path)
        else workspace / "journal.jsonl"
    )
    journal = RuntimeJournal(journal_path)
    started = monotonic()

    raw_paths = tuple(str(resource.path) for resource in resources if resource.path is not None)
    preliminary = understand_challenge(challenge, raw_paths)
    if public_errors:
        return _invalid_result(
            challenge,
            preliminary,
            run_id,
            journal,
            clock,
            started,
            monotonic,
            (*public_errors, *_validate_constraints(constraints)),
        )
    errors = (
        *validate_challenge_input(challenge, resources),
        *_validate_constraints(constraints),
    )
    if errors:
        return _invalid_result(
            challenge, preliminary, run_id, journal, clock, started, monotonic, errors
        )

    try:
        resource_paths = materialize_resources(resources, workspace)
        missing = tuple(path for path in resource_paths if not Path(path).exists())
        if missing:
            return _invalid_result(
                challenge,
                understand_challenge(challenge, resource_paths),
                run_id,
                journal,
                clock,
                started,
                monotonic,
                tuple(f"resource path does not exist: {path}" for path in missing),
            )
        understanding = understand_challenge(challenge, resource_paths)
        metadata = to_metadata(challenge, understanding, resource_paths)
        registry = _adapter_registry(environment.permitted_tools)
        effective_constraints = _apply_attempt_limit(constraints, challenge.attempt_limit)
        policy = environment.verification_policy or _verification_policy(
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
                {
                    "challenge": metadata.name,
                    "category": metadata.category,
                    "resources": resource_paths,
                    "tools": registry.available_tools(),
                },
            )
        )
        journal.append(
            JournalEvent(
                run_id,
                JournalEventKind.CONTEXT_UPDATED,
                clock(),
                {
                    "likely_categories": understanding.likely_categories,
                    "unknowns": understanding.unknowns,
                    "attack_surfaces": understanding.attack_surfaces,
                },
            )
        )
        controller = AutonomyController(
            effective_constraints,
            environment.permitted_tools,
            journal,
            run_id,
            clock,
            monotonic,
        )
        memory = _memory(environment.memory_root)
        brain = SpecialistReasoningSource(
            SpecialistRegistry.default(),
            available_tools=registry.available_tools(),
            memory=memory,
            invocation_guard=controller.allow_specialist_invocation,
            event_sink=lambda kind, payload: _brain_event(
                journal, run_id, clock, kind, payload
            ),
        )
        reasoning_source = RoutedReasoningSource(brain, environment.verifier_route)
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
            trusted_sources_for_disproof=_test_specs(environment.evidence_rules),
            controller=controller,
        )
        state = environment.initial_state or _initial_state(
            challenge, environment.permitted_tools
        )
        loop_result = loop.run(state, max_actions=effective_constraints.max_actions)
        return _project_result(
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
            duration_ms=_duration_ms(started, monotonic),
        )
    except Exception as error:
        # A raised adapter/composition error is a controlled FAILED terminal state. Classified
        # tool/environment failures normally do not raise and remain branch evidence instead.
        understanding = understand_challenge(challenge, raw_paths)
        journal.append(
            JournalEvent(
                run_id,
                JournalEventKind.SOLVE_FINISHED,
                clock(),
                {"status": SolveStatus.FAILED.value, "reason": str(error)},
            )
        )
        return SolveResult(
            status=SolveStatus.FAILED,
            run_id=run_id,
            challenge_name=challenge.name or "unnamed-challenge",
            understanding=understanding,
            terminal_reason=f"orchestration failure: {type(error).__name__}: {error}",
            duration_ms=_duration_ms(started, monotonic),
            journal_path=str(journal.path),
        )


def _project_result(
    *,
    challenge: ChallengeInput,
    understanding,
    environment: EnvironmentConfig,
    run_id: str,
    loop_result: LoopResult,
    board: HypothesisBoard,
    brain: SpecialistReasoningSource,
    controller: AutonomyController,
    policy: VerificationPolicy,
    journal: RuntimeJournal,
    clock,
    duration_ms: int,
) -> SolveResult:
    snapshot = loop_result.context.snapshot
    verified = tuple(
        candidate
        for candidate in snapshot.candidates
        if candidate.verification_status is VerificationStatus.VERIFIED
    )
    solved = bool(verified and snapshot.verification.decision is ControlDecision.STOP)
    status = _solve_status(loop_result.outcome, solved, controller.terminal_reason)
    candidate = verified[0] if solved else None
    actions = _action_traces(loop_result, environment.permitted_tools)
    evidence = tuple(_evidence_trace(item) for item in snapshot.evidence)
    hypotheses = _hypothesis_traces(board)
    contributions = _specialist_contributions(brain)
    reason = controller.terminal_reason or _terminal_reason(loop_result.outcome, solved)
    journal.append(
        JournalEvent(
            run_id,
            JournalEventKind.SOLVE_FINISHED,
            clock(),
            {
                "status": status.value,
                "reason": reason,
                "actions": len(actions),
                "verified": solved,
            },
        )
    )
    blockers = tuple(
        h.hypothesis_id
        for h in board.all_hypotheses()
        if h.status is HypothesisStatus.UNRESOLVED
    )
    remaining = tuple(
        h.hypothesis_id
        for h in board.open_hypotheses()
    )
    return SolveResult(
        status=status,
        run_id=run_id,
        challenge_name=challenge.name or "unnamed-challenge",
        understanding=understanding,
        terminal_reason=reason,
        verified_flag=candidate.value if candidate else None,
        verification_evidence_ids=candidate.supporting_evidence if candidate else (),
        final_verification_method=_verification_method(loop_result, policy) if candidate else None,
        solution_path_summary=_solution_summary(actions, hypotheses, solved),
        actions=actions,
        key_hypotheses=hypotheses,
        specialist_contributions=contributions,
        important_evidence=evidence,
        remaining_hypotheses=remaining,
        unresolved_blockers=blockers,
        budget_usage=controller.usage,
        knowledge_sources=_knowledge_sources(contributions, bool(evidence), bool(snapshot.evidence)),
        reasoning_iterations=controller.usage.iterations,
        duration_ms=duration_ms,
        journal_path=str(journal.path),
    )


def _adapter_registry(tools: Tuple[PermittedTool, ...]) -> AdapterRegistry:
    registry = AdapterRegistry()
    seen = set()
    for tool in tools:
        if not tool.name.strip():
            raise ValueError("permitted tool name must be non-empty")
        if tool.name in seen:
            raise ValueError(f"duplicate permitted tool: {tool.name}")
        if tool.cost < 0:
            raise ValueError(f"tool cost must be non-negative: {tool.name}")
        if not isinstance(tool.adapter, ToolAdapter):
            raise ValueError(f"tool adapter does not satisfy ToolAdapter: {tool.name}")
        if tool.adapter.name != tool.name:
            raise ValueError(
                f"permitted tool name '{tool.name}' does not match adapter '{tool.adapter.name}'"
            )
        seen.add(tool.name)
        registry.register(tool.adapter)
    return registry


def _verification_policy(tools: Tuple[PermittedTool, ...]) -> VerificationPolicy:
    return VerificationPolicy(
        authoritative_output_tools=tuple(t.name for t in tools if t.authoritative_output),
        verifier_tools=tuple(t.name for t in tools if t.verifier),
        deterministic_tools=tuple(t.name for t in tools if t.deterministic),
    )


def _test_specs(rules) -> dict[str, TestSpecification]:
    return {
        rule.hypothesis_id: TestSpecification(
            hypothesis_id=rule.hypothesis_id,
            supporting_body_contains=rule.supporting_body_contains,
            contradicting_body_contains=rule.contradicting_body_contains,
            authoritative_sources=rule.authoritative_sources,
            prerequisites_met=rule.prerequisites_met,
        )
        for rule in rules
    }


def _initial_state(
    challenge: ChallengeInput, tools: Tuple[PermittedTool, ...]
) -> RelevantState:
    return RelevantState(
        environment=EnvironmentState(
            revision="initial",
            available_tools=tuple(sorted(tool.name for tool in tools)),
            network_available=any(tool.network for tool in tools),
        ),
        authentication_context="challenge-credentials" if challenge.credentials else "guest",
        session_context="initial",
        challenge_revision=challenge.revision,
    )


def _memory(configured: Path | None) -> AdvisoryMemory | None:
    root = configured or (_default_agent_root().parent / ".agent_audit")
    return AdvisoryMemory(root) if root.is_dir() else None


def _action_traces(
    result: LoopResult, tools: Tuple[PermittedTool, ...]
) -> Tuple[ActionTrace, ...]:
    costs = {tool.name: tool.cost for tool in tools}
    return tuple(
        ActionTrace(
            action_id=item.action.action_id,
            objective=item.action.objective,
            tool=item.action.tool,
            target=item.action.target,
            result_class=item.classification.result_class.value if item.classification else "",
            impact=item.impact.value,
            decision=item.decision.value,
            cost=max(1, costs.get(item.action.tool, 1)),
        )
        for item in result.pipeline_results
    )


def _evidence_trace(evidence) -> EvidenceTrace:
    return EvidenceTrace(
        evidence_id=evidence.evidence_id,
        source=evidence.source,
        result_class=evidence.result_class.value,
        status=evidence.status.value,
        affected_hypotheses=evidence.affected_hypotheses,
        provenance=f"{evidence.provenance.origin.value}:{evidence.provenance.locator}",
    )


def _hypothesis_traces(board: HypothesisBoard) -> Tuple[HypothesisTrace, ...]:
    return tuple(
        HypothesisTrace(
            hypothesis_id=hypothesis.hypothesis_id,
            statement=hypothesis.statement,
            status=hypothesis.status.value,
            supporting_evidence=hypothesis.supporting_evidence,
            conflicting_evidence=hypothesis.contradicting_evidence,
            unresolved_evidence=hypothesis.unresolved_evidence,
            priority=board.meta(hypothesis.hypothesis_id).priority,
        )
        for hypothesis in board.all_hypotheses()
    )


def _specialist_contributions(
    brain: SpecialistReasoningSource,
) -> Tuple[SpecialistContribution, ...]:
    contributions = []
    seen = set()
    for batch in brain.analysis_history:
        for analysis in batch:
            key = (
                analysis.specialist,
                tuple(h.hypothesis_id for h in analysis.hypotheses),
                tuple(a.objective for a in analysis.candidate_actions),
            )
            if key in seen:
                continue
            seen.add(key)
            contributions.append(
                SpecialistContribution(
                    specialist=analysis.specialist,
                    relevance=analysis.relevance,
                    hypotheses=key[1],
                    proposed_actions=key[2],
                    memory_references=analysis.relevant_memory_refs,
                    reasoning_summary=analysis.reasoning_summary,
                )
            )
    return tuple(contributions)


def _verification_method(result: LoopResult, policy: VerificationPolicy) -> str:
    for item in reversed(result.pipeline_results):
        if item.verification is None or item.decision is not ControlDecision.STOP:
            continue
        execution = item.observation.execution if item.observation else None
        if execution is None:
            continue
        if execution.tool in policy.verifier_tools:
            return VerificationMethod.AUTHORITATIVE_VERIFIER.value
        if execution.tool in policy.deterministic_tools:
            return str(
                execution.metadata.get(
                    "verification_method", VerificationMethod.DETERMINISTIC_DERIVATION.value
                )
            )
        if execution.tool in policy.authoritative_output_tools:
            return VerificationMethod.AUTHORITATIVE_OUTPUT.value
    return VerificationMethod.SUPPORTING_ANALYSIS.value


def _solve_status(
    outcome: LoopOutcome, solved: bool, controller_reason: str
) -> SolveStatus:
    if solved:
        return SolveStatus.SOLVED
    if outcome is LoopOutcome.TIMEOUT:
        return SolveStatus.TIMEOUT
    if outcome is LoopOutcome.BUDGET_EXHAUSTED or "budget exhausted" in controller_reason:
        return SolveStatus.EXHAUSTED
    return SolveStatus.BLOCKED


def _terminal_reason(outcome: LoopOutcome, solved: bool) -> str:
    if solved:
        return "verified candidate reached kernel STOP"
    return {
        LoopOutcome.BLOCKED_NO_ACTIONS: "no useful validated action remains",
        LoopOutcome.BLOCKED_PREREQUISITES: "all useful actions are blocked by prerequisites",
        LoopOutcome.BUDGET_EXHAUSTED: "action budget exhausted",
        LoopOutcome.TIMEOUT: "wall-clock timeout reached",
        LoopOutcome.VERIFIED: "kernel reported STOP without a verified candidate",
    }[outcome]


def _solution_summary(
    actions: Tuple[ActionTrace, ...], hypotheses: Tuple[HypothesisTrace, ...], solved: bool
) -> str:
    action_path = " -> ".join(
        f"{action.objective} [{action.result_class or 'no-result'}]" for action in actions
    ) or "no action executed"
    supported = tuple(h.hypothesis_id for h in hypotheses if h.status == "SUPPORTED")
    result = "verified flag" if solved else "no verified flag"
    return f"{action_path}; supported={supported}; terminal={result}"


def _knowledge_sources(
    contributions: Tuple[SpecialistContribution, ...],
    has_evidence: bool,
    has_artifact_evidence: bool,
) -> Tuple[KnowledgeSource, ...]:
    sources = [KnowledgeSource.DIRECT_MECHANISM_REASONING]
    if contributions:
        sources.append(KnowledgeSource.SPECIALIST_KNOWLEDGE)
    if any(c.memory_references for c in contributions):
        sources.append(KnowledgeSource.EXISTING_MEMORY)
    if has_artifact_evidence or has_evidence:
        sources.append(KnowledgeSource.CHALLENGE_ARTIFACT)
    if contributions:
        sources.append(KnowledgeSource.KNOWN_TECHNIQUE)
    return tuple(dict.fromkeys(sources))


def _brain_event(journal, run_id, clock, kind, payload) -> None:
    try:
        event_kind = JournalEventKind(kind)
    except ValueError:
        return
    journal.append(JournalEvent(run_id, event_kind, clock(), payload))


def _sanitized_challenge(value) -> ChallengeInput:
    if not isinstance(value, ChallengeInput):
        return ChallengeInput()
    return ChallengeInput(
        name=value.name if isinstance(value.name, str) else None,
        category=value.category if isinstance(value.category, str) else None,
        description=value.description if isinstance(value.description, str) else None,
        points=value.points if isinstance(value.points, int) and not isinstance(value.points, bool) else None,
        solves=value.solves if isinstance(value.solves, int) and not isinstance(value.solves, bool) else None,
        hints=value.hints
        if isinstance(value.hints, tuple) and all(isinstance(item, str) for item in value.hints)
        else (),
        flag_format=value.flag_format if isinstance(value.flag_format, str) else None,
        urls=value.urls
        if isinstance(value.urls, tuple) and all(isinstance(item, str) for item in value.urls)
        else (),
        credentials=value.credentials if isinstance(value.credentials, Mapping) else {},
        attempt_limit=value.attempt_limit
        if isinstance(value.attempt_limit, int) and not isinstance(value.attempt_limit, bool)
        else None,
        known_constraints=value.known_constraints
        if isinstance(value.known_constraints, tuple)
        and all(isinstance(item, str) for item in value.known_constraints)
        else (),
        revision=value.revision if isinstance(value.revision, str) else "initial",
    )


def _public_input_errors(challenge, resources, environment, constraints) -> Tuple[str, ...]:
    errors = []
    if not isinstance(challenge, ChallengeInput):
        errors.append("challenge must be ChallengeInput")
    if not isinstance(resources, tuple) or not all(
        isinstance(item, ChallengeResource) for item in resources
    ):
        errors.append("resources must be a tuple of ChallengeResource")
    elif isinstance(resources, tuple):
        for resource in resources:
            if not isinstance(resource.resource_id, str):
                errors.append("resource_id must be a string")
            if not isinstance(resource.kind, ResourceKind):
                errors.append(f"resource kind is invalid: {resource.resource_id}")
            if resource.path is not None and not isinstance(resource.path, Path):
                errors.append(f"resource path must be pathlib.Path: {resource.resource_id}")
            if resource.content is not None and not isinstance(resource.content, (bytes, str)):
                errors.append(f"resource content must be bytes or str: {resource.resource_id}")
            if not isinstance(resource.filename, str):
                errors.append(f"resource filename must be a string: {resource.resource_id}")
    if environment is not None and not isinstance(environment, EnvironmentConfig):
        errors.append("environment must be EnvironmentConfig")
    if constraints is not None and not isinstance(constraints, SolveConstraints):
        errors.append("constraints must be SolveConstraints")
    if isinstance(challenge, ChallengeInput):
        integer_fields = {
            "points": challenge.points,
            "solves": challenge.solves,
            "attempt_limit": challenge.attempt_limit,
        }
        for name, value in integer_fields.items():
            if value is not None and (not isinstance(value, int) or isinstance(value, bool)):
                errors.append(f"{name} must be an integer")
        if challenge.name is not None and not isinstance(challenge.name, str):
            errors.append("name must be a string")
        if challenge.category is not None and not isinstance(challenge.category, str):
            errors.append("category must be a string")
        if challenge.description is not None and not isinstance(challenge.description, str):
            errors.append("description must be a string")
        if challenge.flag_format is not None and not isinstance(challenge.flag_format, str):
            errors.append("flag_format must be a string")
        if not isinstance(challenge.urls, tuple) or not all(
            isinstance(item, str) for item in challenge.urls
        ):
            errors.append("urls must be a tuple of strings")
        if not isinstance(challenge.hints, tuple) or not all(
            isinstance(item, str) for item in challenge.hints
        ):
            errors.append("hints must be a tuple of strings")
        if not isinstance(challenge.credentials, Mapping) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in challenge.credentials.items()
        ):
            errors.append("credentials must map strings to strings")
        if not isinstance(challenge.known_constraints, tuple) or not all(
            isinstance(item, str) for item in challenge.known_constraints
        ):
            errors.append("known_constraints must be a tuple of strings")
        if not isinstance(challenge.revision, str):
            errors.append("revision must be a string")
    if isinstance(environment, EnvironmentConfig):
        if not isinstance(environment.permitted_tools, tuple) or not all(
            isinstance(item, PermittedTool) for item in environment.permitted_tools
        ):
            errors.append("permitted_tools must be a tuple of PermittedTool")
        if not isinstance(environment.evidence_rules, tuple) or not all(
            isinstance(item, EvidenceRule) for item in environment.evidence_rules
        ):
            errors.append("evidence_rules must be a tuple of EvidenceRule")
        if environment.verifier_route is not None and not isinstance(
            environment.verifier_route, CandidateVerifierRoute
        ):
            errors.append("verifier_route must be CandidateVerifierRoute")
        if environment.initial_state is not None and not isinstance(
            environment.initial_state, RelevantState
        ):
            errors.append("initial_state must be RelevantState")
        if not isinstance(environment.satisfied_prerequisites, tuple) or not all(
            isinstance(item, str) and item.strip()
            for item in environment.satisfied_prerequisites
        ):
            errors.append("satisfied_prerequisites must be a tuple of non-empty strings")
        if environment.clock is not None and not callable(environment.clock):
            errors.append("clock must be callable")
        if environment.monotonic is not None and not callable(environment.monotonic):
            errors.append("monotonic must be callable")
        for name, value in (
            ("workspace_root", environment.workspace_root),
            ("journal_path", environment.journal_path),
            ("memory_root", environment.memory_root),
        ):
            if value is not None and not isinstance(value, Path):
                errors.append(f"{name} must be a pathlib.Path")
    return tuple(errors)


def _validate_constraints(constraints: SolveConstraints) -> Tuple[str, ...]:
    errors = []
    for name, value in constraints.__dict__.items():
        if name == "timeout_seconds":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append("timeout_seconds must be numeric")
            elif not math.isfinite(float(value)) or value <= 0:
                errors.append("timeout_seconds must be finite and positive")
            continue
        if not isinstance(value, int) or isinstance(value, bool):
            errors.append(f"{name} must be an integer")
        elif value < 0:
            errors.append(f"{name} must be non-negative")
    return tuple(errors)


def _apply_attempt_limit(
    constraints: SolveConstraints, attempt_limit: int | None
) -> SolveConstraints:
    if attempt_limit is None:
        return constraints
    return replace(
        constraints,
        max_submissions=min(constraints.max_submissions, attempt_limit),
        max_remote_attempts=min(constraints.max_remote_attempts, attempt_limit),
    )


def _invalid_result(
    challenge,
    understanding,
    run_id,
    journal,
    clock,
    started,
    monotonic,
    errors,
) -> SolveResult:
    reason = "; ".join(errors)
    journal.append(
        JournalEvent(
            run_id,
            JournalEventKind.SOLVE_FINISHED,
            clock(),
            {"status": SolveStatus.INVALID_INPUT.value, "reason": reason},
        )
    )
    return SolveResult(
        status=SolveStatus.INVALID_INPUT,
        run_id=run_id,
        challenge_name=challenge.name or "unnamed-challenge",
        understanding=understanding,
        terminal_reason=reason,
        duration_ms=_duration_ms(started, monotonic),
        journal_path=str(journal.path),
    )


def _run_id(name: str | None) -> str:
    stem = re.sub(r"[^a-z0-9]+", "-", (name or "challenge").lower()).strip("-")
    return f"{stem or 'challenge'}-{uuid.uuid4().hex[:12]}"


def _duration_ms(started: float, monotonic) -> int:
    return max(0, int((monotonic() - started) * 1000))


def _default_agent_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _default_runtime_root() -> Path:
    return _default_agent_root() / "runtime"
