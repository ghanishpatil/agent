from __future__ import annotations

from .models import HypothesisImpact, ImpactContext, ResultClass


_UNRESOLVING_RESULTS = {
    ResultClass.RATE_LIMIT,
    ResultClass.TIMEOUT,
    ResultClass.NETWORK_FAILURE,
    ResultClass.TOOL_FAILURE,
    ResultClass.ENVIRONMENT_FAILURE,
}
_BLOCKING_RESULTS = {
    ResultClass.AUTH_FAILURE,
    ResultClass.AUTHZ_FAILURE,
    ResultClass.INPUT_REJECTION,
}
_OBSERVATIONAL_RESULTS = {
    ResultClass.SUCCESS,
    ResultClass.TARGET_RESPONSE,
    ResultClass.STATE_CHANGE,
}


def determine_impact(result_class: ResultClass, context: ImpactContext) -> HypothesisImpact:
    """Map a classified result to conservative hypothesis impact."""
    if not context.observation_available:
        return HypothesisImpact.NO_IMPACT
    if not context.prerequisites_met:
        return HypothesisImpact.BLOCKS_TEST
    if result_class in _UNRESOLVING_RESULTS:
        return HypothesisImpact.UNRESOLVES
    if result_class in _BLOCKING_RESULTS:
        return HypothesisImpact.BLOCKS_TEST
    if result_class is ResultClass.AMBIGUOUS:
        return HypothesisImpact.UNRESOLVES
    if result_class not in _OBSERVATIONAL_RESULTS:
        return HypothesisImpact.NO_IMPACT

    if context.test_inconclusive:
        return HypothesisImpact.UNRESOLVES
    if context.expected_observation_seen and context.authoritative_observation:
        return HypothesisImpact.SUPPORTS
    if context.contradiction_observed and context.valid_discriminating_test:
        if context.authoritative_observation:
            return HypothesisImpact.DISPROVES
        return HypothesisImpact.WEAKENS
    return HypothesisImpact.NO_IMPACT
