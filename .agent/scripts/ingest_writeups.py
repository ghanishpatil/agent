"""Run the ingestion pipeline over a local writeups corpus (read-only input).

By default it ingests the workspace ``writeups/`` tree (a protected, read-only corpus)
into ``.agent/knowledge/local_writeups/``. The input tree is never modified.

Usage:
    python scripts/ingest_writeups.py [--source PATH] [--store PATH] [--near 0.9]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = AGENT_ROOT.parent
sys.path.insert(0, str(AGENT_ROOT / "src"))

from ctf_ingest import IngestionPipeline, KnowledgeStore, LocalDirectorySource  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(WORKSPACE_ROOT / "writeups"))
    parser.add_argument("--store", default=str(AGENT_ROOT / "knowledge" / "local_writeups"))
    parser.add_argument("--near", type=float, default=0.9)
    parser.add_argument(
        "--license",
        default="local workspace writeups corpus (read-only input)",
    )
    args = parser.parse_args()

    source_root = Path(args.source)
    if not source_root.is_dir():
        print(f"source directory not found: {source_root}")
        return 1

    store = KnowledgeStore(Path(args.store))
    source = LocalDirectorySource(source_root, license_note=args.license)
    _records, report = IngestionPipeline(near_threshold=args.near).run([source], store)

    print(f"source:  {source_root}")
    print(f"store:   {args.store}")
    print(
        f"documents_seen={report.documents_seen} "
        f"records_written={report.records_written} "
        f"unique={report.unique_records} duplicates={report.duplicate_records}"
    )
    print("manifest:")
    print(json.dumps(report.manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
