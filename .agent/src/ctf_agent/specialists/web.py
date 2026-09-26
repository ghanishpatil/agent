from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple
from urllib.parse import quote

from ..context import FactState
from ..models import ResultClass
from .base import (
    CandidateAction,
    CandidateMechanism,
    RecommendedTest,
    SpecialistAnalysis,
    SpecialistContext,
    SpecialistHypothesis,
    build_submit_actions,
    current_hypothesis_state,
    mechanism_blocked_by_failure,
    preferred_tools,
    score_relevance,
)


@dataclass(frozen=True)
class _WebMechanism:
    suffix: str
    name: str
    technique: str
    indicators: Tuple[str, ...]
    param: str
    payload: str
    expected_supporting: str
    expected_contradicting: str
    cost: int


# Mechanisms are indicators -> discriminating test, NOT a hardcoded "always try these" list. Only
# mechanisms whose indicators actually appear in the metadata+evidence corpus are proposed.
_MECHANISMS: Tuple[_WebMechanism, ...] = (
    _WebMechanism(
        "sqli", "SQL injection", "sql-injection",
        ("sql", "select", "query", "search", "id=", "login", "database", "records"),
        "id", "1' OR '1'='1",
        "a syntax perturbation changes the response / extra or secret rows appear",
        "identical ordinary response with no structural change",
        1,
    ),
    _WebMechanism(
        "ssti", "server-side template injection", "ssti",
        ("template", "render", "jinja", "twig", "{{", "profile name", "greeting"),
        "name", "{{7*7}}",
        "the response contains 49 (expression evaluated)",
        "the literal {{7*7}} is reflected unevaluated",
        1,
    ),
    _WebMechanism(
        "cmdi", "OS command injection", "command-injection",
        ("ping", "host", "lookup", "exec", "system", "command", "shell"),
        "host", "127.0.0.1; id",
        "command output (uid=/gid=) appears below the normal response",
        "input rejected or unchanged response",
        2,
    ),
    _WebMechanism(
        "ssrf", "server-side request forgery", "ssrf",
        ("url=", "fetch", "webhook", "redirect", "proxy", "callback", "image url"),
        "url", "http://127.0.0.1/",
        "internal service content or a connection to the supplied host",
        "the fetch is rejected or unaffected by host changes",
        2,
    ),
    _WebMechanism(
        "lfi", "local file inclusion / path traversal", "path-traversal",
        ("file=", "path", "include", "download", "page=", "traversal"),
        "file", "../../../../etc/passwd",
        "file contents (root:) appear in the response",
        "no file contents / input rejected",
        2,
    ),
)

# A JWT indicator is a cross-domain signal: the WEB specialist notes it and defers the crypto of it
# to the CRYPTO specialist (mediated by the brain), rather than pretending to analyze token signing.
_JWT_INDICATORS = ("jwt", "token", "eyj", "bearer", "authorization:")


