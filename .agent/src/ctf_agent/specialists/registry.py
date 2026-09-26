from __future__ import annotations

from typing import Tuple

from .base import Specialist, SpecialistContext
from .crypto import CryptoSpecialist
from .forensics import ForensicsSpecialist
from .pwn import PwnSpecialist
from .reverse import ReverseSpecialist
from .selection import SpecialistSelection, SpecialistSelector
from .web import WebSpecialist


class SpecialistRegistry:
    """Explicit set of available specialists plus a selector. No dynamic import / discovery."""

    def __init__(self, specialists: Tuple[Specialist, ...], *, threshold: float = 0.45) -> None:
        if not specialists:
            raise ValueError("SpecialistRegistry requires at least one specialist")
        self._specialists = specialists
        self._selector = SpecialistSelector(specialists, threshold=threshold)

    @classmethod
    def default(cls, *, threshold: float = 0.45) -> "SpecialistRegistry":
        """The Phase 4 initial set: web, crypto, reverse, forensics, pwn."""
        return cls(
            (
                WebSpecialist(),
                CryptoSpecialist(),
                ReverseSpecialist(),
                ForensicsSpecialist(),
                PwnSpecialist(),
            ),
            threshold=threshold,
        )

    @property
    def specialists(self) -> Tuple[Specialist, ...]:
        return self._specialists

    def names(self) -> Tuple[str, ...]:
        return tuple(s.name for s in self._specialists)

    def select(self, context: SpecialistContext) -> SpecialistSelection:
        return self._selector.select(context)
