from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Tuple

from .hypothesis_engine import HypothesisBoard
from .kernel import KernelSnapshot, TrustKernel
from .models import ControlDecision, Evidence, Freshness, Hypothesis, HypothesisStatus


class FactState(str, Enum):
    """The 7 states the spec requires the context model to distinguish."""

    KNOWN = "KNOWN"  # a static challenge fact supplied up front (name, category, files, ...)
    SUPPORTED = "SUPPORTED"
    PLAUSIBLE = "PLAUSIBLE"  # advisory-memory suggestion; not yet evidence-backed
    UNRESOLVED = "UNRESOLVED"
    BLOCKED = "BLOCKED"
    DISPROVEN = "DISPROVEN"
    VERIFIED = "VERIFIED"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ChallengeMetadata:
    """Static, author-supplied facts about the challenge. These are ``KNOWN`` by definition."""

    name: str
    category: str
    points: int = 0
    solves: int = 0
    description: str = ""
    hints: Tuple[str, ...] = ()
    flag_format: str = ""
    files: Tuple[str, ...] = ()
    urls: Tuple[str, ...] = ()


@dataclass(frozen=True)
class HypothesisView:
    hypothesis: Hypothesis
    state: FactState
    evidence_count: int


@dataclass(frozen=True)
class ChallengeContext:
    """A read-only view over kernel state plus static challenge metadata.

    ``ChallengeContext`` does not store truth itself -- every hypothesis/evidence fact is derived
    live from a ``KernelSnapshot``. This guarantees current evidence always outranks anything else,
    because there is nowhere else for a hypothesis's state to come from.
    """

    metadata: ChallengeMetadata
    snapshot: KernelSnapshot
    board: HypothesisBoard

    def hypothesis_views(self) -> Tuple[HypothesisView, ...]:
        views = []
        for hypothesis in self.board.all_hypotheses():
            views.append(
                HypothesisView(
                    hypothesis=hypothesis,
                    state=self._state_for(hypothesis),
                    evidence_count=self._evidence_count(hypothesis),
                )
            )
        return tuple(views)

    def facts(self) -> Mapping[str, FactState]:
        """A flat KNOWN-fact map for the static metadata fields that are populated."""
        facts: dict[str, FactState] = {"name": FactState.KNOWN, "category": FactState.KNOWN}
        if self.metadata.flag_format:
            facts["flag_format"] = FactState.KNOWN
        if self.metadata.files:
            facts["files"] = FactState.KNOWN
        if self.metadata.urls:
            facts["urls"] = FactState.KNOWN
        return facts

    def is_verified(self) -> bool:
        return self.snapshot.verification.decision is ControlDecision.STOP

    def _evidence_count(self, hypothesis: Hypothesis) -> int:
        return sum(
            1
            for evidence in self.snapshot.evidence
            if hypothesis.hypothesis_id in evidence.affected_hypotheses
            and evidence.freshness is Freshness.CURRENT
        )

    def _state_for(self, hypothesis: Hypothesis) -> FactState:
        # Note: a globally verified run does not retroactively verify every hypothesis; only the
        # hypothesis's own status (set by real evidence via apply_evidence) determines its state.
        if hypothesis.status is HypothesisStatus.SUPPORTED:
            return FactState.SUPPORTED
        if hypothesis.status is HypothesisStatus.DISPROVEN:
            return FactState.DISPROVEN
        if hypothesis.status is HypothesisStatus.UNRESOLVED:
            meta = self.board.meta(hypothesis.hypothesis_id)
            if meta.priority <= 0:
                return FactState.BLOCKED
            return FactState.UNRESOLVED
        return FactState.UNRESOLVED if hypothesis.unresolved_evidence else FactState.PLAUSIBLE


def build_context(
    metadata: ChallengeMetadata, kernel: TrustKernel, board: HypothesisBoard
) -> ChallengeContext:
    return ChallengeContext(metadata=metadata, snapshot=kernel.snapshot(), board=board)
