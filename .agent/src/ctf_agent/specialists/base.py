from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Protocol, Tuple, runtime_checkable

from ..context import ChallengeContext
from ..models import Evidence, Freshness, ResultClass
from ..proposals import (
    ActionSuggestion,
    HypothesisSuggestion,
    ProposalRejected,
    _FORBIDDEN_PHRASES,
)


# Result classes that mean "the test was blocked or is unresolved", never "the hypothesis is
# disproven". A specialist that sees any of these for a mechanism's test must keep the mechanism
# PLAUSIBLE/BLOCKED, not DISPROVEN. (This mirrors Phase 2's impact.py, restated here so specialist
# reasoning is explicit about it rather than relying on the kernel to catch a bad annotation.)
NON_DISPROVING_RESULT_CLASSES: frozenset[ResultClass] = frozenset(
    {
        ResultClass.RATE_LIMIT,
        ResultClass.TIMEOUT,
        ResultClass.NETWORK_FAILURE,
        ResultClass.TOOL_FAILURE,
        ResultClass.ENVIRONMENT_FAILURE,
        ResultClass.AUTH_FAILURE,
        ResultClass.AUTHZ_FAILURE,
        ResultClass.INPUT_REJECTION,
    }
)


class SpecialistError(ValueError):
    """Raised when a specialist produces structurally invalid or authority-violating output."""


# Specialists reuse the Phase 3 ``FactState`` enum (from context.py) for mechanism/hypothesis state,
# so there is exactly one KNOWN/SUPPORTED/PLAUSIBLE/UNRESOLVED/BLOCKED/DISPROVEN/VERIFIED vocabulary
# across the whole system. `fact_state` fields below hold a ``FactState`` value (its .value str).


@dataclass(frozen=True)
class SpecialistContext:
    """The read-only snapshot a specialist analyzes. It is a thin wrapper over the Phase 3
    ``ChallengeContext`` plus the tools currently available for execution.

    A specialist may read everything here but can mutate nothing: ``ChallengeContext`` is itself a
    read view over a kernel snapshot, and this wrapper exposes only accessors.
    """

    challenge: ChallengeContext
    available_tools: Tuple[str, ...] = ()
    memory: object = None  # optional AdvisoryMemory; advisory-only, never authoritative

    @property
    def flag_format(self) -> str:
        return self.challenge.metadata.flag_format

    def memory_refs(self, category: str, keywords: Tuple[str, ...]) -> Tuple[str, ...]:
        """Advisory-only historical priors as human-readable reference strings.

        Returns technique/tool/trajectory reference labels from the Phase 1 corpus. These are
        priors for ranking/explanation only; nothing here can create a hypothesis, evidence, or a
        verified flag, and current evidence always outranks them.
        """
        if self.memory is None:
            return ()
        from ..memory_retrieval import MemoryQuery

        bundle = self.memory.retrieve(MemoryQuery(category=category, keywords=keywords))
        refs: list[str] = []
        for match in bundle.techniques:
            refs.append(f"technique:{match.technique_id}:{match.technique}")
        for match in bundle.tools:
            refs.append(f"tool:{match.tool_id}:{match.tool}")
        for match in bundle.trajectories:
            refs.append(f"trajectory:{match.trajectory_id}:{match.key_insight}")
        for match in bundle.failures:
            refs.append(f"failure:{match.record.failure_id}")
        return tuple(refs)

    def current_evidence(self) -> Tuple[Evidence, ...]:
        return tuple(
            e for e in self.challenge.snapshot.evidence if e.freshness is Freshness.CURRENT
        )

    def observation_texts(self) -> Tuple[str, ...]:
        texts = []
        for evidence in self.current_evidence():
            execution = evidence.observation.execution
            body = "\n".join((execution.stdout or "", execution.response_body or "")).strip()
            if body:
                texts.append(body)
        return tuple(texts)

    def indicator_corpus(self) -> str:
        """All the free text a specialist may scan for indicators, lowercased and joined.

        Deliberately includes challenge metadata AND current observation bodies, so specialists
        reason from evidence, not only from the challenge description.
        """
        meta = self.challenge.metadata
        parts = [
            meta.name,
            meta.category,
            meta.description,
            meta.flag_format,
            " ".join(meta.hints),
            " ".join(meta.files),
            " ".join(meta.urls),
        ]
        parts.extend(self.observation_texts())
        return "\n".join(p for p in parts if p).lower()

    def evidence_result_classes(self, hypothesis_id: str) -> Tuple[ResultClass, ...]:
        return tuple(
            e.result_class
            for e in self.current_evidence()
            if hypothesis_id in e.affected_hypotheses
        )


