"""LLMReasoningSource — the production implementation of the frozen ``ReasoningSource`` protocol.

It is the ONLY new place an external model enters the architecture. It:
  1. receives the current ``ChallengeContext`` (read-only agent state),
  2. builds a TEXT reasoning request (challenge facts + current hypotheses/evidence + the NAMES of
     registered tools + a strict JSON schema),
  3. asks the routed model for STRUCTURED output,
  4. parses the JSON defensively,
  5. validates every item through the EXISTING ``proposals.validate_*`` functions,
  6. converts survivors into the EXISTING typed ``*Suggestion`` objects.

The model is given no tool handles and cannot execute anything. Any action naming a tool that is
not a registered trusted adapter is rejected by ``validate_action_suggestion`` before it can reach
the planner. Any prose attempting a state transition ("mark verified", ...) is rejected by
``_reject_forbidden_phrases``. This class never touches kernel/evidence state and never verifies.

It wraps an optional ``base`` ``ReasoningSource`` (in production, the frozen deterministic
``SpecialistReasoningSource``) so specialist proposals remain available and so the frozen
``_project_result`` keeps working; LLM proposals are merged on top, de-duplicated by id.
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable, List, Optional, Tuple

from ctf_agent.adapters import AdapterRegistry
from ctf_agent.context import ChallengeContext, FactState
from ctf_agent.proposals import (
    ActionSuggestion,
    HypothesisSuggestion,
    InterpretationNote,
    ProposalRejected,
    validate_action_suggestion,
    validate_hypothesis_suggestion,
    validate_interpretation_note,
)

from .llm_client import LLMClient, LLMRequest
from .routing import ModelRouter, RouteDecision, RoutingSignals

_SCHEMA_HINT = (
    'Respond with ONLY a JSON object of the form: {"hypotheses":[{"id","statement","mechanism",'
    '"technique","rationale"}],"actions":[{"hypothesis_id","objective","tool","target",'
    '"input_data","relevant_parameters","prerequisites","expected_observation","candidate_flag",'
    '"rationale"}],"notes":[{"hypothesis_id","note"}]}. You may ONLY use a tool listed in '
    "AVAILABLE_TOOLS. You cannot execute anything, verify a flag, or change any state — you only "
    "propose. Never claim a hypothesis is verified or disproven."
)


class LLMReasoningSource:
    def __init__(
        self,
        client: LLMClient,
        *,
        adapters: AdapterRegistry,
        router: Optional[ModelRouter] = None,
        base: Optional[object] = None,
        flag_format: str = "",
        event_sink: Optional[Callable[[str, dict], None]] = None,
    ) -> None:
        self.client = client
        self.adapters = adapters
        self.router = router or ModelRouter()
        self.base = base
        self.flag_format = flag_format
        self._event_sink = event_sink
        # observability / routing state
        self.last_route: Optional[RouteDecision] = None
        self.route_history: List[RouteDecision] = []
        self.rejections: List[str] = []
        self._invocations = 0
        self._last_supported = 0
        self._last_evidence = 0
        self._stall_steps = 0
        # per-context cache (loop calls suggest_hypotheses then suggest_actions with same context)
        self._cache_key: Optional[int] = None
        self._cache: Optional[Tuple[tuple, tuple, tuple]] = None

    # -- ReasoningSource protocol -----------------------------------------------------------
    def suggest_hypotheses(self, context: ChallengeContext) -> Tuple[HypothesisSuggestion, ...]:
        base = tuple(self.base.suggest_hypotheses(context)) if self.base else ()
        hyps, _a, _n = self._llm_for(context)
        base_ids = {h.hypothesis_id for h in base}
        return base + tuple(h for h in hyps if h.hypothesis_id not in base_ids)

    def suggest_actions(self, context: ChallengeContext) -> Tuple[ActionSuggestion, ...]:
        base = tuple(self.base.suggest_actions(context)) if self.base else ()
        _h, acts, _n = self._llm_for(context)
        return base + acts

    def interpret(self, context: ChallengeContext) -> Tuple[InterpretationNote, ...]:
        base = tuple(self.base.interpret(context)) if self.base else ()
        _h, _a, notes = self._llm_for(context)
        return base + notes

    # -- LLM invocation (once per context object) -------------------------------------------
    def _llm_for(self, context: ChallengeContext):
        if self._cache_key == id(context) and self._cache is not None:
            return self._cache
        result = self._invoke(context)
        self._cache_key = id(context)
        self._cache = result
        return result

    def _invoke(self, context: ChallengeContext):
        self._invocations += 1
        signals = self._signals(context)
        decision = self.router.select(signals)
        self.last_route = decision
        self.route_history.append(decision)
        self._emit("model_routed", decision.to_dict())

        prompt = self._build_prompt(context)
        request = LLMRequest(model=decision.model, prompt=prompt, schema_hint=_SCHEMA_HINT)
        try:
            raw = self.client.complete(request)
        except Exception as exc:  # model/transport error -> deterministic fallback model
            fb = self.router.fallback(signals, f"{type(exc).__name__}: {exc}")
            self.last_route = fb
            self.route_history.append(fb)
            self._emit("model_fallback", fb.to_dict())
            try:
                raw = self.client.complete(LLMRequest(model=fb.model, prompt=prompt, schema_hint=_SCHEMA_HINT))
            except Exception:
                return ((), (), ())  # no proposals; loop BLOCKs safely, never crashes
        return self._parse_and_validate(raw)

    # -- signals ----------------------------------------------------------------------------
    def _signals(self, context: ChallengeContext) -> RoutingSignals:
        views = context.hypothesis_views()
        supported = sum(1 for v in views if v.state is FactState.SUPPORTED)
        uncertainty = sum(
            1 for v in views if v.state in (FactState.UNRESOLVED, FactState.PLAUSIBLE, FactState.BLOCKED)
        )
        evidence_count = len(context.snapshot.evidence)
        # stall = invocations since last gain in supported hypotheses or evidence
        if supported > self._last_supported or evidence_count > self._last_evidence:
            self._stall_steps = 0
        else:
            self._stall_steps += 1
        self._last_supported = supported
        self._last_evidence = evidence_count
        last_failure = self._last_failure_class(context)
        return RoutingSignals(
            category=context.metadata.category or "",
            difficulty=self._infer_difficulty(context),
            uncertainty=uncertainty,
            supported_count=supported,
            evidence_count=evidence_count,
            stall_steps=self._stall_steps,
            last_failure_class=last_failure,
            novelty=(supported == 0),
        )

    @staticmethod
    def _infer_difficulty(context: ChallengeContext) -> str:
        meta = context.metadata
        # advisory only: fewer solves / higher points -> harder. Missing signals -> "".
        if meta.solves and meta.solves <= 5:
            return "hard"
        if meta.points and meta.points >= 400:
            return "hard"
        if meta.points and meta.points >= 200:
            return "medium"
        return ""

    @staticmethod
    def _last_failure_class(context: ChallengeContext) -> str:
        for evidence in reversed(context.snapshot.evidence):
            rc = evidence.result_class.value
            if rc in {
                "RATE_LIMIT", "TIMEOUT", "AUTH_FAILURE", "AUTHZ_FAILURE", "NETWORK_FAILURE",
                "TOOL_FAILURE", "ENVIRONMENT_FAILURE",
            }:
                return rc
            break  # only the most recent evidence record matters
        return ""

    # -- prompt construction (TEXT ONLY) ----------------------------------------------------
    def _build_prompt(self, context: ChallengeContext) -> str:
        meta = context.metadata
        lines: List[str] = []
        lines.append("You are a CTF reasoning source. You propose typed reasoning ONLY.")
        lines.append(_SCHEMA_HINT)
        lines.append("")
        lines.append("== CHALLENGE ==")
        lines.append(f"name: {meta.name}")
        lines.append(f"category: {meta.category}")
        if meta.description:
            lines.append(f"description: {meta.description}")
        if meta.hints:
            lines.append(f"hints: {list(meta.hints)}")
        if meta.flag_format:
            lines.append(f"flag_format: {meta.flag_format}")
        if meta.urls:
            lines.append(f"urls: {list(meta.urls)}")
        if meta.files:
            lines.append(f"files: {list(meta.files)}")
        lines.append("")
        lines.append("== AVAILABLE_TOOLS (you may ONLY reference these tool names) ==")
        lines.append(", ".join(self.adapters.available_tools()) or "(none)")
        lines.append("")
        lines.append("== CURRENT HYPOTHESES ==")
        views = context.hypothesis_views()
        if views:
            for v in views:
                lines.append(f"- {v.hypothesis.hypothesis_id} [{v.state}] {v.hypothesis.statement}")
        else:
            lines.append("(none yet)")
        lines.append("")
        lines.append("== CURRENT EVIDENCE (observed; use to justify a candidate_flag) ==")
        if context.snapshot.evidence:
            for e in context.snapshot.evidence[-6:]:
                execution = e.observation.execution
                body = " ".join((execution.stdout or "", execution.response_body or "")).strip()
                lines.append(
                    f"- {e.evidence_id} class={e.result_class.value} status={e.status.value} "
                    f"affects={list(e.affected_hypotheses)} output={body[:240]!r}"
                )
        else:
            lines.append("(no evidence yet — propose the cheapest discriminating test first)")
        lines.append("")
        lines.append(
            "Propose the single cheapest discriminating next action. Only set candidate_flag if a "
            "flag string is already visible in CURRENT EVIDENCE above. Output JSON now."
        )
        return "\n".join(lines)

    # -- parse + validate through the EXISTING pipeline -------------------------------------
    def _parse_and_validate(self, raw: str):
        data = self._safe_json(raw)
        hyps: List[HypothesisSuggestion] = []
        acts: List[ActionSuggestion] = []
        notes: List[InterpretationNote] = []

        for item in _as_list(data.get("hypotheses")):
            try:
                suggestion = HypothesisSuggestion(
                    hypothesis_id=str(item["id"]),
                    statement=str(item["statement"]),
                    mechanism=str(item.get("mechanism", "")),
                    technique=str(item.get("technique", "")),
                    rationale=str(item.get("rationale", "")),
                )
                validate_hypothesis_suggestion(suggestion)
                hyps.append(suggestion)
            except (KeyError, TypeError, ProposalRejected) as exc:
                self._reject("hypothesis", exc)

        for item in _as_list(data.get("actions")):
            try:
                suggestion = ActionSuggestion(
                    hypothesis_id=str(item["hypothesis_id"]),
                    objective=str(item["objective"]),
                    tool=str(item["tool"]),
                    target=str(item["target"]),
                    input_data=item.get("input_data"),
                    relevant_parameters=item.get("relevant_parameters") or {},
                    prerequisites=tuple(str(p) for p in _as_list(item.get("prerequisites"))),
                    expected_observation=str(item.get("expected_observation", "")),
                    rationale=str(item.get("rationale", "")),
                    candidate_flag=str(item.get("candidate_flag", "")),
                )
                # This is the hard tool-isolation gate: unregistered tools (shell/execute_pwsh/etc.)
                # and state-transition prose are rejected here, before the planner ever sees them.
                validate_action_suggestion(suggestion, self.adapters)
                acts.append(suggestion)
            except (KeyError, TypeError, ProposalRejected) as exc:
                self._reject("action", exc)

        for item in _as_list(data.get("notes")):
            try:
                note = InterpretationNote(
                    hypothesis_id=str(item["hypothesis_id"]), note=str(item["note"])
                )
                validate_interpretation_note(note)
                notes.append(note)
            except (KeyError, TypeError, ProposalRejected) as exc:
                self._reject("note", exc)

        return (tuple(hyps), tuple(acts), tuple(notes))

    @staticmethod
    def _safe_json(raw: str) -> dict:
        if not isinstance(raw, str):
            return {}
        text = raw.strip()
        # tolerate a fenced ```json block or leading prose before the object
        fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fence:
            text = fence.group(1)
        else:
            brace = text.find("{")
            if brace > 0:
                text = text[brace:]
        try:
            parsed = json.loads(text)
        except (ValueError, TypeError):
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def _reject(self, kind: str, exc: Exception) -> None:
        msg = f"{kind} rejected: {type(exc).__name__}: {exc}"
        self.rejections.append(msg)
        self._emit("proposal_rejected", {"kind": kind, "reason": str(exc)})

    def _emit(self, kind: str, payload: dict) -> None:
        if self._event_sink is not None:
            self._event_sink(kind, payload)


def _as_list(value: Any) -> list:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]
