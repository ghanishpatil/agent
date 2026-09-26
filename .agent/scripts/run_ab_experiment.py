"""Run the knowledge-augmented A/B experiment over the frozen Phase 5 benchmark.

Control arm    : frozen solver + existing .agent_audit advisory memory (the Phase 5 baseline)
Treatment arm  : frozen solver + (.agent_audit copy + projected external writeup knowledge)

Only environment.memory_root differs between arms. Writes docs/knowledge_ab_results.json.

Usage:
    python scripts/run_ab_experiment.py [--store PATH] [--audit PATH]
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = AGENT_ROOT.parent
sys.path.insert(0, str(AGENT_ROOT / "src"))

from ctf_ingest import KnowledgeStore, records_from_store  # noqa: E402
from ctf_experiment.ab_harness import run_ab_experiment  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", default=str(AGENT_ROOT / "knowledge" / "local_writeups"))
    parser.add_argument("--audit", default=str(WORKSPACE_ROOT / ".agent_audit"))
    args = parser.parse_args()

    store = KnowledgeStore(Path(args.store))
    records = records_from_store(store)
    if not records:
        print(f"no ingested records found in {args.store}; run scripts/ingest_writeups.py first")
        return 1
    audit_root = Path(args.audit) if Path(args.audit).is_dir() else None

    with tempfile.TemporaryDirectory(prefix="ab_experiment_") as tmp:
        comparison = run_ab_experiment(records, Path(tmp) / "work", audit_root=audit_root)
        payload = {
            "external_records": len(records),
            "audit_root": str(audit_root) if audit_root else None,
            **comparison.to_dict(),
        }
        out = AGENT_ROOT / "docs" / "knowledge_ab_results.json"
        out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(f"wrote {out}")
    print(f"verdict: {comparison.verdict}")
    print(f"deltas:  {json.dumps(comparison.deltas)}")
    print(f"invariants: {json.dumps(comparison.invariants)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