@dataclass(frozen=True)
class CandidateMechanism:
    name: str
    description: str
    fact_state: str  # a FactState value
    rationale: str
    supporting_evidence_ids: Tuple[str, ...] = ()
    conflicting_evidence_ids: Tuple[str, ...] = ()


@dataclass(frozen=True)
class SpecialistHypothesis:
    hypothesis_id: str
    statement: str
    mechanism: str
    technique: str
    fact_state: str  # a FactState value
    supporting_evidence_ids: Tuple[str, ...] = ()
    conflicting_evidence_ids: Tuple[str, ...] = ()


@dataclass(frozen=True)
class RecommendedTest:
    objective: str
    description: str
    expected_supporting_observation: str = ""
    expected_contradicting_observation: str = ""
    blocked_by_failures: Tuple[ResultClass, ...] = ()


@dataclass(frozen=True)
class CandidateAction:
    """A proposed action. Inert data: nothing here executes. Converted to a Phase 3
    ``ActionSuggestion`` by ``analysis_to_suggestions`` and only then validated + planned."""

    hypothesis_id: str
    objective: str
    tool: str
    target: str
    input_data: object = None
    relevant_parameters: dict | None = None
    prerequisites: Tuple[str, ...] = ()
    expected_observation: str = ""
    estimated_cost: int = 1
    candidate_flag: str = ""
    reasoning: str = ""


@dataclass(frozen=True)
class SpecialistAnalysis:
    specialist: str
    category: str
    relevance: float
    observations: Tuple[str, ...] = ()
    candidate_mechanisms: Tuple[CandidateMechanism, ...] = ()
    hypotheses: Tuple[SpecialistHypothesis, ...] = ()
    supporting_evidence_refs: Tuple[str, ...] = ()
    conflicting_evidence_refs: Tuple[str, ...] = ()
    recommended_tests: Tuple[RecommendedTest, ...] = ()
    candidate_actions: Tuple[CandidateAction, ...] = ()
    required_tools: Tuple[str, ...] = ()
    prerequisites: Tuple[str, ...] = ()
    expected_observations: Tuple[str, ...] = ()
    confidence: float = 0.0
    reasoning_summary: str = ""
    uncertainty: str = ""
    applicable_techniques: Tuple[str, ...] = ()
    relevant_memory_refs: Tuple[str, ...] = ()


@runtime_checkable
class Specialist(Protocol):
    """The common interface every specialist implements. Advisory only.

    A specialist has no reference to ``TrustKernel``, ``HypothesisBoard``, ``EvidenceManager``, or
    ``AdapterRegistry`` in its ``analyze`` return path -- it returns plain data.
    """

    name: str
    category: str

    def relevance(self, context: SpecialistContext) -> float: ...

    def analyze(self, context: SpecialistContext) -> SpecialistAnalysis: ...


def _reject_forbidden_phrases(text: str) -> None:
    lowered = text.lower()
    for phrase in _FORBIDDEN_PHRASES:
        if phrase in lowered:
            raise SpecialistError(
                f"specialist text attempts a state transition ('{phrase}'); "
                "specialists may only propose, never assert hypothesis/verification state"
            )


