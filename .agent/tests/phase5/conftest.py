from __future__ import annotations

from pathlib import Path

import pytest

from ctf_bench.phase5_benchmark import build_crypto_package


@pytest.fixture
def crypto_package(tmp_path: Path):
    """Deterministic crypto challenge package from the frozen benchmark."""
    return build_crypto_package(tmp_path / "crypto")
