"""Run the knowledge-dependent + adversarial-knowledge experiment.

Writes docs/knowledge_dependent_results.json. Varies only knowledge availability between
control and treatment; the frozen solver, benchmark env, tools, and budgets are identical.

Usage:
    python scripts/run_knowledge_dependent.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT / "src"))

from ctf_experiment.knowledge_dependent_harness import run_knowledge_dependent_experiment  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="kd_experiment_") as tmp:
        report = run_knowledge_dependent_experiment(Path(tmp) / "work")
        payload = report.to_dict()
        out = AGENT_ROOT / "docs" / "knowledge_dependent_results.json"
        out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(f"wrote {out}")
    print(f"verdict: {report.verdict()}")
    print(
        f"knowledge_attributable_verified_solves="
        f"{report.knowledge_attributable_verified_solves} "
        f"safety_all_preserved={report.all_safety_invariants_preserved}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