def validate_specialist_analysis(analysis: SpecialistAnalysis) -> SpecialistAnalysis:
    """Deterministic structural + authority validation of a specialist's output.

    Refuses: empty specialist/category, out-of-range relevance/confidence, forbidden state-assertion
    phrases anywhere in free text, candidate actions/hypotheses with empty required fields, and
    mechanism/hypothesis ``fact_state`` values outside the FactState vocabulary.
    """
    from ..context import FactState

    if not analysis.specialist.strip():
        raise SpecialistError("analysis.specialist must be non-empty")
    if not analysis.category.strip():
        raise SpecialistError("analysis.category must be non-empty")
    if not (0.0 <= analysis.relevance <= 1.0):
        raise SpecialistError("analysis.relevance must be within [0, 1]")
    if not (0.0 <= analysis.confidence <= 1.0):
        raise SpecialistError("analysis.confidence must be within [0, 1]")

    _reject_forbidden_phrases(analysis.reasoning_summary)
    _reject_forbidden_phrases(analysis.uncertainty)
    for observation in analysis.observations:
        _reject_forbidden_phrases(observation)

    valid_states = {state.value for state in FactState}
    for mechanism in analysis.candidate_mechanisms:
        if mechanism.fact_state not in valid_states:
            raise SpecialistError(
                f"mechanism '{mechanism.name}' has invalid fact_state '{mechanism.fact_state}'"
            )
        _reject_forbidden_phrases(mechanism.rationale)

    for hypothesis in analysis.hypotheses:
        if not hypothesis.hypothesis_id.strip():
            raise SpecialistError("hypothesis_id must be non-empty")
        if not hypothesis.statement.strip():
            raise SpecialistError("hypothesis statement must be non-empty")
        if hypothesis.fact_state not in valid_states:
            raise SpecialistError(
                f"hypothesis '{hypothesis.hypothesis_id}' has invalid fact_state "
                f"'{hypothesis.fact_state}'"
            )
        # A specialist may never propose a hypothesis it has already decided is terminal.
        if hypothesis.fact_state in {FactState.DISPROVEN.value, FactState.VERIFIED.value}:
            raise SpecialistError(
                f"specialist proposed hypothesis '{hypothesis.hypothesis_id}' in terminal state "
                f"'{hypothesis.fact_state}'; only the kernel may set terminal status"
            )
        _reject_forbidden_phrases(hypothesis.statement)

    for candidate in analysis.candidate_actions:
        if not candidate.objective.strip():
            raise SpecialistError("candidate action objective must be non-empty")
        if not candidate.tool.strip():
            raise SpecialistError("candidate action tool must be non-empty")
        if not candidate.target.strip():
            raise SpecialistError("candidate action target must be non-empty")
        if not candidate.hypothesis_id.strip():
            raise SpecialistError("candidate action hypothesis_id must be non-empty")
        _reject_forbidden_phrases(candidate.objective)
        _reject_forbidden_phrases(candidate.reasoning)

    return analysis


def analysis_to_suggestions(
    analysis: SpecialistAnalysis,
) -> Tuple[Tuple[HypothesisSuggestion, ...], Tuple[ActionSuggestion, ...]]:
    """The single bridge from specialist output into the Phase 3 proposal world.

    Returns validated-shape (but not yet planner-validated) HypothesisSuggestion and
    ActionSuggestion tuples. The planner still independently validates every ActionSuggestion
    (registered tool, non-empty fields, no forbidden phrases) before anything runs, and the loop
    still seeds hypotheses only via the authoritative ``board.propose_hypothesis``.
    """
    hypotheses = tuple(
        HypothesisSuggestion(
            hypothesis_id=h.hypothesis_id,
            statement=h.statement,
            mechanism=h.mechanism,
            technique=h.technique,
            rationale=analysis.reasoning_summary,
        )
        for h in analysis.hypotheses
    )
    actions = tuple(
        ActionSuggestion(
            hypothesis_id=a.hypothesis_id,
            objective=a.objective,
            tool=a.tool,
            target=a.target,
            input_data=a.input_data,
            relevant_parameters=a.relevant_parameters,
            prerequisites=a.prerequisites,
            expected_observation=a.expected_observation,
            rationale=a.reasoning,
            candidate_flag=a.candidate_flag,
        )
        for a in analysis.candidate_actions
    )
    return hypotheses, actions