class WebSpecialist:
    name = "web"
    category = "web"

    def relevance(self, context: SpecialistContext) -> float:
        indicators = tuple(
            kw for mech in _MECHANISMS for kw in mech.indicators
        ) + _JWT_INDICATORS + ("http", "https", "cookie", "header", "endpoint", "api", "web")
        return score_relevance(context, self.category, indicators)

    def analyze(self, context: SpecialistContext) -> SpecialistAnalysis:
        corpus = context.indicator_corpus()
        base_url = context.challenge.metadata.urls[0] if context.challenge.metadata.urls else ""

        mechanisms: list[CandidateMechanism] = []
        hypotheses: list[SpecialistHypothesis] = []
        actions: list[CandidateAction] = []
        recommended: list[RecommendedTest] = []
        observations: list[str] = []
        memory_refs = context.memory_refs(self.category, ("sql", "injection", "ssti", "command"))

        for mech in _MECHANISMS:
            if not any(ind in corpus for ind in mech.indicators):
                continue
            hyp_id = f"web-{mech.suffix}"
            state = current_hypothesis_state(context, hyp_id)
            if state == FactState.DISPROVEN.value:
                observations.append(f"{mech.name}: DISPROVEN by prior evidence; branch closed")
                continue
            blockers = mechanism_blocked_by_failure(context, hyp_id)
            if blockers:
                # A tool/rate-limit/etc. failure BLOCKS the test; it never disproves the mechanism.
                state = FactState.BLOCKED.value if state == FactState.UNRESOLVED.value else state
                observations.append(
                    f"{mech.name}: prior test blocked by {', '.join(b.value for b in blockers)}; "
                    "re-test needed, mechanism NOT disproven"
                )

            mechanisms.append(
                CandidateMechanism(
                    name=mech.name,
                    description=f"{mech.name} on parameter '{mech.param}'",
                    fact_state=state,
                    rationale=f"indicators present in challenge/evidence for {mech.name}",
                )
            )
            hypotheses.append(
                SpecialistHypothesis(
                    hypothesis_id=hyp_id,
                    statement=f"The application is vulnerable to {mech.name} via '{mech.param}'",
                    mechanism=mech.name,
                    technique=mech.technique,
                    fact_state=state,
                )
            )
            recommended.append(
                RecommendedTest(
                    objective=f"discriminating {mech.name} probe",
                    description=(
                        f"perturb '{mech.param}' with a controlled {mech.name} payload and observe "
                        "whether the response changes structurally"
                    ),
                    expected_supporting_observation=mech.expected_supporting,
                    expected_contradicting_observation=mech.expected_contradicting,
                    blocked_by_failures=(
                        ResultClass.RATE_LIMIT,
                        ResultClass.TIMEOUT,
                        ResultClass.NETWORK_FAILURE,
                        ResultClass.TOOL_FAILURE,
                    ),
                )
            )
            if base_url and "http_probe" in preferred_tools(context, ("http_probe",)):
                probe_url = f"{base_url}?{mech.param}={quote(mech.payload)}"
                actions.append(
                    CandidateAction(
                        hypothesis_id=hyp_id,
                        objective=f"discriminating {mech.name} probe on '{mech.param}'",
                        tool="http_probe",
                        target=probe_url,
                        relevant_parameters={"method": "GET"},
                        expected_observation=mech.expected_supporting,
                        estimated_cost=mech.cost,
                        reasoning=(
                            f"cheapest discriminating test for {mech.name}: one controlled "
                            "syntax perturbation; a 429/timeout/tool failure only blocks the test"
                        ),
                    )
                )

        if any(ind in corpus for ind in _JWT_INDICATORS):
            observations.append(
                "JWT/token indicator present: the token's signing is a CRYPTO-domain question; "
                "deferring algorithm-confusion / signature analysis to the crypto specialist"
            )

        actions.extend(build_submit_actions(tuple(actions), context))

        relevance = self.relevance(context)
        return SpecialistAnalysis(
            specialist=self.name,
            category=self.category,
            relevance=relevance,
            observations=tuple(observations),
            candidate_mechanisms=tuple(mechanisms),
            hypotheses=tuple(hypotheses),
            recommended_tests=tuple(recommended),
            candidate_actions=tuple(actions),
            required_tools=("http_probe",) if base_url else (),
            expected_observations=tuple(m.expected_supporting for m in _MECHANISMS),
            confidence=min(1.0, relevance),
            reasoning_summary=(
                "Reasoned from present indicators to candidate web mechanisms; each is PLAUSIBLE "
                "until a discriminating probe produces supporting or contradicting evidence. "
                "Blocking failures (rate limit, timeout, tool error) are never treated as disproof."
            ),
            uncertainty=(
                "Parameter names are inferred; the exact injectable parameter may differ and would "
                "need a cheap enumeration probe to confirm."
            ),
            applicable_techniques=tuple(m.technique for m in _MECHANISMS),
            relevant_memory_refs=memory_refs,
        )



