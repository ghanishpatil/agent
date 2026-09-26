from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .base import Specialist, SpecialistContext


@dataclass(frozen=True)
class SpecialistSelection:
    """Which specialists the Strategic Brain chose to consult, and why (for audit/metrics)."""

    selected: Tuple[Specialist, ...]
    scored: Tuple[Tuple[str, float], ...]  # (specialist_name, relevance) for every candidate


class SpecialistSelector:
    """Chooses the relevant subset of specialists -- NOT all of them every time.

    A specialist is selected if it is the exact category-match for the challenge (a web challenge
    always consults the web specialist), OR its relevance clears the higher *cross-domain* bar.
    The cross-domain bar is deliberately high so generic keyword overlap (e.g. a crypto challenge
    mentioning "xor"/"key", which are also reverse-ish words) does NOT drag in an off-domain
    specialist -- only a strong, specific cross-domain signal (e.g. JWT for crypto, an ELF binary
    for reverse/pwn) crosses it. Selection is deterministic.
    """

    def __init__(self, specialists: Tuple[Specialist, ...], *, threshold: float = 0.45) -> None:
        self._specialists = specialists
        self._threshold = threshold

    def select(self, context: SpecialistContext) -> SpecialistSelection:
        challenge_category = context.challenge.metadata.category.lower()
        scored: list[Tuple[str, float]] = []
        chosen: list[Tuple[float, Specialist]] = []
        for specialist in self._specialists:
            relevance = specialist.relevance(context)
            scored.append((specialist.name, relevance))
            category_match = specialist.category.lower() == challenge_category or (
                specialist.category.lower() == "reverse" and challenge_category == "rev"
            )
            if category_match or relevance >= self._threshold:
                chosen.append((relevance, specialist))
        chosen.sort(key=lambda item: (-item[0], item[1].name))
        return SpecialistSelection(
            selected=tuple(specialist for _, specialist in chosen),
            scored=tuple(sorted(scored, key=lambda item: (-item[1], item[0]))),
        )
