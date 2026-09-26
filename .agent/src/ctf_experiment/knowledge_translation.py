"""Generalized Knowledge Translation Layer.

A deterministic, **advisory-only** bridge from retrieved CTF knowledge (external writeups) and
agent-generated experiences into the typed suggestions the frozen Strategic Brain / reasoning
source already emit (:class:`ctf_agent.proposals.HypothesisSuggestion` /
:class:`~ctf_agent.proposals.ActionSuggestion`). It replaces the narrow, web-only
``_WEB_TESTS`` bridge concept with a generalized, trajectory-first, template-driven translator.

Design contract (non-negotiable):

* **Knowledge may suggest. Evidence must authorize. Planner/kernel/verification remain
  authoritative.** This module returns *data*; it never executes a tool, makes a request, submits
  a flag, mutates evidence, or changes a hypothesis/verification state.
* **Trajectory-first.** Translation reasons over the ingested reasoning trajectory
  (``CANDIDATE_MECHANISM -> HYPOTHESIS -> DISCRIMINATING_TEST -> OBSERVATION -> INTERPRETATION ->
  NEXT_ACTION``), not over a ``technique -> payload`` lookup. Knowledge is useful even when it
  provides no directly reusable payload — it can still yield a mechanism + hypothesis + a
  described discriminating test (``HYPOTHESIS_ONLY``).
* **No invention.** Concrete values placed in a *runnable* action (target, parameter, payload,
  expected observation, tool) come ONLY from (a) grounded current runtime facts in
  :class:`TranslationContext`, or (b) a vetted, technique-intrinsic
  :class:`MechanismTemplate`. If a required concrete value is missing, the result is
  ``HYPOTHESIS_ONLY`` — never a fabricated value.
* **Exact target/evidence alignment.** Runnable targets are built ONLY from the grounded current
  target; retrieved targets that name a different host, or an exact-target byte mismatch (e.g.
  ``*`` vs ``%2A``), downgrade the result to ``HYPOTHESIS_ONLY``.
* **Provenance is preserved and never collapsed.** External writeups, agent success experiences,
  and agent failure experiences stay distinguishable via :class:`KnowledgeOrigin`.
* **Deterministic.** Same knowledge + same context => same result. No randomness, no clock, no
  network, no model.

Nothing here imports or mutates ``ctf_agent``; it only *constructs* the frozen proposal types.
The seeded ``ssti`` / ``sql-injection`` templates reproduce the exact target construction the
existing ``knowledge_reasoning._WEB_TESTS`` bridge uses (a compatibility test pins this).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.parse import quote, urlsplit

from ctf_agent.proposals import ActionSuggestion, HypothesisSuggestion

from ctf_ingest.models import (
    KnowledgeRecord,
    ReasoningTrajectory,
    Technique,
    TrajectoryStep,
    TrajectoryStepKind,
)

# Agent-experience source kinds (mirrors ctf_runtime.experience_store without importing it, so the
# translator works on external knowledge even if the runtime package is absent).
SOURCE_SUCCESS = "AGENT_SUCCESS_EXPERIENCE"
SOURCE_FAILURE = "AGENT_FAILURE_EXPERIENCE"

TRANSLATION_SCHEMA_VERSION = "1.0"

# Environmental / non-authoritative result classes: their presence in a failure experience means
# the technique is UNRESOLVED, never disproven.
_ENVIRONMENTAL_CLASSES = frozenset(
    {"RATE_LIMIT", "TIMEOUT", "NETWORK_FAILURE", "TOOL_FAILURE", "ENVIRONMENT_FAILURE",
     "AUTH_FAILURE", "AUTHZ_FAILURE", "INPUT_REJECTION"}
)


# =========================================================================================
# Enums
# =========================================================================================

class KnowledgeOrigin(str, Enum):
    """Provenance class of a translated result. Never collapsed into one anonymous source."""

    EXTERNAL_WRITEUP = "EXTERNAL_WRITEUP"
    AGENT_SUCCESS_EXPERIENCE = "AGENT_SUCCESS_EXPERIENCE"
    AGENT_FAILURE_EXPERIENCE = "AGENT_FAILURE_EXPERIENCE"


class TranslationStatus(str, Enum):
    """What the translator was able to justify from knowledge + current evidence."""

    RUNNABLE_TEST = "RUNNABLE_TEST"        # a legitimately grounded discriminating action exists
    HYPOTHESIS_ONLY = "HYPOTHESIS_ONLY"    # mechanism/hypothesis known; not enough to run safely
    ADVISORY_CONFLICT = "ADVISORY_CONFLICT"  # knowledge conflicts with current authoritative evidence
    NOT_APPLICABLE = "NOT_APPLICABLE"      # no mechanism could be extracted at all


class Applicability(str, Enum):
    """How applicable the mechanism is judged to be, given the knowledge source."""

    PLAUSIBLE = "PLAUSIBLE"                 # worth testing (default for external/success)
    UNRESOLVED = "UNRESOLVED"               # a prior attempt neither proved nor disproved it
    DISPROVEN_ELSEWHERE = "DISPROVEN_ELSEWHERE"  # authoritatively disproven in a DIFFERENT context


# =========================================================================================
# Provenance + support metadata
# =========================================================================================

@dataclass(frozen=True)
class TranslationProvenance:
    """Traces a translated result back to its exact source and the steps that produced it."""

    origin: KnowledgeOrigin
    source_id: str                          # record_id (external) or experience record_id (agent)
    technique_id: str = ""
    # external-knowledge locators
    source_uri: str = ""
    document_path: str = ""
    # agent-experience locators
    run_id: str = ""
    session_id: str = ""
    driver: str = ""
    source_kind: str = ""
    # which trajectory steps produced each element (order indices; -1 == not from a step)
    mechanism_step_order: int = -1
    hypothesis_step_order: int = -1
    test_step_order: int = -1

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "origin": self.origin.value, "source_id": self.source_id,
            "technique_id": self.technique_id, "source_uri": self.source_uri,
            "document_path": self.document_path, "run_id": self.run_id,
            "session_id": self.session_id, "driver": self.driver, "source_kind": self.source_kind,
            "mechanism_step_order": self.mechanism_step_order,
            "hypothesis_step_order": self.hypothesis_step_order,
            "test_step_order": self.test_step_order,
        }
        return d


@dataclass(frozen=True)
class TrajectoryExtract:
    """The trajectory-first reading of a record: one text (+order) per reasoning stage."""

    mechanism: str = ""
    mechanism_order: int = -1
    hypothesis: str = ""
    hypothesis_order: int = -1
    discriminating_test: str = ""
    discriminating_test_order: int = -1
    observation: str = ""
    observation_order: int = -1
    interpretation: str = ""
    interpretation_order: int = -1
    next_action: str = ""
    next_action_order: int = -1
    conflicts: Tuple[str, ...] = ()          # notes about conflicting/duplicated steps

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mechanism": self.mechanism, "mechanism_order": self.mechanism_order,
            "hypothesis": self.hypothesis, "hypothesis_order": self.hypothesis_order,
            "discriminating_test": self.discriminating_test,
            "discriminating_test_order": self.discriminating_test_order,
            "observation": self.observation, "observation_order": self.observation_order,
            "interpretation": self.interpretation, "interpretation_order": self.interpretation_order,
            "next_action": self.next_action, "next_action_order": self.next_action_order,
            "conflicts": list(self.conflicts),
        }


@dataclass(frozen=True)
class TranslationSupport:
    """Confidence/support metadata for auditing why a translation reached its status."""

    confidence: float = 0.0
    extract: TrajectoryExtract = field(default_factory=TrajectoryExtract)
    template_id: str = ""
    grounded_target: str = ""
    used_context_facts: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "confidence": self.confidence, "extract": self.extract.to_dict(),
            "template_id": self.template_id, "grounded_target": self.grounded_target,
            "used_context_facts": list(self.used_context_facts),
        }


# =========================================================================================
# Translation result
# =========================================================================================

@dataclass(frozen=True)
class TranslationResult:
    """A single advisory translation. Runnable iff ``status is RUNNABLE_TEST``."""

    status: TranslationStatus
    mechanism: str
    technique_id: str
    hypothesis: Optional[HypothesisSuggestion]
    discriminating_test: str
    runnable_action: Optional[ActionSuggestion]
    provenance: TranslationProvenance
    applicability: Applicability = Applicability.PLAUSIBLE
    support: TranslationSupport = field(default_factory=TranslationSupport)
    evidence_requirements: Tuple[str, ...] = ()
    missing_requirements: Tuple[str, ...] = ()
    reason: str = ""
    schema_version: str = TRANSLATION_SCHEMA_VERSION

    def is_runnable(self) -> bool:
        return self.status is TranslationStatus.RUNNABLE_TEST and self.runnable_action is not None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value, "mechanism": self.mechanism,
            "technique_id": self.technique_id,
            "hypothesis": None if self.hypothesis is None else {
                "hypothesis_id": self.hypothesis.hypothesis_id,
                "statement": self.hypothesis.statement, "mechanism": self.hypothesis.mechanism,
                "technique": self.hypothesis.technique, "rationale": self.hypothesis.rationale,
            },
            "discriminating_test": self.discriminating_test,
            "runnable_action": None if self.runnable_action is None else {
                "hypothesis_id": self.runnable_action.hypothesis_id,
                "objective": self.runnable_action.objective, "tool": self.runnable_action.tool,
                "target": self.runnable_action.target,
                "expected_observation": self.runnable_action.expected_observation,
            },
            "provenance": self.provenance.to_dict(),
            "applicability": self.applicability.value,
            "support": self.support.to_dict(),
            "evidence_requirements": list(self.evidence_requirements),
            "missing_requirements": list(self.missing_requirements),
            "reason": self.reason, "schema_version": self.schema_version,
        }


# =========================================================================================
# Current runtime context (the "evidence must authorize" side) — only grounded facts
# =========================================================================================

@dataclass(frozen=True)
class TranslationContext:
    """Grounded current-challenge facts the translator may use. Nothing here is invented by the
    translator; the caller supplies only facts already established by the challenge package or by
    authoritative runtime evidence.

    * ``target_urls`` — grounded base URLs (challenge metadata / observed). Runnable targets are
      built ONLY from these.
    * ``available_tools`` / ``verifier_tool`` — the registered adapters (a runnable action's tool
      must be one of these, minus the verifier).
    * ``known_parameters`` — parameters actually identified for the current target.
    * ``exact_targets`` — authoritative exact target strings; if provided, a synthesized runnable
      target must byte-equal one of them (guards ``*`` vs ``%2A`` style mismatches).
    * ``disproven_mechanisms`` — mechanisms the current run's authoritative evidence has already
      disproven (current evidence wins over historical knowledge).
    """

    category: str = ""
    target_urls: Tuple[str, ...] = ()
    available_tools: Tuple[str, ...] = ()
    verifier_tool: str = ""
    known_parameters: Tuple[str, ...] = ()
    exact_targets: Tuple[str, ...] = ()
    disproven_mechanisms: Tuple[str, ...] = ()

    def probe_tool(self) -> str:
        for name in self.available_tools:
            if name and name != self.verifier_tool:
                return name
        return ""


# =========================================================================================
# Mechanism templates (generalized; seeded, extensible; NOT a hardcoded technique switch)
# =========================================================================================

@dataclass(frozen=True)
class RunnableSpec:
    """How a template *may* become a runnable discriminating test, if context grounds it.

    ``kind`` selects a small, deterministic synthesis strategy. ``param``/``payload``/
    ``expected_observation`` are technique-intrinsic constants (the canonical first test a
    specialist would run), never per-challenge invented values. ``required_context`` lists the
    grounded slots that MUST be present in :class:`TranslationContext` for synthesis to be allowed.
    ``param_must_be_grounded`` additionally requires the parameter to be one the current challenge
    actually identified.
    """

    kind: str
    param: str = ""
    payload: str = ""
    expected_observation: str = ""
    required_context: Tuple[str, ...] = ("target_url", "probe_tool")
    param_must_be_grounded: bool = False


@dataclass(frozen=True)
class MechanismTemplate:
    """Generalized, data-driven representation of a technique's canonical reasoning + test.

    A template ALWAYS yields a mechanism + hypothesis + a *described* discriminating test (usable
    as ``HYPOTHESIS_ONLY``). It yields a *runnable* action only when ``runnable`` is set AND the
    context satisfies the runnable requirements with exact alignment.
    """

    technique_id: str
    category: str
    mechanism: str
    technique: str                          # human-readable technique name
    hypothesis_id: str
    hypothesis_statement: str
    discriminating_test: str                # prose description; always available
    aliases: Tuple[str, ...] = ()           # extra technique_ids/keywords that map here
    runnable: Optional[RunnableSpec] = None


# Seeded templates. SSTI + SQLi reproduce the exact ``_WEB_TESTS`` behavior; the others are
# hypothesis-only across categories to demonstrate generalization without inventing payloads.
_SEEDED_TEMPLATES: Tuple[MechanismTemplate, ...] = (
    MechanismTemplate(
        technique_id="ssti",
        category="web",
        mechanism="ssti",
        technique="Server-Side Template Injection",
        hypothesis_id="web-ssti",
        hypothesis_statement="a server-side template may evaluate injected expressions in the name parameter",
        discriminating_test="inject a template expression (e.g. {{7*7}}) into a reflected parameter "
                            "and check whether the server evaluates it",
        aliases=("server-side-template-injection", "template-injection"),
        runnable=RunnableSpec(
            kind="web_query_probe", param="name", payload="{{7*7}}",
            expected_observation="the template evaluates the expression (e.g. 49 / EVAL=49)",
            required_context=("target_url", "probe_tool"),
        ),
    ),
    MechanismTemplate(
        technique_id="sql-injection",
        category="web",
        mechanism="sqli",
        technique="SQL Injection",
        hypothesis_id="web-sqli",
        hypothesis_statement="the id parameter may be injectable, expanding or leaking rows",
        discriminating_test="perturb the query syntax (e.g. 1' OR '1'='1) and check whether the "
                            "response changes or leaks extra rows",
        aliases=("sqli", "sql-inj"),
        runnable=RunnableSpec(
            kind="web_query_probe", param="id", payload="1' OR '1'='1",
            expected_observation="a syntax perturbation changes the response or leaks extra rows",
            required_context=("target_url", "probe_tool"),
        ),
    ),
    # --- generalization seeds (hypothesis-only: no vetted per-challenge runnable synthesis) ------
    MechanismTemplate(
        technique_id="jwt-algorithm-confusion",
        category="web",
        mechanism="jwt algorithm confusion",
        technique="JWT Algorithm Confusion",
        hypothesis_id="web-jwt-alg-confusion",
        hypothesis_statement="the verifier may trust the token-declared algorithm",
        discriminating_test="test whether changing the token's declared algorithm changes "
                            "verification behavior",
        aliases=("jwt", "jwt-confusion", "alg-confusion", "jwt-none"),
    ),
    MechanismTemplate(
        technique_id="mersenne-twister-prng",
        category="crypto",
        mechanism="predictable PRNG (Mersenne Twister)",
        technique="PRNG State Recovery",
        hypothesis_id="crypto-mt-prng",
        hypothesis_statement="outputs may derive from a predictable Mersenne Twister PRNG whose "
                             "state can be recovered from enough consecutive outputs",
        discriminating_test="collect the required number of consecutive outputs and test whether "
                            "the recovered state predicts the next output",
        aliases=("mt19937", "prng", "random-prediction", "predictable-random"),
    ),
    MechanismTemplate(
        technique_id="dynamic-analysis",
        category="reverse",
        mechanism="dynamic analysis / sandbox escape",
        technique="Dynamic Analysis",
        hypothesis_id="rev-dynamic-analysis",
        hypothesis_statement="runtime behavior may reveal a check or an escape not visible in static text",
        discriminating_test="run the target under observation and compare behavior across inputs to "
                            "locate the decision point",
        aliases=("pyjail", "sandbox-escape", "instrumentation"),
    ),
    MechanismTemplate(
        technique_id="audio-steganography",
        category="forensics",
        mechanism="audio steganography (spectrogram / frequency domain)",
        technique="Audio Steganography",
        hypothesis_id="forensics-audio-stego",
        hypothesis_statement="a payload may be hidden in the audio frequency domain",
        discriminating_test="render a spectrogram / inspect the frequency domain for hidden content",
        aliases=("stego", "spectrogram", "audio-stego"),
    ),
    MechanismTemplate(
        technique_id="format-string",
        category="pwn",
        mechanism="format string vulnerability",
        technique="Format String",
        hypothesis_id="pwn-format-string",
        hypothesis_statement="an unfiltered format specifier may leak or write memory",
        discriminating_test="submit format specifiers (e.g. %p sequences) and check whether the "
                            "output leaks stack/memory values",
        aliases=("fmtstr", "printf-leak", "format-string-bug"),
    ),
    MechanismTemplate(
        technique_id="python-jail-escape",
        category="misc",
        mechanism="python jail escape via object traversal",
        technique="Python Jail Escape",
        hypothesis_id="misc-pyjail-escape",
        hypothesis_statement="restricted execution may still allow reaching builtins via object "
                             "attribute traversal",
        discriminating_test="probe available attributes/subclasses to reach an execution primitive",
        aliases=("pyjail-escape", "jail-escape", "builtins-traversal"),
    ),
)


class TemplateRegistry:
    """Deterministic lookup of :class:`MechanismTemplate` by technique_id / alias / mechanism text.

    Seeded with the built-in templates; callers may register additional templates. This is the
    generalized replacement for a hardcoded ``technique -> payload`` switch.
    """

    def __init__(self, templates: Sequence[MechanismTemplate] = _SEEDED_TEMPLATES) -> None:
        self._by_id: Dict[str, MechanismTemplate] = {}
        self._by_alias: Dict[str, MechanismTemplate] = {}
        for tpl in templates:
            self.register(tpl)

    def register(self, template: MechanismTemplate) -> None:
        self._by_id[template.technique_id.lower()] = template
        for alias in (template.technique_id,) + template.aliases:
            self._by_alias.setdefault(_norm(alias), template)
        # allow matching by the mechanism phrase too
        self._by_alias.setdefault(_norm(template.mechanism), template)

    def lookup(self, key: str) -> Optional[MechanismTemplate]:
        if not key:
            return None
        k = key.lower().strip()
        if k in self._by_id:
            return self._by_id[k]
        return self._by_alias.get(_norm(key))

    def all_templates(self) -> Tuple[MechanismTemplate, ...]:
        """The unique registered templates (one per technique_id)."""
        return tuple(self._by_id.values())

    def match_text(self, text: str) -> Optional[MechanismTemplate]:
        """Find a template whose alias/mechanism appears as a whole token-run in free text."""
        if not text:
            return None
        low = _norm(text)
        # longest alias first so 'sql-injection' wins over a bare 'sql'
        for alias in sorted(self._by_alias, key=len, reverse=True):
            if alias and alias in low:
                return self._by_alias[alias]
        return None


def _norm(text: str) -> str:
    """Normalize to a space-padded token string so aliases match whole token-runs only.

    ``" sql injection "`` is a substring of ``" ... a sql injection here ... "`` but ``" sql "`` is
    NOT a substring of ``" sqli "`` — preventing 'sql' from matching 'sqli'.
    """
    if not text:
        return ""
    cleaned = "".join(ch if ch.isalnum() else " " for ch in text.lower())
    tokens = cleaned.split()
    if not tokens:
        return ""
    return " " + " ".join(tokens) + " "


# =========================================================================================
# Trajectory-first extraction
# =========================================================================================

def extract_trajectory(trajectory: ReasoningTrajectory) -> TrajectoryExtract:
    """Read one text per reasoning stage from the trajectory, deterministically.

    For repeated steps of the same kind, the lowest-order step wins and later ones are noted as
    conflicts (their text is not merged). Malformed/empty trajectories yield an empty extract.
    """
    def _first(kind: TrajectoryStepKind) -> Tuple[str, int, List[str]]:
        matches = sorted(
            (s for s in trajectory.steps if s.kind is kind and (s.text or "").strip()),
            key=lambda s: (s.order, s.text),
        )
        if not matches:
            return "", -1, []
        chosen = matches[0]
        conflicts = []
        for extra in matches[1:]:
            if _norm(extra.text) != _norm(chosen.text):
                conflicts.append(f"{kind.value}#{extra.order}")
        return chosen.text.strip(), chosen.order, conflicts

    mech, mech_o, c1 = _first(TrajectoryStepKind.CANDIDATE_MECHANISM)
    hyp, hyp_o, c2 = _first(TrajectoryStepKind.HYPOTHESIS)
    test, test_o, c3 = _first(TrajectoryStepKind.DISCRIMINATING_TEST)
    obs, obs_o, c4 = _first(TrajectoryStepKind.OBSERVATION)
    interp, interp_o, c5 = _first(TrajectoryStepKind.INTERPRETATION)
    nxt, nxt_o, c6 = _first(TrajectoryStepKind.NEXT_ACTION)
    conflicts = tuple(c1 + c2 + c3 + c4 + c5 + c6)
    return TrajectoryExtract(
        mechanism=mech, mechanism_order=mech_o,
        hypothesis=hyp, hypothesis_order=hyp_o,
        discriminating_test=test, discriminating_test_order=test_o,
        observation=obs, observation_order=obs_o,
        interpretation=interp, interpretation_order=interp_o,
        next_action=nxt, next_action_order=nxt_o,
        conflicts=conflicts,
    )


# Explicit host/URL detector for target alignment (section 8).
def _hosts_in_text(text: str) -> List[str]:
    hosts: List[str] = []
    for token in text.replace("(", " ").replace(")", " ").replace(",", " ").split():
        if token.startswith(("http://", "https://")):
            try:
                host = urlsplit(token).netloc
            except ValueError:
                host = ""
            if host:
                hosts.append(host.lower())
    return hosts


# =========================================================================================
# The translator
# =========================================================================================

class KnowledgeTranslator:
    """Deterministic translator for external :class:`KnowledgeRecord`s and agent experiences."""

    def __init__(self, registry: Optional[TemplateRegistry] = None) -> None:
        self.registry = registry or TemplateRegistry()

    # -- external writeups ---------------------------------------------------------------
    def translate_record(
        self, record: KnowledgeRecord, context: TranslationContext,
    ) -> Tuple[TranslationResult, ...]:
        """Translate every usable mechanism in an external writeup (deterministic order)."""
        extract = extract_trajectory(record.trajectory)
        results: List[TranslationResult] = []
        seen_templates: set = set()

        # 1) structured techniques first (technique_id -> template), in record order
        for tech in record.techniques:
            tpl = self.registry.lookup(tech.technique_id) or self.registry.match_text(tech.name)
            if tpl is None or tpl.technique_id in seen_templates:
                continue
            seen_templates.add(tpl.technique_id)
            results.append(self._translate_with_template(
                tpl, extract, context, record=record, technique=tech,
                confidence=_clamp(tech.confidence or record.trajectory.completeness or 0.5),
            ))

        # 2) trajectory-named mechanism, if no structured technique matched it
        if not results:
            tpl = self._template_from_extract(extract)
            if tpl is not None:
                results.append(self._translate_with_template(
                    tpl, extract, context, record=record, technique=None,
                    confidence=_clamp(record.trajectory.completeness or 0.4),
                ))

        # 3) nothing at all -> a single NOT_APPLICABLE advisory carrying provenance
        if not results:
            results.append(self._not_applicable(record, extract))
        return tuple(results)

    def _template_from_extract(self, extract: TrajectoryExtract) -> Optional[MechanismTemplate]:
        for text in (extract.mechanism, extract.hypothesis, extract.next_action,
                     extract.discriminating_test):
            tpl = self.registry.match_text(text)
            if tpl is not None:
                return tpl
        return None

    def _translate_with_template(
        self, tpl: MechanismTemplate, extract: TrajectoryExtract, context: TranslationContext,
        *, record: KnowledgeRecord, technique: Optional[Technique], confidence: float,
    ) -> TranslationResult:
        origin = KnowledgeOrigin.EXTERNAL_WRITEUP
        provenance = TranslationProvenance(
            origin=origin, source_id=record.record_id,
            technique_id=tpl.technique_id,
            source_uri=record.provenance.source_uri,
            document_path=record.provenance.document_path,
            mechanism_step_order=extract.mechanism_order,
            hypothesis_step_order=extract.hypothesis_order,
            test_step_order=extract.discriminating_test_order,
        )
        # trajectory text is preferred for human-facing prose; template supplies the fallback and
        # the technique-intrinsic runnable constants.
        mechanism = extract.mechanism or tpl.mechanism
        hyp_statement = extract.hypothesis or tpl.hypothesis_statement
        test_prose = extract.discriminating_test or tpl.discriminating_test
        retrieved_hosts = _record_hosts(record)
        return self._decide(
            tpl, context, provenance, mechanism, hyp_statement, test_prose, extract, confidence,
            retrieved_hosts=retrieved_hosts, applicability=Applicability.PLAUSIBLE,
            rationale_source=f"external knowledge {record.record_id}",
        )

    def _not_applicable(self, record: KnowledgeRecord, extract: TrajectoryExtract) -> TranslationResult:
        prov = TranslationProvenance(
            origin=KnowledgeOrigin.EXTERNAL_WRITEUP, source_id=record.record_id,
            source_uri=record.provenance.source_uri, document_path=record.provenance.document_path,
            mechanism_step_order=extract.mechanism_order,
        )
        return TranslationResult(
            status=TranslationStatus.NOT_APPLICABLE,
            mechanism=extract.mechanism or "", technique_id="", hypothesis=None,
            discriminating_test=extract.discriminating_test or "",
            runnable_action=None, provenance=prov,
            support=TranslationSupport(confidence=0.0, extract=extract),
            reason="no known mechanism template and no trajectory mechanism could be extracted",
        )

    # -- agent experiences ---------------------------------------------------------------
    def translate_experience(
        self, experience: Any, context: TranslationContext,
    ) -> Tuple[TranslationResult, ...]:
        """Translate a ctf_runtime ExperienceRecord (success or failure) into advisory results.

        Duck-typed so this module does not depend on ``ctf_runtime`` at import time. A failure
        experience becomes UNRESOLVED advisory knowledge (never "impossible") unless the record
        carries an authoritative DISPROVEN hypothesis for the mechanism — and even then it is only
        ``DISPROVEN_ELSEWHERE`` (a different challenge context), never a current disproof.
        """
        source_kind = getattr(experience, "source_kind", "")
        is_failure = source_kind == SOURCE_FAILURE
        origin = (KnowledgeOrigin.AGENT_FAILURE_EXPERIENCE if is_failure
                  else KnowledgeOrigin.AGENT_SUCCESS_EXPERIENCE)
        prov_src = getattr(experience, "provenance", None)
        mechanism_text = getattr(experience, "mechanism", "") or ""
        techniques = tuple(getattr(experience, "techniques", ()) or ())
        record_id = getattr(experience, "record_id", "")

        tpl = self.registry.match_text(mechanism_text)
        if tpl is None:
            for t in techniques:
                tpl = self.registry.lookup(t) or self.registry.match_text(t)
                if tpl is not None:
                    break

        provenance = TranslationProvenance(
            origin=origin, source_id=record_id,
            technique_id=(tpl.technique_id if tpl else ""),
            run_id=getattr(prov_src, "run_id", "") if prov_src else "",
            session_id=getattr(prov_src, "session_id", "") if prov_src else "",
            driver=getattr(prov_src, "driver", "") if prov_src else "",
            source_kind=source_kind,
        )

        if tpl is None:
            # Still useful as pure hypothesis-only advisory if a mechanism phrase exists.
            if not mechanism_text:
                return (TranslationResult(
                    status=TranslationStatus.NOT_APPLICABLE, mechanism="", technique_id="",
                    hypothesis=None, discriminating_test="", runnable_action=None,
                    provenance=provenance,
                    applicability=(Applicability.UNRESOLVED if is_failure else Applicability.PLAUSIBLE),
                    reason="experience carries no recognizable mechanism",
                ),)
            return (self._experience_hypothesis_only(
                experience, provenance, mechanism_text, mechanism_text,
                f"prior {'failed' if is_failure else 'successful'} attempt", is_failure),)

        if is_failure:
            applicability, reason = self._failure_applicability(experience, tpl)
            # Failure experiences are advisory hypothesis-only: a prior attempt did not establish
            # the mechanism here, so we never emit a runnable action from a failure.
            return (self._experience_hypothesis_only(
                experience, provenance,
                mechanism_text or tpl.mechanism, tpl.hypothesis_statement,
                reason, is_failure, applicability=applicability, template=tpl),)

        # success experience: may become runnable if context grounds it and evidence doesn't conflict
        extract = TrajectoryExtract(mechanism=mechanism_text, mechanism_order=-1)
        return (self._decide(
            tpl, context, provenance, mechanism_text or tpl.mechanism, tpl.hypothesis_statement,
            tpl.discriminating_test, extract, confidence=0.75,
            retrieved_hosts=(), applicability=Applicability.PLAUSIBLE,
            rationale_source=f"agent success experience {record_id}",
        ),)

    def _experience_hypothesis_only(
        self, experience: Any, provenance: TranslationProvenance, mechanism: str,
        hyp_statement: str, reason: str, is_failure: bool,
        applicability: Optional[Applicability] = None, template: Optional[MechanismTemplate] = None,
    ) -> TranslationResult:
        if applicability is None:
            applicability = Applicability.UNRESOLVED if is_failure else Applicability.PLAUSIBLE
        tid = provenance.technique_id
        hyp = HypothesisSuggestion(
            hypothesis_id=(template.hypothesis_id if template else _slug(mechanism)),
            statement=hyp_statement,
            mechanism=(template.mechanism if template else mechanism),
            technique=(template.technique if template else mechanism),
            rationale=f"advisory from {provenance.origin.value.lower()} {provenance.source_id}",
        )
        return TranslationResult(
            status=TranslationStatus.HYPOTHESIS_ONLY,
            mechanism=mechanism, technique_id=tid, hypothesis=hyp,
            discriminating_test=(template.discriminating_test if template else ""),
            runnable_action=None, provenance=provenance, applicability=applicability,
            support=TranslationSupport(confidence=0.5, template_id=tid),
            reason=reason,
        )

    def _failure_applicability(
        self, experience: Any, tpl: MechanismTemplate,
    ) -> Tuple[Applicability, str]:
        disproven = tuple(getattr(experience, "disproven", ()) or ())
        failure_classes = tuple(getattr(experience, "failure_classes", ()) or ())
        # Authoritative DISPROVEN of THIS mechanism's hypothesis (in that other challenge) only.
        if tpl.hypothesis_id in disproven:
            return (Applicability.DISPROVEN_ELSEWHERE,
                    f"{tpl.technique} was authoritatively disproven in a different challenge "
                    f"context; treat as reduced applicability, not impossible")
        if any(fc in _ENVIRONMENTAL_CLASSES for fc in failure_classes):
            envs = ", ".join(sorted(fc for fc in failure_classes if fc in _ENVIRONMENTAL_CLASSES))
            return (Applicability.UNRESOLVED,
                    f"a prior attempt was inconclusive ({envs}); {tpl.technique} remains unresolved, "
                    f"not disproven")
        return (Applicability.UNRESOLVED,
                f"a prior attempt did not establish {tpl.technique}; it remains unresolved")

    # -- the runnable-vs-hypothesis-only decision ----------------------------------------
    def _decide(
        self, tpl: MechanismTemplate, context: TranslationContext,
        provenance: TranslationProvenance, mechanism: str, hyp_statement: str, test_prose: str,
        extract: TrajectoryExtract, confidence: float, *, retrieved_hosts: Sequence[str],
        applicability: Applicability, rationale_source: str,
    ) -> TranslationResult:
        hyp = HypothesisSuggestion(
            hypothesis_id=tpl.hypothesis_id, statement=hyp_statement,
            mechanism=tpl.mechanism, technique=tpl.technique,
            rationale=f"typed candidate hypothesis derived from {rationale_source}",
        )
        req = tpl.runnable.required_context if tpl.runnable else ()
        support = TranslationSupport(confidence=confidence, extract=extract, template_id=tpl.technique_id)

        # current authoritative evidence wins: if this mechanism is already disproven, advise conflict
        if _norm(tpl.mechanism) in {_norm(m) for m in context.disproven_mechanisms} or \
                _norm(mechanism) in {_norm(m) for m in context.disproven_mechanisms}:
            return TranslationResult(
                status=TranslationStatus.ADVISORY_CONFLICT, mechanism=mechanism,
                technique_id=tpl.technique_id, hypothesis=hyp, discriminating_test=test_prose,
                runnable_action=None, provenance=provenance,
                applicability=Applicability.DISPROVEN_ELSEWHERE, support=support,
                evidence_requirements=tuple(req),
                reason="current authoritative evidence disproves this mechanism; advisory only",
            )

        # no runnable synthesis for this template -> hypothesis-only (knowledge still useful)
        if tpl.runnable is None:
            return TranslationResult(
                status=TranslationStatus.HYPOTHESIS_ONLY, mechanism=mechanism,
                technique_id=tpl.technique_id, hypothesis=hyp, discriminating_test=test_prose,
                runnable_action=None, provenance=provenance, applicability=applicability,
                support=support, evidence_requirements=tuple(req),
                reason="mechanism recognized but no vetted runnable synthesis for this technique; "
                       "propose the described discriminating test instead",
            )

        spec = tpl.runnable
        missing: List[str] = []
        used_facts: List[str] = []

        base_url = context.target_urls[0] if context.target_urls else ""
        if "target_url" in spec.required_context:
            if not base_url:
                missing.append("target_url")
            else:
                used_facts.append(f"target_url={base_url}")

        probe = context.probe_tool()
        if "probe_tool" in spec.required_context:
            if not probe:
                missing.append("probe_tool")
            else:
                used_facts.append(f"probe_tool={probe}")

        if spec.param_must_be_grounded:
            if spec.param not in context.known_parameters:
                missing.append(f"parameter:{spec.param}")
            else:
                used_facts.append(f"param={spec.param}")

        if missing:
            return TranslationResult(
                status=TranslationStatus.HYPOTHESIS_ONLY, mechanism=mechanism,
                technique_id=tpl.technique_id, hypothesis=hyp, discriminating_test=test_prose,
                runnable_action=None, provenance=provenance, applicability=applicability,
                support=support, evidence_requirements=tuple(spec.required_context),
                missing_requirements=tuple(missing),
                reason="insufficient grounded evidence to synthesize a runnable test "
                       f"(missing: {', '.join(missing)}); returning hypothesis-only",
            )

        # target/evidence alignment: retrieved knowledge that names a DIFFERENT host is a mismatch.
        current_host = urlsplit(base_url).netloc.lower()
        if retrieved_hosts and current_host and current_host not in retrieved_hosts:
            return TranslationResult(
                status=TranslationStatus.HYPOTHESIS_ONLY, mechanism=mechanism,
                technique_id=tpl.technique_id, hypothesis=hyp, discriminating_test=test_prose,
                runnable_action=None, provenance=provenance, applicability=applicability,
                support=support, evidence_requirements=tuple(spec.required_context),
                reason=f"retrieved target host(s) {sorted(set(retrieved_hosts))} do not match the "
                       f"current target host {current_host!r}; alignment failed, hypothesis-only",
            )

        # synthesize the runnable target from GROUNDED base + technique-intrinsic param/payload,
        # using the SAME quoting as the existing bridge (byte-identical construction).
        target = f"{base_url}?{spec.param}={quote(spec.payload)}"

        # exact-target byte alignment (guards '*' vs '%2A' style mismatch)
        if context.exact_targets and target not in context.exact_targets:
            return TranslationResult(
                status=TranslationStatus.HYPOTHESIS_ONLY, mechanism=mechanism,
                technique_id=tpl.technique_id, hypothesis=hyp, discriminating_test=test_prose,
                runnable_action=None, provenance=provenance, applicability=applicability,
                support=TranslationSupport(confidence=confidence, extract=extract,
                                           template_id=tpl.technique_id, grounded_target=target),
                evidence_requirements=tuple(spec.required_context),
                reason=f"synthesized target {target!r} does not byte-match an authoritative exact "
                       f"target; refusing to 'fix' encoding, hypothesis-only",
            )

        action = ActionSuggestion(
            hypothesis_id=tpl.hypothesis_id,
            objective=f"knowledge-derived discriminating test for {tpl.technique}",
            tool=probe, target=target, input_data=None, relevant_parameters={},
            prerequisites=(),
            expected_observation=spec.expected_observation,  # technique-intrinsic, never invented
            rationale="knowledge named this mechanism; propose its standard cheapest discriminating "
                      "test (execution/classification/verification remain the kernel's)",
            candidate_flag="",  # translator NEVER carries a flag (historical flags are not current)
        )
        return TranslationResult(
            status=TranslationStatus.RUNNABLE_TEST, mechanism=mechanism,
            technique_id=tpl.technique_id, hypothesis=hyp, discriminating_test=test_prose,
            runnable_action=action, provenance=provenance, applicability=applicability,
            support=TranslationSupport(confidence=confidence, extract=extract,
                                       template_id=tpl.technique_id, grounded_target=target,
                                       used_context_facts=tuple(used_facts)),
            evidence_requirements=tuple(spec.required_context),
            reason="grounded target + probe tool available and aligned; runnable discriminating test",
        )


# =========================================================================================
# helpers
# =========================================================================================

def _clamp(value: float) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, v))


def _slug(text: str) -> str:
    out = "".join(ch if ch.isalnum() else "-" for ch in text.lower()).strip("-")
    while "--" in out:
        out = out.replace("--", "-")
    return out[:48] or "mechanism"


def _record_hosts(record: KnowledgeRecord) -> Tuple[str, ...]:
    hosts: List[str] = []
    for step in record.trajectory.steps:
        hosts.extend(_hosts_in_text(step.text or ""))
    for tech in record.techniques:
        hosts.extend(_hosts_in_text(tech.evidence or ""))
    return tuple(dict.fromkeys(hosts))
