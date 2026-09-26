from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .kernel import PipelineResult
from .models import Hypothesis, HypothesisStatus


@dataclass(frozen=True)
class HypothesisMeta:
    """Phase-3-only advisory metadata about a hypothesis.

    None of these fields carry trust weight. They exist so the planner/LLM boundary can annotate a
    hypothesis (mechanism, technique, suggested tests, priority) without touching the Phase 2
    ``Hypothesis`` dataclass, whose only authoritative fields are ``status`` and the three evidence
    tuples set by ``apply_evidence``.
    """

    hypothesis_id: str
    mechanism: str = ""
    technique: str = ""
    discriminating_tests: Tuple[str, ...] = ()
    priority: int = 1  # 0 means "branch closed / low value", higher means more worth testing


class HypothesisAuthorityError(RuntimeError):
    """Raised if something outside kernel/hypothesis output tries to force a terminal status."""


_TERMINAL_STATUSES = {HypothesisStatus.SUPPORTED, HypothesisStatus.DISPROVEN}


class HypothesisBoard:
    """A read cache of kernel-produced hypothesis state plus advisory Phase 3 metadata.

    ``record()`` is the *only* way a ``Hypothesis`` enters the board, and it only ever accepts a
    ``Hypothesis`` that came out of a ``PipelineResult`` (i.e. was produced by
    ``TrustKernel.process()`` -> ``apply_evidence()``). There is no method here that constructs a
    ``Hypothesis`` with a terminal status directly; ``propose_hypothesis`` seeds ``OPEN`` hypotheses
    only, and the kernel is what may later move it to SUPPORTED/DISPROVEN via genuine evidence.
    """

    def __init__(self) -> None:
        self._hypotheses: dict[str, Hypothesis] = {}
        self._meta: dict[str, HypothesisMeta] = {}

    def propose_hypothesis(
        self,
        hypothesis_id: str,
        statement: str,
        *,
        mechanism: str = "",
        technique: str = "",
        discriminating_tests: Tuple[str, ...] = (),
    ) -> Hypothesis:
        """Seed a new OPEN hypothesis. Cannot create a hypothesis with a terminal status."""
        if hypothesis_id in self._hypotheses:
            raise ValueError(f"hypothesis '{hypothesis_id}' already exists")
        hypothesis = Hypothesis(hypothesis_id=hypothesis_id, statement=statement)
        self._hypotheses[hypothesis_id] = hypothesis
        self._meta[hypothesis_id] = HypothesisMeta(
            hypothesis_id=hypothesis_id,
            mechanism=mechanism,
            technique=technique,
            discriminating_tests=discriminating_tests,
        )
        return hypothesis

    def record(self, result: PipelineResult) -> Hypothesis:
        """Mirror a kernel pipeline result into the board's cache.

        This never assigns a status; it stores exactly the ``Hypothesis`` object the kernel already
        produced. If a caller somehow constructed a terminal-status ``Hypothesis`` by hand (bypassing
        ``apply_evidence``), recording it is refused, because this method is the single choke point
        through which board state changes -- and it demands provenance in the form of a real
        ``PipelineResult``.
        """
        hypothesis = result.hypothesis
        if hypothesis.status in _TERMINAL_STATUSES and not hypothesis.last_updated:
            raise HypothesisAuthorityError(
                "a terminal-status hypothesis must carry evidence provenance "
                "(last_updated set by apply_evidence); refusing to record"
            )
        self._hypotheses[hypothesis.hypothesis_id] = hypothesis
        self._meta.setdefault(
            hypothesis.hypothesis_id, HypothesisMeta(hypothesis_id=hypothesis.hypothesis_id)
        )
        return hypothesis

    def set_priority(self, hypothesis_id: str, priority: int) -> None:
        """Advisory-only: lower priority to close a low-value branch without declaring disproof."""
        current = self._meta[hypothesis_id]
        self._meta[hypothesis_id] = HypothesisMeta(
            hypothesis_id=current.hypothesis_id,
            mechanism=current.mechanism,
            technique=current.technique,
            discriminating_tests=current.discriminating_tests,
            priority=priority,
        )

    def get(self, hypothesis_id: str) -> Hypothesis:
        return self._hypotheses[hypothesis_id]

    def meta(self, hypothesis_id: str) -> HypothesisMeta:
        return self._meta[hypothesis_id]

    def all_hypotheses(self) -> Tuple[Hypothesis, ...]:
        return tuple(self._hypotheses.values())

    def open_hypotheses(self) -> Tuple[Hypothesis, ...]:
        """Hypotheses that are not yet terminal and still have nonzero priority."""
        return tuple(
            h
            for h in self._hypotheses.values()
            if h.status not in _TERMINAL_STATUSES and self._meta[h.hypothesis_id].priority > 0
        )

    def unresolved_hypotheses(self) -> Tuple[Hypothesis, ...]:
        return tuple(
            h for h in self.open_hypotheses() if h.status is HypothesisStatus.UNRESOLVED
        )
