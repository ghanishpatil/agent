"""Run the knowledge-integration A/B experiment (v2) and write artifacts.

Produces:
  docs/knowledge_dependent_results_v2.json  (A/B outcomes + per-case metrics)
  docs/knowledge_integration_performance.json (aggregate performance table)

Does NOT overwrite docs/knowledge_dependent_results.json (the v1 KNOWLEDGE-SAFE result).

Usage:
    python scripts/run_knowledge_integration.py
"""

from __future__ import annotations

import json
import statistics
import sys
import tempfile
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT / "src"))

from ctf_experiment.knowledge_dependent_harness_v2 import run_experiment_v2  # noqa: E402


def _aggregate(cases) -> dict:
    def vals(key):
        return [c["metrics"][key] for c in cases if c["metrics"].get(key) is not None]

    solved = [c for c in cases if c["treatment"]["status"] == "SOLVED"]
    verified_times = [c["metrics"]["time_to_verified_ms"] for c in solved if c["metrics"]["time_to_verified_ms"] is not None]
    first_action = vals("time_to_first_action_ms")
    return {
        "mean_time_to_first_action_ms": round(statistics.mean(first_action), 3) if first_action else None,
        "mean_time_to_verified_ms": round(statistics.mean(verified_times), 3) if verified_times else None,
        "mean_actions_per_solve": round(statistics.mean(vals("actions_per_solve")), 3),
        "total_retrieval_calls": sum(vals("retrieval_calls_per_solve")),
        "total_knowledge_hypotheses": sum(vals("knowledge_hypotheses_per_solve")),
        "total_unnecessary_retrievals": sum(vals("unnecessary_retrievals")),
        "total_duplicate_actions": sum(vals("duplicate_actions")),
        "total_budget_violations": sum(vals("budget_violations")),
        "false_verifications": sum(1 for c in cases if c["metrics"]["false_verification"]),
        "false_disproofs": sum(1 for c in cases if c["metrics"]["false_disproof"]),
        "stopping_correct_cases": sum(1 for c in cases if c["metrics"]["stopping_correct"]),
        "fast_path_cases_zero_retrieval": sum(
            1 for c in cases if c["metrics"]["retrieval_calls_per_solve"] == 0
        ),
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="kd_v2_") as tmp:
        report = run_experiment_v2(Path(tmp) / "work")
        d = report.to_dict()

        results_out = AGENT_ROOT / "docs" / "knowledge_dependent_results_v2.json"
        results_out.write_text(json.dumps(d, indent=2, sort_keys=True), encoding="utf-8")

        perf = {
            "verdict": d["verdict"],
            "knowledge_attributable_verified_solves": d["knowledge_attributable_verified_solves"],
            "all_safety_invariants_preserved": d["all_safety_invariants_preserved"],
            "aggregate": _aggregate(d["cases"]),
            "per_case_metrics": {c["case_id"]: c["metrics"] for c in d["cases"]},
        }
        perf_out = AGENT_ROOT / "docs" / "knowledge_integration_performance.json"
        perf_out.write_text(json.dumps(perf, indent=2, sort_keys=True), encoding="utf-8")

    print(f"wrote {results_out}")
    print(f"wrote {perf_out}")
    print(f"verdict: {report.verdict()}")
    print(f"KAVS={report.knowledge_attributable_verified_solves} "
          f"safety_all={report.all_safety_preserved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
