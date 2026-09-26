"""Frozen benchmark definitions for the Phase 5 autonomous solver.

This package is the single source of truth for the evaluation challenge set. The exact
same challenges are reused for the baseline and for any later baseline-vs-augmented
knowledge experiment. It is additive and is never imported by ``ctf_agent``.
"""

from .phase5_benchmark import (
    PHASE5_MANIFEST,
    BenchmarkCaseSpec,
    build_crypto_package,
    build_phase5_cases,
    classical_environment,
    standard_constraints,
    web_case_environment,
)

__all__ = [
    "PHASE5_MANIFEST",
    "BenchmarkCaseSpec",
    "build_crypto_package",
    "build_phase5_cases",
    "classical_environment",
    "standard_constraints",
    "web_case_environment",
]
