from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Tuple, runtime_checkable

from .context import ChallengeContext
from .proposals import ActionSuggestion, HypothesisSuggestion, InterpretationNote


@runtime_checkable
class ReasoningSource(Protocol):
    """The one interface any 'brain' (real LLM, script, human) must satisfy.

    A ``ReasoningSource`` never touches kernel state. It only returns plain ``*Suggestion``
    dataclasses, which must then pass through ``proposals.validate_*`` before anything downstream
    (the planner) may act on them.
    """

    def suggest_hypotheses(self, context: ChallengeContext) -> Tuple[HypothesisSuggestion, ...]: ...

    def suggest_actions(self, context: ChallengeContext) -> Tuple[ActionSuggestion, ...]: ...

    def interpret(self, context: ChallengeContext) -> Tuple[InterpretationNote, ...]: ...


@dataclass
class ScriptedReasoningSource:
    """A deterministic test double standing in for a real LLM.

    Real integration (Phase 4+) would implement ``ReasoningSource`` against an actual model behind
    this exact same interface; nothing else in Phase 3 would need to change, because the planner
    and loop only ever see validated ``*Suggestion`` objects, never raw model output.
    """

    hypothesis_script: Tuple[HypothesisSuggestion, ...] = field(default_factory=tuple)
    action_script: Tuple[ActionSuggestion, ...] = field(default_factory=tuple)
    interpretation_script: Tuple[InterpretationNote, ...] = field(default_factory=tuple)

    def suggest_hypotheses(self, context: ChallengeContext) -> Tuple[HypothesisSuggestion, ...]:
        del context  # the script is fixed; a real source would read context here
        return self.hypothesis_script

    def suggest_actions(self, context: ChallengeContext) -> Tuple[ActionSuggestion, ...]:
        del context
        return self.action_script

    def interpret(self, context: ChallengeContext) -> Tuple[InterpretationNote, ...]:
        del context
        return self.interpretation_script
