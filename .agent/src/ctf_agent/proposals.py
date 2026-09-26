from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Tuple

from .adapters import AdapterRegistry


# Free-text phrases that would try to smuggle an authoritative state transition through prose.
# Any suggestion containing one of these (case-insensitive) is rejected outright: the LLM boundary
# must never be allowed to *say* a hypothesis is disproven/verified and have that stick.
_FORBIDDEN_PHRASES: Tuple[str, ...] = (
    "mark disproven",
    "mark as disproven",
    "mark verified",
    "mark as verified",
    "assume verified",
    "declare verified",
    "declare disproven",
    "treat as verified",
    "treat as disproven",
    "is now verified",
    "is now disproven",
)


class ProposalRejected(ValueError):
    """Raised when a suggestion fails deterministic validation at the LLM boundary."""


@dataclass(frozen=True)
class HypothesisSuggestion:
    """What an LLM (or any external reasoner) may propose about a new hypothesis.

    This is plain data. It has no ``status`` field and no way to express one -- proposing a
    hypothesis can only ever result in an ``OPEN`` ``Hypothesis`` (see
    ``HypothesisBoard.propose_hypothesis``), regardless of what free text accompanies it.
    """

    hypothesis_id: str
    statement: str
    mechanism: str = ""
    technique: str = ""
    rationale: str = ""


@dataclass(frozen=True)
class ActionSuggestion:
    """What an LLM may propose as a next action. Must resolve to a registered tool.

    ``candidate_flag`` lets the LLM say "if this action's result looks right, try submitting this
    string as the flag" -- it is advisory only. Naming a candidate here never verifies it: the loop
    still runs it through ``TrustKernel.process(candidate=...)``, and the kernel's
    ``VerificationController`` independently decides, from the actual observed evidence, whether it
    is accepted. An LLM cannot verify a flag merely by suggesting one.
    """

    hypothesis_id: str
    objective: str
    tool: str
    target: str
    input_data: object = None
    relevant_parameters: Mapping[str, object] | None = None
    prerequisites: Tuple[str, ...] = ()
    expected_observation: str = ""
    rationale: str = ""
    candidate_flag: str = ""


@dataclass(frozen=True)
class InterpretationNote:
    """An LLM's free-text interpretation of an already-classified observation.

    Interpretation notes are advisory commentary only. They are stored for audit/journal purposes
    and are never consulted by the kernel, the hypothesis board, or the verification controller.
    """

    hypothesis_id: str
    note: str


def validate_hypothesis_suggestion(suggestion: HypothesisSuggestion) -> HypothesisSuggestion:
    if not suggestion.hypothesis_id.strip():
        raise ProposalRejected("hypothesis_id must be non-empty")
    if not suggestion.statement.strip():
        raise ProposalRejected("statement must be non-empty")
    _reject_forbidden_phrases(suggestion.statement)
    _reject_forbidden_phrases(suggestion.rationale)
    return suggestion


def validate_action_suggestion(
    suggestion: ActionSuggestion, adapters: AdapterRegistry
) -> ActionSuggestion:
    if not suggestion.objective.strip():
        raise ProposalRejected("objective must be non-empty")
    if not suggestion.hypothesis_id.strip():
        raise ProposalRejected("hypothesis_id must be non-empty")
    if not adapters.is_registered(suggestion.tool):
        raise ProposalRejected(
            f"tool '{suggestion.tool}' is not registered; "
            f"available: {adapters.available_tools()}"
        )
    if not suggestion.target.strip():
        raise ProposalRejected("target must be non-empty")
    _reject_forbidden_phrases(suggestion.objective)
    _reject_forbidden_phrases(suggestion.rationale)
    return suggestion


def validate_interpretation_note(note: InterpretationNote) -> InterpretationNote:
    if not note.hypothesis_id.strip():
        raise ProposalRejected("hypothesis_id must be non-empty")
    _reject_forbidden_phrases(note.note)
    return note


def _reject_forbidden_phrases(text: str) -> None:
    lowered = text.lower()
    for phrase in _FORBIDDEN_PHRASES:
        if phrase in lowered:
            raise ProposalRejected(
                f"suggestion text attempts to assert a state transition ('{phrase}'); "
                "only TrustKernel.process() may change hypothesis/verification state"
            )