def score_relevance(
    context: SpecialistContext, own_category: str, indicator_keywords: Tuple[str, ...]
) -> float:
    """Deterministic relevance in [0,1]: category match is the primary signal (0.6), indicator
    keyword hits in the combined metadata+evidence corpus add up to 0.4. No hidden state."""
    corpus = context.indicator_corpus()
    score = 0.0
    if context.challenge.metadata.category.lower() == own_category.lower():
        score += 0.6
    hits = sum(1 for kw in indicator_keywords if kw.lower() in corpus)
    if hits:
        score += min(0.4, 0.1 * hits)
    return round(min(1.0, score), 4)


def current_hypothesis_state(context: SpecialistContext, hypothesis_id: str) -> str:
    """Read a hypothesis's *current* FactState from the live board (evidence-derived), or PLAUSIBLE
    if the board has never seen it. This is how a specialist stays evidence-aware: it does not
    invent a state, it reports what the kernel-fed board currently says.
    """
    from ..context import FactState

    for view in context.challenge.hypothesis_views():
        if view.hypothesis.hypothesis_id == hypothesis_id:
            return view.state.value
    return FactState.PLAUSIBLE.value


def mechanism_blocked_by_failure(
    context: SpecialistContext, hypothesis_id: str
) -> Tuple[ResultClass, ...]:
    """Return the non-disproving failure result classes currently recorded for a hypothesis.

    A specialist uses this to say "my test was BLOCKED/UNRESOLVED by X" instead of ever concluding
    the mechanism is disproven.
    """
    return tuple(
        rc
        for rc in context.evidence_result_classes(hypothesis_id)
        if rc in NON_DISPROVING_RESULT_CLASSES
    )


@dataclass(frozen=True)
class ToolMechanism:
    """A mechanism a specialist tests by running a local analysis tool in a specific mode."""

    suffix: str
    name: str
    technique: str
    indicators: Tuple[str, ...]
    mode: str
    expected_supporting: str
    expected_contradicting: str
    cost: int = 1


