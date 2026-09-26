"""Model-routing policy — lives ONLY at the ReasoningSource layer.

Routing selects which model produces the next batch of *proposals*. It has no effect on execution,
verification, or state: the model it selects can still only emit typed suggestions that the frozen
pipeline validates and governs. Routing is therefore a cost/quality lever, never a trust lever.

Policy (per task):
- FAST      -> "sonnet-5"            (default; start cheap)
- DEEP      -> "opus-5"              (escalate when evidence shows deeper reasoning is justified)
- FALLBACK  -> "gpt-5.6-luna-think"  (used only when the selected model errors)
- HIGH_END  -> "gpt-5.6-sol-high"    (explicit benchmark/alternative or extreme escalation)

Category is only ONE signal and never hard-maps to a model on its own; escalation is driven by
evidence (uncertainty, stall, failure class, difficulty, budget pressure, novelty).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ModelTier(str, Enum):
    FAST = "FAST"
    DEEP = "DEEP"
    FALLBACK = "FALLBACK"
    HIGH_END = "HIGH_END"

    def __str__(self) -> str:
        return self.value


# Tier -> concrete model identifier (opaque strings handed to the LLM client; nothing else).
TIER_MODELS = {
    ModelTier.FAST: "sonnet-5",
    ModelTier.DEEP: "opus-5",
    ModelTier.FALLBACK: "gpt-5.6-luna-think",
    ModelTier.HIGH_END: "gpt-5.6-sol-high",
}


@dataclass(frozen=True)
class RoutingSignals:
    """Evidence-derived signals the router considers. All are read from agent state, never from the
    model's own claims."""

    category: str = ""
    difficulty: str = ""            # "", "easy", "medium", "hard", "insane" (inferred, advisory)
    uncertainty: int = 0            # count of UNRESOLVED/PLAUSIBLE/BLOCKED hypotheses
    supported_count: int = 0        # count of SUPPORTED hypotheses
    evidence_count: int = 0         # current evidence records
    stall_steps: int = 0            # reasoning invocations since the last new SUPPORTED/evidence gain
    last_failure_class: str = ""    # most recent observation result_class if it was a failure
    budget_remaining_fraction: float = 1.0
    novelty: bool = False           # no supported hypothesis and no matching prior technique
    force_tier: Optional[ModelTier] = None  # explicit override (e.g. benchmark HIGH_END)


@dataclass(frozen=True)
class RouteDecision:
    tier: ModelTier
    model: str
    escalation_reason: str

    def to_dict(self) -> dict:
        return {"tier": self.tier.value, "model": self.model, "escalation_reason": self.escalation_reason}


_HARD = {"hard", "insane"}
_FAILURE_CLASSES = {
    "RATE_LIMIT", "TIMEOUT", "AUTH_FAILURE", "AUTHZ_FAILURE", "NETWORK_FAILURE",
    "TOOL_FAILURE", "ENVIRONMENT_FAILURE",
}


class ModelRouter:
    """Deterministic, evidence-driven model router. Starts cheap and escalates only on evidence.

    Thresholds are simple and explicit (no utility framework). The router is pure given its signals,
    so routing decisions are fully reproducible and testable.
    """

    def __init__(
        self,
        *,
        stall_escalate: int = 2,
        uncertainty_escalate: int = 3,
        extreme_stall: int = 4,
        low_budget_fraction: float = 0.2,
    ) -> None:
        self.stall_escalate = stall_escalate
        self.uncertainty_escalate = uncertainty_escalate
        self.extreme_stall = extreme_stall
        self.low_budget_fraction = low_budget_fraction

    def select(self, signals: RoutingSignals) -> RouteDecision:
        if signals.force_tier is not None:
            return self._decision(signals.force_tier, f"explicit force_tier={signals.force_tier.value}")

        # Extreme escalation: prolonged stall with no progress -> the high-end alternative.
        if signals.stall_steps >= self.extreme_stall:
            return self._decision(
                ModelTier.HIGH_END,
                f"extreme stall ({signals.stall_steps} steps without new supported evidence)",
            )

        reasons = []
        if signals.stall_steps >= self.stall_escalate:
            reasons.append(f"stall={signals.stall_steps}")
        if signals.uncertainty >= self.uncertainty_escalate:
            reasons.append(f"uncertainty={signals.uncertainty}")
        if signals.difficulty in _HARD:
            reasons.append(f"difficulty={signals.difficulty}")
        if signals.last_failure_class in _FAILURE_CLASSES:
            reasons.append(f"failure_class={signals.last_failure_class}")
        if signals.novelty and signals.supported_count == 0 and signals.evidence_count > 0:
            reasons.append("novel-mechanism, no supported hypothesis yet")
        if signals.budget_remaining_fraction <= self.low_budget_fraction and signals.supported_count == 0:
            reasons.append(f"budget pressure ({signals.budget_remaining_fraction:.2f}) without a solve")

        if reasons:
            return self._decision(ModelTier.DEEP, "escalated: " + ", ".join(reasons))

        # Default: cheap fast tier.
        return self._decision(
            ModelTier.FAST,
            "default fast path (low uncertainty, no stall, no blocking failure)",
        )

    def fallback(self, signals: RoutingSignals, error: str) -> RouteDecision:
        """Used only when the primary selected model raised an error."""
        return self._decision(ModelTier.FALLBACK, f"primary model error -> fallback: {error[:160]}")

    @staticmethod
    def _decision(tier: ModelTier, reason: str) -> RouteDecision:
        return RouteDecision(tier=tier, model=TIER_MODELS[tier], escalation_reason=reason)
