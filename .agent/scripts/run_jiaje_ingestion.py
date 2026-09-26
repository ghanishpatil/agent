"""First external CTF knowledge ingestion experiment: Jiajie Chen's (@jiegec) jia.je writeups.

Ingests the cached Jia Jie pages into a SEPARATE versioned store (knowledge/jiaje_v1), validates
ingestion + retrieval independently, compares against the local corpus, and runs the existing
knowledge-dependent evaluation in three configs (local / jiaje / local+jiaje) with efficiency
metrics. Does not mix Jia Jie into the local store and does not connect the full corpus to the
solver beyond this controlled evaluation.

Writes artifacts under docs/. Reruns are idempotent.
"""

from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT / "src"))

from ctf_ingest import CachedHttpSource, IngestionPipeline, KnowledgeStore, records_from_store
from ctf_ingest.retrieval import KnowledgeRetriever, RetrievalQuery
from ctf_experiment.corpus_analysis import (
    compare_corpora,
    corpus_stats,
    cross_corpus_duplicates,
    extraction_quality,
)
from ctf_experiment.retrieval_eval import LabeledQuery, evaluate_retrieval
from ctf_experiment.knowledge_dependent_harness_v2 import run_experiment_v2

CACHE = AGENT_ROOT / "knowledge" / "_jiaje_cache"
JIAJE_STORE = AGENT_ROOT / "knowledge" / "jiaje_v1"
LOCAL_STORE = AGENT_ROOT / "knowledge" / "local_writeups"
DOCS = AGENT_ROOT / "docs"


def _write(name: str, payload) -> Path:
    path = DOCS / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _integrity_manifest(records, store: KnowledgeStore) -> dict:
    return {
        "store": str(JIAJE_STORE),
        "store_manifest": store.read_manifest(),
        "records": [
            {
                "record_id": r.record_id,
                "content_hash": r.content_hash,
                "source_uri": r.provenance.source_uri,
                "retrieved_at": r.provenance.retrieved_at,
                "author": r.provenance.extra.get("author", ""),
                "has_static_content": r.provenance.extra.get("has_static_content", ""),
            }
            for r in records
        ],
    }


def _labeled_queries(records):
    def find(suffix):
        return next((r.record_id for r in records if r.provenance.source_uri.endswith(suffix)), None)

    pyjail = find("pyjail.html")
    solution = find("solution.html")
    queries = []
    if pyjail:
        queries.append(LabeledQuery(
            "pyjail",
            RetrievalQuery(text="python jail escape bypass builtins subclasses pyjail",
                           category="misc", keywords=("pyjail", "jail")),
            relevant_ids=(pyjail,),
        ))
    if solution:
        queries.append(LabeledQuery(
            "crypto-taxonomy",
            RetrievalQuery(text="rsa discrete logarithm aes padding oracle lll lattice technique index",
                           category="misc", keywords=("rsa", "aes")),
            relevant_ids=(solution,),
        ))
    return queries


