"""Phase 5 test support — re-exports the frozen benchmark helpers.

The canonical definitions live in ``ctf_bench.phase5_benchmark`` so the tests, the
baseline generator, and any later augmented-knowledge experiment all exercise the
identical challenges. This shim preserves the existing ``from .support import ...``
call sites.
"""

from __future__ import annotations

from ctf_bench.phase5_benchmark import (  # noqa: F401
    ClassicalTool,
    LocalVerifier,
    UnavailableTool,
    WebBehaviorAdapter,
    classical_environment,
    standard_constraints,
    web_case_environment,
)

__all__ = [
    "ClassicalTool",
    "LocalVerifier",
    "UnavailableTool",
    "WebBehaviorAdapter",
    "classical_environment",
    "standard_constraints",
    "web_case_environment",
]
