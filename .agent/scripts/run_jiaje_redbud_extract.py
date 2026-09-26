"""Extract + ingest the 22 Redbud writeups into knowledge/jiaje_redbud_v1/ (no solver, no retrieval).

Reuses ctf_ingest (models, normalize, technique table, KnowledgeStore, Deduplicator) via the new
redbud_extract layer. Raw source stays immutable. Produces extraction/quality/dedup artifacts with
per-document statistics. Does NOT connect to the solver, run the benchmark, or fine-tune.
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT / "src"))

from ctf_ingest import KnowledgeStore, records_from_store
from ctf_ingest.redbud_extract import EXTRACTION_VERSION, build_extraction
from ctf_ingest.models import TRAJECTORY_ORDER
from ctf_experiment.corpus_analysis import corpus_stats, cross_corpus_duplicates

NS = AGENT_ROOT / "knowledge" / "jiaje_redbud_v1"
RAW = NS / "raw"
STORE_DIR = NS / "store"
FETCH_MANIFEST = AGENT_ROOT / "docs" / "jiaje_redbud_fetch_manifest.json"
LOCAL_STORE = AGENT_ROOT / "knowledge" / "local_writeups"
JIAJE_V1 = AGENT_ROOT / "knowledge" / "jiaje_v1"
DOCS = AGENT_ROOT / "docs"


def _write(name: str, payload) -> Path:
    p = DOCS / name
    p.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return p


def main() -> int:
    fetch = json.loads(FETCH_MANIFEST.read_text(encoding="utf-8"))
    fetch_records = fetch["records"]
    if len(fetch_records) != 22:
        print(f"ABORT: expected 22 fetched records, found {len(fetch_records)}")
        return 3

    extractions = []
    for rec in fetch_records:
        html_path = Path(rec["html_artifact"])
        if not html_path.exists():
            print(f"ABORT: missing raw artifact {html_path}")
            return 3
        html = html_path.read_text(encoding="utf-8")
        rel = str(html_path.relative_to(AGENT_ROOT)).replace("\\", "/")
        ex = build_extraction(
            html,
            source_url=rec["source_url"],
            raw_artifact_relpath=rel,
            content_sha256=rec["content_sha256"],
            event=rec["event"],
            challenge_id=rec["challenge_id"],
            author=rec.get("provenance", {}).get("author", "Jiajie Chen (@jiegec)"),
            retrieved_at=rec["retrieved_at"],
        )
        extractions.append(ex)

    records = [ex.record for ex in extractions]

    # -- persist: KnowledgeStore (reused) + extractions.jsonl (records + field provenance) -------
    store = KnowledgeStore(STORE_DIR)
    store_manifest = store.write(records)
    (NS / "extractions.jsonl").write_text(
        "\n".join(json.dumps(ex.to_dict(), sort_keys=True) for ex in extractions) + "\n", encoding="utf-8"
    )

    # -- deduplication: internal + cross-corpus (local, jiaje_v1); provenance preserved ----------
    local_records = list(records_from_store(KnowledgeStore(LOCAL_STORE)))
    jiaje_v1_records = list(records_from_store(KnowledgeStore(JIAJE_V1)))
    internal = cross_corpus_duplicates(records, records)  # self: detects intra-corpus repeats
    # self-compare counts each record as duplicate of an earlier identical one; recompute cleanly:
    internal_dupes = _internal_duplicates(records)
    vs_local = cross_corpus_duplicates(local_records, records)
    vs_jiaje = cross_corpus_duplicates(jiaje_v1_records, records)
    duplicate_report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": "duplicates are reported and provenance-preserved; none are discarded",
        "internal_redbud": internal_dupes,
        "vs_local_writeups": {"local_records": vs_local["local_records"], "duplicate_count": vs_local["duplicate_count"], "duplicate_rate": vs_local["duplicate_rate"], "matches": vs_local["duplicate_matches"]},
        "vs_jiaje_v1": {"jiaje_v1_records": vs_jiaje["local_records"], "duplicate_count": vs_jiaje["duplicate_count"], "duplicate_rate": vs_jiaje["duplicate_rate"], "matches": vs_jiaje["duplicate_matches"]},
    }
    _write("jiaje_redbud_duplicate_report.json", duplicate_report)

    # -- corpus + per-document statistics --------------------------------------------------------
    stats = corpus_stats(records)
    per_doc = []
    for ex in extractions:
        r = ex.record
        present = sorted(k.value for k in {s.kind for s in r.trajectory.steps})
        per_doc.append({
            "record_id": r.record_id,
            "event": r.metadata.event,
            "challenge": r.metadata.name,
            "category": r.metadata.category,
            "difficulty": r.metadata.difficulty or None,
            "source_url": r.provenance.source_uri,
            "techniques": [t.technique_id for t in r.techniques],
            "technique_count": len(r.techniques),
            "trajectory_stages_present": present,
            "trajectory_completeness": r.trajectory.completeness,
            "genuine_trajectory": ex.genuine_trajectory,
            "failure_corrections": len(r.failures),
            "flags_present": len(r.metadata.flags),
            "field_provenance": ex.field_provenance,
        })

    completeness = [r.trajectory.completeness for r in records]
    genuine = sum(1 for ex in extractions if ex.genuine_trajectory)
    stage_presence = Counter()
    for r in records:
        for k in {s.kind for s in r.trajectory.steps}:
            stage_presence[k.value] += 1

    extraction_stats = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "extraction_version": EXTRACTION_VERSION,
        "documents": len(records),
        "corpus": stats,
        "trajectory": {
            "mean_completeness": round(statistics.mean(completeness), 4),
            "median_completeness": round(statistics.median(completeness), 4),
            "min_completeness": round(min(completeness), 4),
            "max_completeness": round(max(completeness), 4),
            "genuine_trajectories": genuine,
            "genuine_trajectory_rate": round(genuine / len(records), 4),
            "stage_presence_counts": dict(sorted(stage_presence.items())),
            "stage_order": [k.value for k in TRAJECTORY_ORDER],
        },
        "technique_coverage": stats["technique_coverage"],
        "distinct_techniques": stats["distinct_techniques"],
        "category_distribution": stats["categories"],
        "failure_correction_coverage": stats["failure_correction_coverage"],
        "provenance_completeness": stats["provenance_completeness"],
        "store_manifest": store_manifest,
        "per_document": per_doc,
    }
    _write("jiaje_redbud_extraction_statistics.json", extraction_stats)

    # -- extraction-quality report: per-field E/I/M, per-document + aggregate --------------------
    field_summary: Dict[str, Counter] = {}
    for ex in extractions:
        for fld, verdict in ex.field_provenance.items():
            field_summary.setdefault(fld, Counter())[verdict] += 1
    quality = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "note": "reasoning stages are EXPLICIT only when a section heading denotes them; never inferred/fabricated",
        "field_summary_explicit_inferred_missing": {f: dict(c) for f, c in sorted(field_summary.items())},
        "per_document": [{"challenge": d["challenge"], "event": d["event"], "field_provenance": d["field_provenance"], "genuine_trajectory": d["genuine_trajectory"], "trajectory_completeness": d["trajectory_completeness"]} for d in per_doc],
    }
    _write("jiaje_redbud_extraction_quality.json", quality)

    _write_report(extraction_stats, duplicate_report, per_doc)

    print(f"Redbud extraction complete: {len(records)} records → {STORE_DIR}")
    print(f"  mean trajectory completeness: {extraction_stats['trajectory']['mean_completeness']} "
          f"(genuine trajectories: {genuine}/{len(records)})")
    print(f"  distinct techniques: {stats['distinct_techniques']} · categories: {stats['categories']}")
    print(f"  failure/correction coverage: {stats['failure_correction_coverage']} · provenance: {stats['provenance_completeness']}")
    print(f"  dupes: internal={internal_dupes['duplicate_count']} vs_local={vs_local['duplicate_count']} vs_jiaje_v1={vs_jiaje['duplicate_count']}")
    return 0


def _internal_duplicates(records):
    from ctf_ingest.dedup import Deduplicator

    dedup = Deduplicator(near_threshold=0.9)
    matches = []
    for r in records:
        d = dedup.evaluate(r.record_id, r.content_hash, f"{r.title} {r.summary}")
        if d.is_duplicate:
            matches.append({"record_id": r.record_id, "duplicate_of": d.duplicate_of, "similarity": d.similarity, "reason": d.reason})
        dedup.accept(r.record_id, r.content_hash, f"{r.title} {r.summary}")
    return {"records": len(records), "duplicate_count": len(matches), "matches": matches}


def _write_report(stats, dup, per_doc) -> None:
    t = stats["trajectory"]
    lines = [
        "# Jia Jie Redbud Extraction Report", "",
        f"Generated: {stats['generated_at']} · extraction: {stats['extraction_version']}", "",
        "Extracted the 22 frozen Redbud raw writeups into `knowledge/jiaje_redbud_v1/` by extending "
        "ctf_ingest (reused models/normalize/technique-table/store/dedup). Raw source is immutable. "
        "Not connected to the solver; benchmark not run; nothing fine-tuned. Reasoning stages are "
        "recorded EXPLICIT only when a section heading denotes them — never fabricated.", "",
        "## Answer: how much genuine reusable reasoning knowledge?", "",
        f"- documents: {stats['documents']}",
        f"- distinct techniques: {stats['distinct_techniques']}",
        f"- category distribution: {stats['category_distribution']}",
        f"- mean trajectory completeness: {t['mean_completeness']} (median {t['median_completeness']}, "
        f"min {t['min_completeness']}, max {t['max_completeness']})",
        f"- **genuine reasoning trajectories** (description→analysis/approach→solution/verification): "
        f"{t['genuine_trajectories']}/{stats['documents']} ({t['genuine_trajectory_rate']})",
        f"- failure/correction coverage: {stats['failure_correction_coverage']}",
        f"- provenance completeness: {stats['provenance_completeness']}",
        f"- duplicates: internal={dup['internal_redbud']['duplicate_count']}, "
        f"vs local={dup['vs_local_writeups']['duplicate_count']}, vs jiaje_v1={dup['vs_jiaje_v1']['duplicate_count']}",
        "",
        "### Trajectory stage presence (of 22 documents)", "",
        "| stage | docs with stage |", "|---|---|",
    ]
    for stage in t["stage_order"]:
        lines.append(f"| {stage} | {t['stage_presence_counts'].get(stage, 0)} |")
    lines += ["", "## Per-document statistics (no averaging hides weak extraction)", "",
              "| event | challenge | cat | tech | stages | complete | genuine | fails | flags |",
              "|---|---|---|---|---|---|---|---|---|"]
    for d in per_doc:
        lines.append(
            f"| {d['event']} | {d['challenge']} | {d['category'] or '-'} | {d['technique_count']} | "
            f"{len(d['trajectory_stages_present'])} | {d['trajectory_completeness']} | "
            f"{'yes' if d['genuine_trajectory'] else 'no'} | {d['failure_corrections']} | {d['flags_present']} |"
        )
    lines += ["", "## Interpretation", "",
              "These are solution-oriented expert writeups: most contain description → analysis/approach "
              "→ solution (+ often a final flag), which yields moderate trajectory completeness. They are "
              "largely NOT full hypothesize→test→observe→update narratives, and explicit "
              "failure/correction sequences are rare — so the reusable knowledge is strongest as "
              "technique + challenge-pattern + solution knowledge, and weaker as step-by-step reasoning "
              "trajectories. Values above are measured from section headings, not inferred.", ""]
    (DOCS / "jiaje_redbud_extraction_report.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
