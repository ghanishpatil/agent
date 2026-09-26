from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime

from .classifier import classify_result
from .deduplication import ActionRegistry, fingerprint_action
from .evidence import EvidenceManager
from .hypothesis import apply_evidence
from .impact import determine_impact
from .models import (
    Action,
    ChallengeState,
    ControlDecision,
    Evidence,
    ExecutionResult,
    FlagCandidate,
    Hypothesis,
    HypothesisImpact,
    ImpactContext,
    Observation,
    ResultClassification,
    TestSpecification,
    VerificationDecision,
    VerificationPolicy,
    VerificationState,
)
from .verification import FlagAttemptRegistry, VerificationController


@dataclass(frozen=True)
class PipelineResult:
    action: Action
    decision: ControlDecision
    hypothesis: Hypothesis
    observation: Observation | None = None
    classification: ResultClassification | None = None
    evidence: Evidence | None = None
    impact: HypothesisImpact = HypothesisImpact.NO_IMPACT
    verification: VerificationDecision | None = None


@dataclass(frozen=True)
class KernelSnapshot:
    challenge: ChallengeState | None
    hypotheses: tuple[Hypothesis, ...]
    evidence: tuple[Evidence, ...]
    candidates: tuple[FlagCandidate, ...]
    verification: VerificationState


class TrustKernel:
    """Atomic trust transition. It does not execute tools or choose actions."""

    def __init__(
        self,
        *,
        challenge: ChallengeState | None = None,
        verification_policy: VerificationPolicy | None = None,
        trusted_sources: dict[str, tuple[str, ...]] | None = None,
    ) -> None:
        self.actions = ActionRegistry()
        self.evidence = EvidenceManager()
        self.verifier = VerificationController(
            self.evidence, verification_policy or VerificationPolicy()
        )
        self.flag_attempts = FlagAttemptRegistry(self.evidence)
        self._challenge = challenge
        self._hypotheses: dict[str, Hypothesis] = {}
        self._candidates: dict[str, FlagCandidate] = {}
        self._verification = VerificationState()
        self._trusted_sources = {
            tool: tuple(sources) for tool, sources in (trusted_sources or {}).items()
        }
        self._test_specs: dict[str, TestSpecification] = {}
        self._test_by_hypothesis: dict[str, str] = {}

    def register_test(self, action: Action, specification: TestSpecification) -> None:
        fingerprint = fingerprint_action(action)
        self._test_specs[fingerprint] = specification
        self._test_by_hypothesis[specification.hypothesis_id] = fingerprint

    def test_fingerprint(self, hypothesis_id: str) -> str:
        return self._test_by_hypothesis[hypothesis_id]

    def snapshot(self) -> KernelSnapshot:
        return KernelSnapshot(
            challenge=self._challenge,
            hypotheses=tuple(self._hypotheses.values()),
            evidence=self.evidence.records,
            candidates=tuple(self._candidates.values()),
            verification=self._verification,
        )

    def process(
        self,
        *,
        action: Action,
        execution: ExecutionResult,
        hypothesis: Hypothesis,
        observed_at: datetime,
        source: str,
        candidate: FlagCandidate | None = None,
        candidate_evidence_ids: tuple[str, ...] = (),
        verifier: str = "",
    ) -> PipelineResult:
        if self._verification.decision is ControlDecision.STOP:
            return PipelineResult(action, ControlDecision.STOP, hypothesis)
        self._validate_inputs(action, execution, hypothesis, source)
        if candidate is not None:
            attempt_decision = self.flag_attempts.check_and_record(
                candidate,
                verifier or action.target,
                candidate_evidence_ids,
                action.state_before,
                observed_at,
            )
            if attempt_decision is ControlDecision.DUPLICATE:
                return PipelineResult(action, ControlDecision.DUPLICATE, hypothesis)
        registration = self.actions.register(action)
        if registration is ControlDecision.DUPLICATE:
            return PipelineResult(action, ControlDecision.DUPLICATE, hypothesis)

        classification = classify_result(execution)
        context = self._derive_impact_context(action, execution, hypothesis, source)
        impact = determine_impact(classification.result_class, context)
        observation = self._observation(action, execution, observed_at, source)
        evidence = self.evidence.record_current(
            observation=observation,
            classification=classification,
            impact=impact,
            affected_hypotheses=(hypothesis.hypothesis_id,),
        )
        updated = apply_evidence(hypothesis, evidence, impact, observed_at)
        self._hypotheses[updated.hypothesis_id] = updated
        self.actions.record_result(
            action.action_id,
            result_class=classification.result_class,
            state_after=action.state_after,
        )

        verification = None
        decision = ControlDecision.CONTINUE
        if candidate is not None:
            verification_ids = candidate_evidence_ids + (evidence.evidence_id,)
            verification = self.verifier.evaluate(candidate, verification_ids)
            self._candidates[candidate.value] = verification.candidate
            decision = verification.decision
            self._verification = VerificationState(
                tuple(self._candidates.values()), verification.decision
            )
        return PipelineResult(
            action=action,
            decision=decision,
            hypothesis=updated,
            observation=observation,
            classification=classification,
            evidence=evidence,
            impact=impact,
            verification=verification,
        )

    @staticmethod
    def _validate_inputs(
        action: Action,
        execution: ExecutionResult,
        hypothesis: Hypothesis,
        source: str,
    ) -> None:
        if execution.action_id != action.action_id:
            raise ValueError("execution action_id must match action action_id")
        if execution.tool != action.tool:
            raise ValueError("execution tool must match action tool")
        if not source.strip():
            raise ValueError("observation source is required")
        if not hypothesis.hypothesis_id.strip():
            raise ValueError("hypothesis_id is required")

    def _derive_impact_context(
        self,
        action: Action,
        execution: ExecutionResult,
        hypothesis: Hypothesis,
        source: str,
    ) -> ImpactContext:
        specification = self._test_specs.get(fingerprint_action(action))
        if specification is None:
            return ImpactContext(hypothesis.hypothesis_id)
        if specification.hypothesis_id != hypothesis.hypothesis_id:
            raise ValueError("registered test targets a different hypothesis")

        body = "\n".join((execution.stdout, execution.response_body))
        supports = bool(specification.supporting_body_contains) and all(
            marker in body for marker in specification.supporting_body_contains
        )
        contradicts = bool(specification.contradicting_body_contains) and all(
            marker in body for marker in specification.contradicting_body_contains
        )
        valid_test = bool(
            specification.supporting_body_contains
            or specification.contradicting_body_contains
        )
        trusted_for_tool = self._trusted_sources.get(action.tool, ())
        authoritative = (
            source in specification.authoritative_sources
            and source in trusted_for_tool
        )
        return ImpactContext(
            hypothesis_id=hypothesis.hypothesis_id,
            prerequisites_met=specification.prerequisites_met,
            valid_discriminating_test=valid_test,
            authoritative_observation=authoritative,
            expected_observation_seen=supports,
            contradiction_observed=contradicts,
            test_inconclusive=valid_test and not supports and not contradicts,
        )

    @staticmethod
    def _observation(
        action: Action,
        execution: ExecutionResult,
        observed_at: datetime,
        source: str,
    ) -> Observation:
        identity = f"{action.action_id}|{observed_at.isoformat()}|{source}"
        return Observation(
            observation_id="obs-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16],
            action_id=action.action_id,
            timestamp=observed_at,
            source=source,
            execution=execution,
        )
