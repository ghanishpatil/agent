"""AgentSession — the production runtime entrypoint.

It composes EXACTLY the frozen ``solve()`` pipeline (reusing the frozen ``_solver`` helper
functions verbatim) and substitutes only the reasoning source: an ``LLMReasoningSource`` wrapping
the frozen deterministic ``SpecialistReasoningSource``, still wrapped by the frozen
``RoutedReasoningSource``. It duplicates none of the loop/kernel/planner logic — every action is
driven by ``ReasoningLoop.run(...)``.

Stepping: ``ReasoningLoop`` persists its board/kernel/fingerprints/prerequisites on ``self`` across
calls, so a single ``AgentSession`` holds ONE loop and advances it one action per ``step()`` via
``loop.run(state, max_actions=1)``. Terminal is detected from ``is_verified()`` and from whether a
new pipeline result was produced (a max_actions=1 run reports BUDGET_EXHAUSTED even mid-solve, so
its outcome is not used for termination). ``run()`` repeats ``step()`` until terminal or budget.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from ctf_agent.autonomy import solver as _solver
from ctf_agent.autonomy.contracts import (
    ChallengeInput,
    ChallengeResource,
    EnvironmentConfig,
    SolveConstraints,
    SolveResult,
)
from ctf_agent.autonomy.control import AutonomyController
from ctf_agent.autonomy.reasoning import RoutedReasoningSource
from ctf_agent.autonomy.resources import materialize_resources
from ctf_agent.autonomy.understanding import understand_challenge, to_metadata
from ctf_agent.context import build_context
from ctf_agent.hypothesis_engine import HypothesisBoard
from ctf_agent.journal import JournalEvent, JournalEventKind, RuntimeJournal
from ctf_agent.kernel import TrustKernel
from ctf_agent.loop import ReasoningLoop
from ctf_agent.models import ChallengeState
from ctf_agent.planner import ActionPlanner
from ctf_agent.specialists import SpecialistRegistry, SpecialistReasoningSource

from .journal import RuntimeSessionJournal
from .llm_client import LLMClient
from .reasoning_source import LLMReasoningSource
from .routing import ModelRouter


@dataclass(frozen=True)
class StepReport:
    step_index: int
    executed: bool
    model: str
    escalation_reason: str
    action_tool: Optional[str]
    action_objective: Optional[str]
    planner_decision: Optional[str]
    observation_class: Optional[str]
    impact: Optional[str]
    hypothesis_id: Optional[str]
    hypothesis_state: Optional[str]
    verified: bool


class AgentSession:
    """Thin runtime API around the frozen reasoning loop. The LLM is the reasoning source; the
    agent owns all execution, verification, and state."""

    def __init__(
        self,
        challenge: ChallengeInput,
        *,
        llm_client: Optional[LLMClient] = None,
        environment: Optional[EnvironmentConfig] = None,
        constraints: Optional[SolveConstraints] = None,
        resources: Tuple[ChallengeResource, ...] = (),
        router: Optional[ModelRouter] = None,
        session_journal_path: Optional[Path] = None,
        use_specialist_base: bool = True,
        inner_reasoning_source: Optional[object] = None,
    ) -> None:
        self._challenge = challenge
        self._client = llm_client
        # Optional Architecture-A hook: an externally-driven reasoning source (e.g. a queued source
        # filled by Kiro via ctf_propose) replaces the internal LLMReasoningSource. It is still
        # wrapped by the frozen RoutedReasoningSource and governed by the frozen pipeline.
        self._inner_reasoning_source = inner_reasoning_source
        self._environment = environment if isinstance(environment, EnvironmentConfig) else EnvironmentConfig()
        self._constraints = constraints if isinstance(constraints, SolveConstraints) else SolveConstraints()
        self._resources = resources
        self._router = router or ModelRouter()
        self._session_journal_path = session_journal_path
        self._use_specialist_base = use_specialist_base

        self._started = False
        self._steps = 0
        self._executed = 0
        self._state = None
        self._loop: Optional[ReasoningLoop] = None
        self._kernel: Optional[TrustKernel] = None
        self._board: Optional[HypothesisBoard] = None
        self._controller: Optional[AutonomyController] = None
        self._brain: Optional[SpecialistReasoningSource] = None
        self._llm_source: Optional[LLMReasoningSource] = None
        self._metadata = None
        self._understanding = None
        self._policy = None
        self._run_id = ""
        self._journal: Optional[RuntimeJournal] = None
        self._session_journal: Optional[RuntimeSessionJournal] = None
        self._last_loop_result = None
        self._clock: Callable[[], datetime] = (
            self._environment.clock if callable(self._environment.clock)
            else (lambda: datetime.now(timezone.utc))
        )
        self._monotonic = (
            self._environment.monotonic if callable(self._environment.monotonic) else time.monotonic
        )
        self._start_monotonic = 0.0

    # -- lifecycle --------------------------------------------------------------------------
    def start(self) -> "AgentSession":
        if self._started:
            return self
        env = self._environment
        challenge = self._challenge
        self._run_id = env.run_id or _solver._run_id(challenge.name)
        workspace = env.workspace_root if isinstance(env.workspace_root, Path) else (
            _solver._default_runtime_root() / self._run_id
        )
        journal_path = env.journal_path if isinstance(env.journal_path, Path) else workspace / "journal.jsonl"
        self._journal = RuntimeJournal(journal_path)
        self._start_monotonic = self._monotonic()

        resource_paths = materialize_resources(self._resources, workspace)
        self._understanding = understand_challenge(challenge, resource_paths)
        self._metadata = to_metadata(challenge, self._understanding, resource_paths)

        registry = _solver._adapter_registry(env.permitted_tools)
        effective_constraints = _solver._apply_attempt_limit(self._constraints, challenge.attempt_limit)
        self._effective_constraints = effective_constraints
        self._policy = env.verification_policy or _solver._verification_policy(env.permitted_tools)
        trusted_sources = {
            t.name: t.authoritative_sources for t in env.permitted_tools if t.authoritative_sources
        }
        self._kernel = TrustKernel(
            challenge=ChallengeState(
                challenge_id=self._run_id,
                name=self._metadata.name,
                attempts_remaining=challenge.attempt_limit,
                revision=challenge.revision,
            ),
            verification_policy=self._policy,
            trusted_sources=trusted_sources,
        )
        self._journal.append(
            JournalEvent(
                self._run_id, JournalEventKind.SOLVE_STARTED, self._clock(),
                {"challenge": self._metadata.name, "category": self._metadata.category,
                 "tools": registry.available_tools(), "runtime": "AgentSession",
                 "reasoning_source": "LLMReasoningSource"},
            )
        )
        self._controller = AutonomyController(
            effective_constraints, env.permitted_tools, self._journal, self._run_id,
            self._clock, self._monotonic,
        )
        memory = _solver._memory(env.memory_root)
        self._brain = SpecialistReasoningSource(
            SpecialistRegistry.default(),
            available_tools=registry.available_tools(),
            memory=memory,
            invocation_guard=self._controller.allow_specialist_invocation,
            event_sink=lambda kind, payload: _solver._brain_event(
                self._journal, self._run_id, self._clock, kind, payload
            ),
        )
        if self._inner_reasoning_source is not None:
            # Architecture A: the injected source is authoritative reasoning input. Give it the
            # registry (for propose-time tool validation) if it supports attach().
            self._llm_source = self._inner_reasoning_source
            attach = getattr(self._llm_source, "attach", None)
            if callable(attach):
                attach(registry)
        else:
            if self._client is None:
                raise ValueError("AgentSession requires an llm_client unless inner_reasoning_source is provided")
            self._llm_source = LLMReasoningSource(
                self._client,
                adapters=registry,
                router=self._router,
                base=self._brain if self._use_specialist_base else None,
                flag_format=challenge.flag_format or "",
                event_sink=lambda kind, payload: _solver._brain_event(
                    self._journal, self._run_id, self._clock, kind, payload
                ),
            )
        reasoning_source = RoutedReasoningSource(self._llm_source, env.verifier_route)
        self._board = HypothesisBoard()
        self._loop = ReasoningLoop(
            metadata=self._metadata,
            kernel=self._kernel,
            adapters=registry,
            planner=ActionPlanner(registry, memory),
            reasoning_source=reasoning_source,
            journal=self._journal,
            run_id=self._run_id,
            clock=self._clock,
            board=self._board,
            satisfied_prerequisites=set(env.satisfied_prerequisites),
            trusted_sources_for_disproof=_solver._test_specs(env.evidence_rules),
            controller=self._controller,
        )
        self._state = env.initial_state or _solver._initial_state(challenge, env.permitted_tools)
        self._session_journal = RuntimeSessionJournal(
            path=self._session_journal_path, challenge_id=self._run_id
        )
        self._started = True
        return self

    def step(self) -> StepReport:
        """Advance the frozen loop by one action; record a runtime-journal entry."""
        if not self._started:
            self.start()
        before = len(self._last_loop_result.pipeline_results) if self._last_loop_result else 0
        self._last_loop_result = self._loop.run(self._state, max_actions=1)
        self._steps += 1
        results = self._last_loop_result.pipeline_results
        executed = len(results) > before
        route = self._llm_source.last_route
        model = route.model if route else ""
        escalation = route.escalation_reason if route else ""
        if executed:
            self._executed += 1
            pr = results[-1]
            self._session_journal.record_step(
                pipeline_result=pr, model=model, escalation_reason=escalation,
                timestamp=self._clock().isoformat(),
            )
            return StepReport(
                step_index=self._steps, executed=True, model=model, escalation_reason=escalation,
                action_tool=pr.action.tool, action_objective=pr.action.objective,
                planner_decision=pr.decision.value,
                observation_class=pr.classification.result_class.value if pr.classification else None,
                impact=pr.impact.value,
                hypothesis_id=pr.hypothesis.hypothesis_id if pr.hypothesis else None,
                hypothesis_state=pr.hypothesis.status.value if pr.hypothesis else None,
                verified=self.is_verified(),
            )
        return StepReport(
            step_index=self._steps, executed=False, model=model, escalation_reason=escalation,
            action_tool=None, action_objective=None, planner_decision=None,
            observation_class=None, impact=None, hypothesis_id=None, hypothesis_state=None,
            verified=self.is_verified(),
        )

    def run(self, max_steps: Optional[int] = None) -> SolveResult:
        """Repeat step() until verified, blocked (no new action), or budget reached; then project."""
        if not self._started:
            self.start()
        cap = max_steps if max_steps is not None else self._effective_constraints.max_actions
        while self._steps < cap:
            if self.is_verified():
                break
            report = self.step()
            if self.is_verified():
                break
            if not report.executed:
                break  # loop could not produce a validated action -> terminal (blocked)
        return self.get_result()

    # -- read-only inspection ---------------------------------------------------------------
    @property
    def adapter_registry(self):
        """The trusted AdapterRegistry for this session (for propose-time tool validation)."""
        return self._loop.adapters if self._loop is not None else None

    @property
    def metadata(self):
        return self._metadata

    def _context(self):
        return build_context(self._metadata, self._kernel, self._board)

    def get_state(self) -> dict:
        ctx = self._context()
        return {
            "run_id": self._run_id,
            "steps": self._steps,
            "actions_executed": self._executed,
            "verified": self.is_verified(),
            "hypotheses": self.get_hypotheses(),
            "evidence": self.get_evidence(),
            "last_model": self._llm_source.last_route.model if self._llm_source and self._llm_source.last_route else None,
        }

    def get_hypotheses(self) -> List[dict]:
        ctx = self._context()
        return [
            {
                "hypothesis_id": v.hypothesis.hypothesis_id,
                "statement": v.hypothesis.statement,
                "state": v.state.value,
                "status": v.hypothesis.status.value,
                "evidence_count": v.evidence_count,
            }
            for v in ctx.hypothesis_views()
        ]

    def get_evidence(self) -> List[dict]:
        ctx = self._context()
        return [
            {
                "evidence_id": e.evidence_id,
                "result_class": e.result_class.value,
                "status": e.status.value,
                "affects": list(e.affected_hypotheses),
                "source": e.source,
            }
            for e in ctx.snapshot.evidence
        ]

    def recent_observations(self, limit: int = 6) -> List[dict]:
        """Recent observation bodies (stdout+response_body, truncated) so an external reasoner can
        read what the trusted adapters actually returned. Read-only projection."""
        ctx = self._context()
        out: List[dict] = []
        for e in ctx.snapshot.evidence[-limit:]:
            ex = e.observation.execution
            body = " ".join((ex.stdout or "", ex.response_body or "")).strip()
            out.append({
                "evidence_id": e.evidence_id, "source": e.source,
                "result_class": e.result_class.value, "status": e.status.value,
                "output": body[:800],
            })
        return out

    def get_pending_actions(self) -> List[dict]:
        """The validated action proposals the reasoning source produced for the current context."""
        if self._llm_source is None:
            return []
        ctx = self._context()
        actions = self._loop.reasoning_source.suggest_actions(ctx)
        return [
            {"hypothesis_id": a.hypothesis_id, "objective": a.objective, "tool": a.tool,
             "target": a.target, "candidate_flag": a.candidate_flag}
            for a in actions
        ]

    def is_verified(self) -> bool:
        if self._kernel is None:
            return False
        return self._context().is_verified()

    def get_flag(self) -> Optional[str]:
        ctx = self._context()
        from ctf_agent.models import VerificationStatus, ControlDecision
        verified = [c for c in ctx.snapshot.candidates if c.verification_status is VerificationStatus.VERIFIED]
        if verified and ctx.snapshot.verification.decision is ControlDecision.STOP:
            return verified[0].value
        return None

    def get_result(self) -> SolveResult:
        if self._last_loop_result is None:
            # nothing ran yet — run a full pass
            self._last_loop_result = self._loop.run(self._state, max_actions=self._effective_constraints.max_actions)
        return _solver._project_result(
            challenge=self._challenge,
            understanding=self._understanding,
            environment=self._environment,
            run_id=self._run_id,
            loop_result=self._last_loop_result,
            board=self._board,
            brain=self._brain,
            controller=self._controller,
            policy=self._policy,
            journal=self._journal,
            clock=self._clock,
            duration_ms=_solver._duration_ms(self._start_monotonic, self._monotonic),
        )

    # -- observability accessors ------------------------------------------------------------
    def session_journal_records(self) -> List[dict]:
        return list(self._session_journal.records) if self._session_journal else []

    def route_history(self) -> List[dict]:
        return [d.to_dict() for d in self._llm_source.route_history] if self._llm_source else []

    def proposal_rejections(self) -> List[str]:
        return list(self._llm_source.rejections) if self._llm_source else []