def main() -> int:
    # 1. Ingest into the separate versioned store.
    store = KnowledgeStore(JIAJE_STORE)
    jiaje_records, ingest_report = IngestionPipeline().run([CachedHttpSource(CACHE)], store)
    local_records = list(records_from_store(KnowledgeStore(LOCAL_STORE)))

    # Raw texts (for explicit-vs-inferred category detection in extraction quality).
    raw_texts = {}
    for r in jiaje_records:
        fp = CACHE / r.provenance.document_path
        if fp.exists():
            raw_texts[r.record_id] = fp.read_text(encoding="utf-8")

    # 2. Statistics + integrity.
    jiaje_stats = corpus_stats(jiaje_records)
    local_stats = corpus_stats(local_records)
    stats_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "documents_seen": ingest_report.documents_seen,
        "records_written": ingest_report.records_written,
        "unique_records": ingest_report.unique_records,
        "intra_run_duplicates": ingest_report.duplicate_records,
        "jiaje_stats": jiaje_stats,
    }
    _write("jiaje_ingestion_statistics.json", stats_payload)
    _write("jiaje_integrity_manifest.json", _integrity_manifest(jiaje_records, store))

    # 3. Cross-corpus duplicate detection (provenance preserved).
    dup = cross_corpus_duplicates(local_records, jiaje_records)
    _write("jiaje_duplicate_report.json", dup)

    # 4. Extraction quality.
    extraction = extraction_quality(jiaje_records, raw_texts)
    _write("jiaje_extraction_quality.json", extraction)

    # 5. Retrieval quality on the new corpus (labeled).
    retriever = KnowledgeRetriever.from_records(jiaje_records)
    labeled = _labeled_queries(jiaje_records)
    retrieval = evaluate_retrieval(retriever, labeled, k=3).to_dict() if labeled else {"note": "no labeled queries"}
    _write("jiaje_retrieval_quality.json", retrieval)

    # 6. Corpus comparison.
    comparison = compare_corpora(local_stats, jiaje_stats)
    _write("jiaje_corpus_comparison.json", {"local_stats": local_stats, "jiaje_stats": jiaje_stats, "comparison": comparison})

    # 7. Three-config knowledge-dependent evaluation (local / jiaje / local+jiaje).
    # Restricted to the two cases with well-defined semantics under a GLOBAL corpus retriever:
    #   - kd2-baseline-solvable : easy/fast check (must stay 0-retrieval regardless of corpus)
    #   - kd2-knowledge-dependent: does the corpus supply the missing mechanism?
    # The adversarial cases (misleading/conflicting/noise) are defined by their own per-case
    # knowledge and are validated in the immutable v2 experiment; re-running them under a global
    # corpus retriever changes their intent, so they are excluded here.
    from ctf_experiment.knowledge_dependent_benchmark_v2 import build_cases_v2

    local_ret = KnowledgeRetriever.from_records(local_records)
    jiaje_ret = KnowledgeRetriever.from_records(jiaje_records)
    combined_ret = KnowledgeRetriever.from_records(local_records + jiaje_records)
    configs = {
        "local": lambda case: local_ret,
        "jiaje": lambda case: jiaje_ret,
        "local_plus_jiaje": lambda case: combined_ret,
    }
    corpus_case_ids = {"kd2-baseline-solvable", "kd2-knowledge-dependent"}
    three_config = {}
    with tempfile.TemporaryDirectory(prefix="jiaje_3cfg_") as tmp:
        for name, factory in configs.items():
            subset = tuple(
                c for c in build_cases_v2(Path(tmp) / name / "bench") if c.case_id in corpus_case_ids
            )
            rep = run_experiment_v2(Path(tmp) / name, cases=subset, retriever_factory=factory).to_dict()
            three_config[name] = {
                "verdict": rep["verdict"],
                "knowledge_attributable_verified_solves": rep["knowledge_attributable_verified_solves"],
                "all_safety_invariants_preserved": rep["all_safety_invariants_preserved"],
                "per_case": {c["case_id"]: {
                    "treatment_status": c["treatment"]["status"],
                    "verified_flag": c["treatment"]["verified_flag"],
                    "retrieval_calls": c["metrics"]["retrieval_calls_per_solve"],
                    "retrieved_records": c["metrics"].get("retrieved_records_per_solve"),
                    "knowledge_hypotheses": c["metrics"]["knowledge_hypotheses_per_solve"],
                    "actions": c["metrics"]["actions_per_solve"],
                    "time_to_first_action_ms": c["metrics"]["time_to_first_action_ms"],
                    "time_to_verified_ms": c["metrics"]["time_to_verified_ms"],
                    "unnecessary_retrievals": c["metrics"]["unnecessary_retrievals"],
                    "knowledge_attributable": c["knowledge_attributable_verified_solve"],
                    "safety_ok": all(c["safety_invariants"].values()),
                } for c in rep["cases"]},
            }
    _write("jiaje_three_config_results.json", three_config)

    print("Jia Jie ingestion + evaluation complete.")
    print(f"jiaje records: {len(jiaje_records)} | local records: {len(local_records)}")
    print(f"cross-corpus duplicates: {dup['duplicate_count']} (rate {dup['duplicate_rate']})")
    if labeled:
        print(f"retrieval P@3={retrieval['mean_precision_at_k']} R@3={retrieval['mean_recall_at_k']} MRR={retrieval['mean_reciprocal_rank']}")
    for name, r in three_config.items():
        print(f"  config {name}: KAVS={r['knowledge_attributable_verified_solves']} safety={r['all_safety_invariants_preserved']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
