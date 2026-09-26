"""Generate the reproducible Phase 5 clean-baseline manifest.

This script composes the exact labeled KNOWN/NOVEL/ADVERSARIAL/HELD_OUT evaluation
cases from the frozen ``ctf_bench.phase5_benchmark`` (the single source of truth shared
with the tests), runs the real ``EvaluationHarness`` against the deterministic
specialist brain, and writes ``docs/phase5_baseline.json``.

It provides no action or hypothesis sequence to the solver; the solver decides.

Usage:
    python scripts/generate_phase5_baseline.py [--test-count N] [--historical TEXT]
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = AGENT_ROOT.parent
sys.path.insert(0, str(AGENT_ROOT / "src"))

import json  # noqa: E402
from collections import defaultdict  # noqa: E402

from ctf_agent.autonomy.baseline import write_baseline  # noqa: E402
from ctf_agent.autonomy.contracts import SolveStatus  # noqa: E402
from ctf_agent.autonomy.evaluation import EvaluationHarness, EvaluationReport  # noqa: E402

from ctf_bench.phase5_benchmark import build_phase5_cases  # noqa: E402

PROTECTED_TREES = (".agent_audit", ".kiro", "writeups")


def _per_kind_breakdown(report: EvaluationReport) -> dict:
    by_kind: dict[str, list] = defaultdict(list)
    for item in report.cases:
        by_kind[item.kind.value].append(item)
    breakdown = {}
    for kind, items in sorted(by_kind.items()):
        solved = [i for i in items if i.result.status is SolveStatus.SOLVED]
        verified = [
            i for i in solved if i.result.verified_flag and i.result.verification_evidence_ids
        ]
        breakdown[kind] = {
            "cases": len(items),
            "solved": len(solved),
            "solve_rate": len(solved) / len(items) if items else 0.0,
            "verified_solve_rate": len(verified) / len(items) if items else 0.0,
            "case_ids": [i.case_id for i in items],
        }
    return breakdown


def _write_results(path: Path, report: EvaluationReport) -> Path:
    """Write the focused Phase 5 results artifact (the numbers, incl. held-out breakdown)."""
    m = report.metrics
    payload = {
        "case_count": m.case_count,
        "headline": {
            "verified_solve_rate": m.verified_solve_rate,
            "solve_rate": m.solve_rate,
            "false_verification_rate": m.false_verification_rate,
            "false_disproof_rate": m.false_disproof_rate,
            "average_actions_per_solve": m.average_actions_per_solve,
            "median_actions_per_solve": m.median_actions_per_solve,
            "duplicate_action_rate": m.duplicate_action_rate,
            "blind_retry_rate": m.blind_retry_rate,
            "dead_end_recovery_rate": m.dead_end_recovery_rate,
            "environmental_failure_recovery_rate": m.environmental_failure_recovery_rate,
            "tool_failure_recovery_rate": m.tool_failure_recovery_rate,
            "specialist_selection_accuracy": m.specialist_selection_accuracy,
            "useful_specialist_proposal_rate": m.useful_specialist_proposal_rate,
            "candidate_verification_success": m.candidate_verification_success,
            "stop_correctness": m.stop_correctness,
            "budget_violations": m.budget_violations,
            "terminal_state_correctness": m.terminal_state_correctness,
        },
        "per_kind": _per_kind_breakdown(report),
        "per_case": [
            {
                "case_id": i.case_id,
                "kind": i.kind.value,
                "status": i.result.status.value,
                "verified_flag": i.result.verified_flag,
                "status_correct": i.status_correct,
                "flag_correct": i.flag_correct,
                "actions": len(i.result.actions),
                "failures": list(i.failures),
            }
            for i in report.cases
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _protected_integrity() -> dict[str, str]:
    integrity: dict[str, str] = {}
    for name in PROTECTED_TREES:
        root = WORKSPACE_ROOT / name
        if not root.is_dir():
            integrity[name] = "MISSING"
            continue
        digest = hashlib.sha256()
        files = sorted(p for p in root.rglob("*") if p.is_file())
        for path in files:
            digest.update(str(path.relative_to(root)).replace("\\", "/").encode("utf-8"))
            digest.update(hashlib.sha256(path.read_bytes()).digest())
        integrity[name] = f"sha256:{digest.hexdigest()};files={len(files)}"
    return integrity


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-count", type=int, default=264)
    parser.add_argument("--historical", default="12/12 pass")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        cases, _ = build_phase5_cases(tmp_path)
        report = EvaluationHarness().run(cases)

        tool_names = sorted(
            {
                tool.name
                for case in cases
                for tool in case.environment_factory().permitted_tools
            }
        )
        out = write_baseline(
            AGENT_ROOT / "docs" / "phase5_baseline.json",
            report=report,
            test_count=args.test_count,
            historical_regressions=args.historical,
            available_tools=tool_names,
            model_configuration="deterministic specialist brain; no external LLM configured",
            memory_root=WORKSPACE_ROOT / ".agent_audit",
            protected_integrity=_protected_integrity(),
        )

        results_out = _write_results(AGENT_ROOT / "docs" / "phase5_results.json", report)

    print(f"wrote {out}")
    print(f"wrote {results_out}")
    m = report.metrics
    print(f"cases={m.case_count} solve_rate={m.solve_rate:.3f} "
          f"verified_solve_rate={m.verified_solve_rate:.3f} "
          f"false_verification={m.false_verification_rate:.3f} "
          f"false_disproof={m.false_disproof_rate} "
          f"duplicate_action_rate={m.duplicate_action_rate:.3f} "
          f"avg_actions={m.average_actions_per_solve:.3f} "
          f"stop_correctness={m.stop_correctness:.3f} "
          f"budget_violations={m.budget_violations}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