def analyze_with_tool(
    context: SpecialistContext,
    *,
    specialist: str,
    category: str,
    id_prefix: str,
    mechanisms: Tuple[ToolMechanism, ...],
    tool_default: Tuple[str, ...],
    extra_relevance_indicators: Tuple[str, ...],
    memory_keywords: Tuple[str, ...],
    reasoning_summary: str,
    uncertainty: str,
) -> SpecialistAnalysis:
    """Shared analysis body for specialists that drive a single local analysis tool by mode.

    Only mechanisms whose indicators are actually present are proposed; each becomes a
    hypothesis + a discriminating ``[mode, target]`` action; failures are annotated as
    BLOCKED/UNRESOLVED (never DISPROVEN); observed flag tokens become submit proposals.
    """
    from ..context import FactState

    corpus = context.indicator_corpus()
    tools = preferred_tools(context, tool_default)
    # Prefer one of THIS specialist's own tools that is actually available; otherwise fall back to
    # the specialist's canonical tool name (NOT some unrelated available tool). If the canonical
    # tool isn't registered, the planner will simply reject the action -- the specialist must never
    # hijack another specialist's tool.
    tool = next((t for t in tool_default if t in tools), tool_default[0])
    target = context.challenge.metadata.files[0] if context.challenge.metadata.files else ""

    candidate_mechanisms: list[CandidateMechanism] = []
    hypotheses: list[SpecialistHypothesis] = []
    actions: list[CandidateAction] = []
    recommended: list[RecommendedTest] = []
    observations: list[str] = []

    for mech in mechanisms:
        if not any(ind in corpus for ind in mech.indicators):
            continue
        hyp_id = f"{id_prefix}-{mech.suffix}"
        state = current_hypothesis_state(context, hyp_id)
        if state == FactState.DISPROVEN.value:
            observations.append(f"{mech.name}: DISPROVEN by prior evidence; branch closed")
            continue
        blockers = mechanism_blocked_by_failure(context, hyp_id)
        if blockers:
            state = FactState.BLOCKED.value if state == FactState.UNRESOLVED.value else state
            observations.append(
                f"{mech.name}: prior test blocked by {', '.join(b.value for b in blockers)}; "
                "tool/environment failure is not disproof of the mechanism"
            )
        candidate_mechanisms.append(
            CandidateMechanism(
                name=mech.name,
                description=f"candidate mechanism: {mech.name}",
                fact_state=state,
                rationale=f"indicators for {mech.name} present in challenge/evidence",
            )
        )
        hypotheses.append(
            SpecialistHypothesis(
                hypothesis_id=hyp_id,
                statement=f"The artifact/target exhibits {mech.name}",
                mechanism=mech.name,
                technique=mech.technique,
                fact_state=state,
            )
        )
        recommended.append(
            RecommendedTest(
                objective=f"test {mech.name}",
                description=f"run {tool} in '{mech.mode}' mode and interpret the structured result",
                expected_supporting_observation=mech.expected_supporting,
                expected_contradicting_observation=mech.expected_contradicting,
                blocked_by_failures=(ResultClass.TOOL_FAILURE, ResultClass.ENVIRONMENT_FAILURE),
            )
        )
        if target and tool:
            actions.append(
                CandidateAction(
                    hypothesis_id=hyp_id,
                    objective=f"{mech.mode} analysis for {mech.name}",
                    tool=tool,
                    target=target,
                    input_data=[mech.mode, target],
                    expected_observation=mech.expected_supporting,
                    estimated_cost=mech.cost,
                    reasoning=(
                        f"cheapest useful test for {mech.name}; a tool/environment failure only "
                        "blocks this test and must not be read as disproof"
                    ),
                )
            )

    actions.extend(build_submit_actions(tuple(actions), context))

    relevance = score_relevance(
        context,
        category,
        tuple(kw for m in mechanisms for kw in m.indicators) + extra_relevance_indicators,
    )
    return SpecialistAnalysis(
        specialist=specialist,
        category=category,
        relevance=relevance,
        observations=tuple(observations),
        candidate_mechanisms=tuple(candidate_mechanisms),
        hypotheses=tuple(hypotheses),
        recommended_tests=tuple(recommended),
        candidate_actions=tuple(actions),
        required_tools=(tool,) if target else (),
        expected_observations=tuple(m.expected_supporting for m in mechanisms),
        confidence=min(1.0, relevance),
        reasoning_summary=reasoning_summary,
        uncertainty=uncertainty,
        applicable_techniques=tuple(m.technique for m in mechanisms),
        relevant_memory_refs=context.memory_refs(_memory_category(category), memory_keywords),
    )


def _memory_category(specialist_category: str) -> str:
    # Map specialist categories to the Phase 1 corpus category strings.
    return {"reverse": "rev"}.get(specialist_category, specialist_category)


def preferred_tools(context: SpecialistContext, default: Tuple[str, ...]) -> Tuple[str, ...]:
    """Prefer tools the environment advertises; otherwise fall back to canonical names and let the
    planner reject any that are not actually registered."""
    return context.available_tools or default


