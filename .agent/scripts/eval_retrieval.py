"""Independent retrieval-quality evaluation. Writes docs/retrieval_quality.json.

- Labeled precision@k / recall@k / MRR on a controlled synthetic corpus (non-circular).
- Category-consistency@k over the real ingested writeups store (descriptive).

Usage:
    python scripts/eval_retrieval.py [--store PATH] [--k 5]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT / "src"))

from ctf_ingest import KnowledgeStore  # noqa: E402
from ctf_ingest.retrieval import KnowledgeRetriever, RetrievalQuery  # noqa: E402
from ctf_experiment.labeled import synthetic_labeled_corpus  # noqa: E402
from ctf_experiment.retrieval_eval import category_consistency_at_k, evaluate_retrieval  # noqa: E402

REAL_CATEGORIES = ("web", "crypto", "pwn", "reverse", "forensics")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", default=str(AGENT_ROOT / "knowledge" / "local_writeups"))
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()

    records, queries = synthetic_labeled_corpus()
    synthetic_retriever = KnowledgeRetriever.from_records(records)
    labeled = evaluate_retrieval(synthetic_retriever, queries, k=args.k)

    payload = {"labeled_synthetic": labeled.to_dict()}

    store = KnowledgeStore(Path(args.store))
    if any(store.read_all()):
        real_retriever = KnowledgeRetriever.from_store(store)
        cat_queries = [
            RetrievalQuery(text=f"{c} challenge", category=c, keywords=(c,))
            for c in REAL_CATEGORIES
        ]
        payload["real_store_category_consistency"] = category_consistency_at_k(
            real_retriever, cat_queries, k=args.k
        )
        payload["real_store_path"] = str(args.store)

    out = AGENT_ROOT / "docs" / "retrieval_quality.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"wrote {out}")
    print(
        "labeled: P@{k}={p:.3f} R@{k}={r:.3f} MRR={m:.3f}".format(
            k=args.k,
            p=labeled.mean_precision_at_k,
            r=labeled.mean_recall_at_k,
            m=labeled.mean_reciprocal_rank,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