def build_submit_actions(
    probes: Tuple["CandidateAction", ...], context: SpecialistContext
) -> Tuple["CandidateAction", ...]:
    """Turn observed flag tokens into submit proposals, reusing the FULL probe construction
    (tool+target+input_data) of whichever of *this specialist's own* probes produced the token.

    Matching by (tool, target) is how the specialist recovers the exact ``input_data`` to re-run a
    stateful tool -- it never guesses. The submit action differs from the probe only by objective
    (so it is not a duplicate) and by carrying ``candidate_flag``. The Phase 2 kernel still performs
    the actual verification from real bound evidence.
    """
    from ..context import FactState

    candidates = extract_flag_candidates(context)
    if not candidates:
        return ()
    # Several mechanisms can probe the same (tool, target) differing only by input_data mode, so a
    # plain (tool,target) lookup is ambiguous. Group all matching probes and choose the one whose
    # hypothesis the current evidence actually SUPPORTS; never attach a submission to a DISPROVEN
    # branch. This keeps the submit evidence-driven (which mechanism won) rather than order-driven.
    probes_by_target: dict[Tuple[str, str], list["CandidateAction"]] = {}
    for probe in probes:
        probes_by_target.setdefault((probe.tool, probe.target), []).append(probe)

    submits: list["CandidateAction"] = []
    seen: set[Tuple[str, str, str]] = set()
    for flag_value, tool, source in candidates:
        matching = probes_by_target.get((tool, source), [])
        probe = _choose_supported_probe(matching, context)
        if probe is None:
            continue
        if current_hypothesis_state(context, probe.hypothesis_id) == FactState.DISPROVEN.value:
            continue
        key = (flag_value, tool, source)
        if key in seen:
            continue
        seen.add(key)
        submits.append(
            CandidateAction(
                hypothesis_id=probe.hypothesis_id,
                objective="submit observed flag candidate for authoritative verification",
                tool=tool,
                target=source,
                input_data=probe.input_data,
                relevant_parameters=probe.relevant_parameters,
                prerequisites=probe.prerequisites,
                expected_observation="the challenge's authoritative verifier accepts the candidate",
                estimated_cost=1,
                candidate_flag=flag_value,
                reasoning=(
                    "a flag-format token was observed in authoritative tool output; propose "
                    "submitting exactly that observed value -- the Phase 2 VerificationController "
                    "independently decides acceptance, this is only a value-to-try proposal"
                ),
            )
        )
    return tuple(submits)


def _choose_supported_probe(
    probes: list["CandidateAction"], context: SpecialistContext
) -> "CandidateAction | None":
    """Among probes sharing a (tool, target), pick the one whose hypothesis is currently SUPPORTED
    (evidence-driven), else the first non-DISPROVEN one, else None."""
    from ..context import FactState

    if not probes:
        return None
    for probe in probes:
        if current_hypothesis_state(context, probe.hypothesis_id) == FactState.SUPPORTED.value:
            return probe
    for probe in probes:
        if current_hypothesis_state(context, probe.hypothesis_id) != FactState.DISPROVEN.value:
            return probe
    return None


def extract_flag_candidates(context: SpecialistContext) -> Tuple[Tuple[str, str, str], ...]:
    """Scan current authoritative-looking evidence for flag-format tokens.

    Returns tuples of ``(flag_value, producing_tool, producing_source)`` so a specialist can propose
    submitting a value it actually *observed*, reusing the exact tool+target that produced it. This
    is evidence-derived, never foreknowledge: if no observation contains a flag-shaped token, the
    result is empty and the specialist proposes discriminating probes instead.
    """
    pattern = _flag_regex(context.flag_format)
    found: list[Tuple[str, str, str]] = []
    seen: set[str] = set()
    for evidence in context.current_evidence():
        if evidence.result_class not in {
            ResultClass.SUCCESS,
            ResultClass.TARGET_RESPONSE,
            ResultClass.STATE_CHANGE,
        }:
            # Failed/blocked tool output is not a legitimate candidate origin even if it happens to
            # contain flag-shaped text. The Phase 2 verifier would not accept that evidence alone;
            # Phase 5 additionally refuses to generate the candidate in the first place.
            continue
        execution = evidence.observation.execution
        body = "\n".join((execution.stdout or "", execution.response_body or ""))
        for match in pattern.findall(body):
            if match not in seen:
                seen.add(match)
                found.append((match, execution.tool, evidence.observation.source))
    return tuple(found)


def _flag_regex(flag_format: str) -> "re.Pattern[str]":
    """Build a flag matcher. If the challenge names a prefix like ``CTF{`` we anchor on it;
    otherwise we fall back to a generic ``WORD{...}`` shape. Never matches across braces."""
    prefix = ""
    if flag_format and "{" in flag_format:
        prefix = flag_format.split("{", 1)[0]
    prefix = re.sub(r"[^A-Za-z0-9_]", "", prefix)
    if prefix:
        return re.compile(rf"{re.escape(prefix)}\{{[^}}]*\}}")
    return re.compile(r"[A-Za-z0-9_]{2,}\{[^}]*\}")
