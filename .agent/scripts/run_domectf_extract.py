"""Extract + ingest the verified DomeCTF individual writeups into knowledge/domectf_v1/.

Source of truth: the FROZEN discovery corpus knowledge/domectf_sources_v1/ (read-only). Only
sources that are ACCESSIBLE and classified A_INDIVIDUAL_WRITEUP (declared type INDIVIDUAL/GITHUB/
MEDIUM/BLOG) are extracted — official/index/404/blocked/redirected sources are skipped and the
reasons are recorded. Reuses ctf_ingest (models, normalize, technique table, KnowledgeStore,
Deduplicator) via the additive domectf_extract layer.

Does NOT connect to the solver/retrieval/planner/specialists/Phase 5, does NOT run a benchmark,
does NOT fine-tune, and does NOT modify any frozen artifact. Re-runs are idempotent.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT / "src"))

from ctf_ingest import KnowledgeStore, records_from_store  # noqa: E402
from ctf_ingest.domectf_extract import EXTRACTION_VERSION, build_extraction, canonical_link  # noqa: E402
from ctf_ingest.models import TRAJECTORY_ORDER  # noqa: E402
from ctf_experiment.corpus_analysis import corpus_stats, cross_corpus_duplicates  # noqa: E402

SRC_NS = AGENT_ROOT / "knowledge" / "domectf_sources_v1"
NS = AGENT_ROOT / "knowledge" / "domectf_v1"
STORE_DIR = NS / "store"
DOCS = NS / "docs"
RAW_REFS = NS / "raw_refs"
REPORTS = NS / "reports"
MANIFESTS = NS / "manifests"

LOCAL_STORE = AGENT_ROOT / "knowledge" / "local_writeups"
JIAJE_V1 = AGENT_ROOT / "knowledge" / "jiaje_v1"
JIAJE_REDBUD = AGENT_ROOT / "knowledge" / "jiaje_redbud_v1" / "store"

INDIV_TYPES = {"INDIVIDUAL_WRITEUP", "GITHUB_WRITEUP", "MEDIUM_WRITEUP", "BLOG_WRITEUP"}


def _write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _load_sources():
    verif = json.loads((SRC_NS / "reports/domectf_source_verification.json").read_text(encoding="utf-8"))
    disc = json.loads((SRC_NS / "reports/domectf_discovered_sources.json").read_text(encoding="utf-8"))
    inv = json.loads((SRC_NS / "reports/domectf_source_inventory.json").read_text(encoding="utf-8"))
    man = json.loads((SRC_NS / "manifests/domectf_source_manifest.json").read_text(encoding="utf-8"))
    return verif, disc, inv, man


def _select_sources(verif, disc, inv, man):
    """Return (selected, skipped). Each selected item carries everything build_extraction needs."""
    raw_by_url = {e["source_url"]: e for e in man["entries"]}
    ref_by_url = {r["url"]: r for r in inv["references"]}
    ref_by_id = {r["ref_id"]: r for r in inv["references"]}

    selected, skipped = [], []

    # Explicit references, individual-type + accessible + classified individual.
    for v in verif["results"]:
        indiv = v["declared_source_type"] in INDIV_TYPES
        ok = v["accessibility"] == "ACCESSIBLE" and v["content_classification"] == "A_INDIVIDUAL_WRITEUP"
        if not (indiv and ok):
            if indiv:  # an individual-type source we could not use — record why
                skipped.append({"url": v["url"], "reason": v["accessibility"],
                                "classification": v["content_classification"], "origin": "explicit"})
            continue
        ref = ref_by_url.get(v["url"], {})
        rawe = raw_by_url.get(v["url"], {})
        selected.append({
            "source_url": v["url"], "final_url": v["final_url"], "raw_artifact": rawe.get("raw_artifact", ""),
            "content_sha256": v["content_sha256"], "event": ref.get("event", ""), "year": ref.get("year"),
            "challenge_id": (ref.get("challenge_name") or "").strip() or v["url"].rsplit("/", 1)[-1],
            "reference_author": ref.get("source_author") or "", "reference_challenge_name": ref.get("challenge_name") or "",
            "source_origin": "explicit_reference",
        })

    # Discovered new individual writeups, accessible + classified individual. Year/event from the
    # originating index reference (deterministic), NOT from the URL path.
    for d in disc["discovered"]:
        if d["already_in_explicit_references"]:
            continue
        ver = d.get("verification") or {}
        if not (ver.get("accessibility") == "ACCESSIBLE" and ver.get("content_classification") == "A_INDIVIDUAL_WRITEUP"):
            continue
        origin_ref = ref_by_id.get(d["originating_ref_id"], {})
        durl = d["discovered_url"]
        rawe = raw_by_url.get(durl, {})
        selected.append({
            "source_url": durl, "final_url": ver.get("final_url", durl), "raw_artifact": rawe.get("raw_artifact", ""),
            "content_sha256": ver.get("content_sha256", ""), "event": origin_ref.get("event", ""),
            "year": origin_ref.get("year"),
            "challenge_id": durl.rsplit("/", 1)[-1].replace("-writeup.html", ""),
            "reference_author": "", "reference_challenge_name": "",  # taken from page title/meta
            "source_origin": "discovered_from_explicit_source",
        })
    return selected, skipped


def main() -> int:
    if not SRC_NS.exists():
        print(f"ABORT: source discovery corpus not found at {SRC_NS}")
        return 3
    for d in (STORE_DIR, DOCS, RAW_REFS, REPORTS, MANIFESTS):
        d.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()

    verif, disc, inv, man = _load_sources()
    selected, skipped = _select_sources(verif, disc, inv, man)

    extractions = []
    per_doc = []
    for s in selected:
        raw_path = AGENT_ROOT / s["raw_artifact"] if s["raw_artifact"] else None
        if not raw_path or not raw_path.exists():
            skipped.append({"url": s["source_url"], "reason": "raw artifact missing", "origin": s["source_origin"]})
            continue
        html = raw_path.read_bytes().decode("utf-8", "replace")
        ext = build_extraction(
            html,
            source_url=s["source_url"],
            canonical_url=canonical_link(html) or s["final_url"],
            raw_artifact_relpath=s["raw_artifact"],
            content_sha256=s["content_sha256"],
            event=s["event"],
            year=s["year"],
            challenge_id=s["challenge_id"],
            reference_author=s["reference_author"],
            reference_challenge_name=s["reference_challenge_name"],
            source_origin=s["source_origin"],
            retrieved_at=generated_at,
        )
        extractions.append(ext)
        r = ext.record
        stages = [k.value for k in TRAJECTORY_ORDER if any(st.kind is k for st in r.trajectory.steps)]
        per_doc.append({
            "record_id": r.record_id, "challenge": r.metadata.name, "year": s["year"], "event": s["event"],
            "category": r.metadata.category, "difficulty": r.metadata.difficulty,
            "source_url": s["source_url"], "canonical_url": r.provenance.extra.get("canonical_url", ""),
            "source_origin": s["source_origin"], "author": r.provenance.extra.get("author", ""),
            "technique_count": len(r.techniques), "techniques": [t.technique_id for t in r.techniques],
            "tools_present": ext.field_provenance.get("commands_tools") == "explicit",
            "flags_present": len(r.metadata.flags), "failure_corrections": len(r.failures),
            "trajectory_completeness": r.trajectory.completeness, "trajectory_stages_present": stages,
            "genuine_trajectory": ext.genuine_trajectory, "field_provenance": ext.field_provenance,
        })

    records = [e.record for e in extractions]

    # -- persist: KnowledgeStore (reused) + per-doc extraction artifacts + sidecar --------------
    store = KnowledgeStore(STORE_DIR)
    store_manifest = store.write(records)
    (NS / "extractions.jsonl").write_text(
        "\n".join(json.dumps(e.to_dict(), sort_keys=True) for e in extractions) + "\n", encoding="utf-8")
    for e in extractions:
        _write(DOCS / f"{e.record.record_id}.json", e.to_dict())

    # -- deduplication: internal + cross-corpus (local, jiaje_v1, jiaje_redbud) -----------------
    def load(store_dir):
        try:
            return list(records_from_store(KnowledgeStore(store_dir)))
        except Exception:
            return []

    local_records = load(LOCAL_STORE)
    jiaje_records = load(JIAJE_V1)
    redbud_records = load(JIAJE_REDBUD)

    internal_raw = cross_corpus_duplicates(records, records)
    # A self-comparison flags every record as an exact duplicate of itself; keep only genuine
    # intra-corpus duplicates (a record matching a DIFFERENT record).
    internal_dupes = [m for m in internal_raw.get("duplicate_matches", [])
                      if m.get("new_record_id") != m.get("duplicate_of")]
    vs_local = cross_corpus_duplicates(local_records, records)
    vs_jiaje = cross_corpus_duplicates(jiaje_records, records)
    vs_redbud = cross_corpus_duplicates(redbud_records, records)

    duplicate_report = {
        "generated_at": generated_at,
        "policy": "duplicates are reported with provenance preserved; distinct challenges are never merged even when techniques/templates are similar",
        "internal_domectf": {"records": len(records), "near_duplicate_count": len(internal_dupes), "matches": internal_dupes},
        "vs_local_writeups": {"other_records": vs_local["local_records"], "duplicate_count": vs_local["duplicate_count"], "matches": vs_local["duplicate_matches"]},
        "vs_jiaje_v1": {"other_records": vs_jiaje["local_records"], "duplicate_count": vs_jiaje["duplicate_count"], "matches": vs_jiaje["duplicate_matches"]},
        "vs_jiaje_redbud_v1": {"other_records": vs_redbud["local_records"], "duplicate_count": vs_redbud["duplicate_count"], "matches": vs_redbud["duplicate_matches"]},
    }
    _write(REPORTS / "domectf_duplicate_report.json", duplicate_report)

    # -- statistics -----------------------------------------------------------------------------
    stats = corpus_stats(records)
    by_year = Counter(str(d["year"]) for d in per_doc)
    by_cat = Counter(d["category"] or "(uninferred)" for d in per_doc)
    genuine = sum(1 for d in per_doc if d["genuine_trajectory"])
    with_failures = sum(1 for d in per_doc if d["failure_corrections"] > 0)
    with_verification = sum(1 for d in per_doc if "VERIFICATION" in d["trajectory_stages_present"])
    tool_docs = sum(1 for d in per_doc if d["tools_present"])
    completeness_vals = [d["trajectory_completeness"] for d in per_doc] or [0.0]

    per_year_breakdown = {}
    for y in ("2019", "2020", "2021"):
        yd = [d for d in per_doc if str(d["year"]) == y]
        per_year_breakdown[y] = {
            "records": len(yd),
            "categories": dict(Counter(d["category"] or "(uninferred)" for d in yd)),
            "genuine_trajectories": sum(1 for d in yd if d["genuine_trajectory"]),
            "with_failures": sum(1 for d in yd if d["failure_corrections"] > 0),
            "with_verification": sum(1 for d in yd if "VERIFICATION" in d["trajectory_stages_present"]),
            "mean_trajectory_completeness": round(sum(d["trajectory_completeness"] for d in yd) / len(yd), 4) if yd else 0.0,
        }

    extraction_stats = {
        "generated_at": generated_at,
        "extraction_version": EXTRACTION_VERSION,
        "sources_selected": len(selected),
        "records_written": len(records),
        "skipped": skipped,
        "store_manifest": store_manifest,
        "category_distribution": dict(by_cat),
        "year_distribution": dict(by_year),
        "per_year_breakdown": per_year_breakdown,
        "technique_coverage": stats.get("technique_coverage", {}),
        "distinct_techniques": stats.get("distinct_techniques", 0),
        "tool_coverage_documents": tool_docs,
        "trajectory": {
            "mean_completeness": round(sum(completeness_vals) / len(completeness_vals), 4),
            "genuine_reasoning_chains": genuine,
            "with_verification": with_verification,
        },
        "failure_correction_coverage": round(with_failures / len(records), 4) if records else 0.0,
        "provenance_completeness": stats.get("provenance_completeness", 0.0),
        "per_document": per_doc,
    }
    _write(REPORTS / "domectf_extraction_statistics.json", extraction_stats)

    # -- quality (per-field E/I/M) --------------------------------------------------------------
    field_summary = defaultdict(lambda: Counter())
    for d in per_doc:
        for fld, verdict in d["field_provenance"].items():
            field_summary[fld][verdict] += 1
    quality = {
        "generated_at": generated_at,
        "note": "reasoning stages are EXPLICIT only when a heading (or concrete artifact for solution/verification) denotes them; never inferred/fabricated",
        "field_summary_explicit_inferred_missing": {k: dict(v) for k, v in field_summary.items()},
        "solution_knowledge": {
            "documents_with_solution_mechanism": sum(1 for d in per_doc if d["field_provenance"].get("solution_mechanism") == "explicit"),
            "documents_with_techniques": sum(1 for d in per_doc if d["field_provenance"].get("techniques_mechanisms") == "explicit"),
            "documents_with_tools": tool_docs,
        },
        "reasoning_knowledge": {
            "genuine_reasoning_chains": genuine,
            "documents_with_any_reasoning_stage": sum(1 for d in per_doc if any(
                s in d["trajectory_stages_present"] for s in ("HYPOTHESIS", "INTERPRETATION", "OBSERVED_CLUE",
                "DISCRIMINATING_TEST", "OBSERVATION", "HYPOTHESIS_UPDATE", "NEXT_ACTION"))),
            "mean_trajectory_completeness": round(sum(completeness_vals) / len(completeness_vals), 4),
        },
        "failure_knowledge": {"documents_with_failure_correction": with_failures},
        "verification_knowledge": {"documents_with_verification": with_verification},
        "per_document": [{"challenge": d["challenge"], "year": d["year"], "category": d["category"],
                          "genuine_trajectory": d["genuine_trajectory"],
                          "trajectory_completeness": d["trajectory_completeness"],
                          "field_provenance": d["field_provenance"]} for d in per_doc],
    }
    _write(REPORTS / "domectf_extraction_quality.json", quality)

    # -- provenance / integrity manifest --------------------------------------------------------
    _write(MANIFESTS / "domectf_provenance_manifest.json", {
        "generated_at": generated_at,
        "extraction_version": EXTRACTION_VERSION,
        "source_corpus": str(SRC_NS.relative_to(AGENT_ROOT)),
        "store": str(STORE_DIR.relative_to(AGENT_ROOT)),
        "store_manifest": store_manifest,
        "records": [{
            "record_id": r.record_id, "content_hash": r.content_hash,
            "source_uri": r.provenance.source_uri, "canonical_url": r.provenance.extra.get("canonical_url", ""),
            "content_sha256": r.provenance.content_sha256, "event": r.provenance.extra.get("event", ""),
            "year": r.provenance.extra.get("year", ""), "challenge": r.provenance.extra.get("challenge", ""),
            "source_origin": r.provenance.extra.get("source_origin", ""), "raw_artifact": r.provenance.extra.get("raw_artifact", ""),
            "extraction_version": r.schema_version,
        } for r in records],
    })

    _write_report(extraction_stats, quality, duplicate_report, per_doc)

    print(f"DomeCTF extraction complete -> {STORE_DIR}")
    print(f"  selected: {len(selected)} | records: {len(records)} | skipped: {len(skipped)}")
    print(f"  years: {dict(by_year)} | categories: {dict(by_cat)}")
    print(f"  distinct techniques: {stats.get('distinct_techniques', 0)} | tool docs: {tool_docs}")
    print(f"  mean trajectory completeness: {extraction_stats['trajectory']['mean_completeness']} | genuine reasoning chains: {genuine}")
    print(f"  with verification: {with_verification} | with failure/correction: {with_failures}")
    print(f"  dupes: internal={len(internal_dupes)} vs_local={vs_local['duplicate_count']} vs_jiaje={vs_jiaje['duplicate_count']} vs_redbud={vs_redbud['duplicate_count']}")
    return 0


def _write_report(stats, quality, dup, per_doc) -> None:
    t = stats["trajectory"]
    lines = [
        "# DomeCTF Historical Challenge-Level Extraction Report", "",
        f"Generated: {stats['generated_at']} - extraction: {stats['extraction_version']}", "",
        "Extracted the verified individual DomeCTF writeups from the frozen source-discovery corpus "
        "(`knowledge/domectf_sources_v1/`) into the isolated `knowledge/domectf_v1/` store by extending "
        "`ctf_ingest` (reused models/normalize/technique-table/store/dedup). Not connected to the "
        "solver/retrieval/benchmark; nothing fine-tuned. Reasoning stages are recorded EXPLICIT only "
        "when a section heading denotes them (solution/verification may also come from a concrete code "
        "block / flag), and are never fabricated.", "",
        f"- Sources selected: {stats['sources_selected']}",
        f"- KnowledgeRecords written: {stats['records_written']}",
        f"- Skipped: {len(stats['skipped'])}",
        f"- Distinct techniques: {stats['distinct_techniques']}",
        f"- Tool coverage (documents): {stats['tool_coverage_documents']}",
        f"- Mean trajectory completeness: {t['mean_completeness']}",
        f"- Genuine reasoning chains: {t['genuine_reasoning_chains']} / {stats['records_written']}",
        f"- With verification: {t['with_verification']}",
        f"- Failure/correction coverage: {stats['failure_correction_coverage']}",
        f"- Provenance completeness: {stats['provenance_completeness']}",
        "",
        "## Per-year breakdown", "",
        "| year | event | records | genuine reasoning | verification | mean completeness | categories |",
        "|---|---|---|---|---|---|---|",
    ]
    events = {str(d["year"]): d["event"] for d in per_doc}
    for y, b in stats["per_year_breakdown"].items():
        lines.append(f"| {y} | {events.get(y, '')} | {b['records']} | {b['genuine_trajectories']} | "
                     f"{b['with_verification']} | {b['mean_trajectory_completeness']} | {b['categories']} |")
    lines += [
        "",
        "## Category distribution", "",
    ]
    for cat, n in sorted(stats["category_distribution"].items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"- {cat}: {n}")
    lines += [
        "",
        "## Deduplication", "",
        f"- Internal near-duplicates: {dup['internal_domectf']['near_duplicate_count']}",
        f"- vs local writeups: {dup['vs_local_writeups']['duplicate_count']}",
        f"- vs Jia Jie v1: {dup['vs_jiaje_v1']['duplicate_count']}",
        f"- vs Jia Jie Redbud v1: {dup['vs_jiaje_redbud_v1']['duplicate_count']}",
        "",
        "## Knowledge quality (solution vs reasoning — NOT conflated)", "",
        f"- **Solution/technique knowledge**: {quality['solution_knowledge']['documents_with_solution_mechanism']} docs "
        f"with an explicit solution mechanism; {quality['solution_knowledge']['documents_with_techniques']} with techniques; "
        f"{quality['solution_knowledge']['documents_with_tools']} with tools.",
        f"- **Reasoning knowledge**: {quality['reasoning_knowledge']['genuine_reasoning_chains']} genuine reasoning chains; "
        f"{quality['reasoning_knowledge']['documents_with_any_reasoning_stage']} docs with any explicit intermediate reasoning stage; "
        f"mean completeness {quality['reasoning_knowledge']['mean_trajectory_completeness']}.",
        f"- **Failure/correction knowledge**: {quality['failure_knowledge']['documents_with_failure_correction']} docs.",
        f"- **Verification knowledge**: {quality['verification_knowledge']['documents_with_verification']} docs.",
        "",
        "## Limitations", "",
        "- These are published final writeups (mostly Beagle Security 'Story + Solution' pages and "
        "GitHub markdown), not think-aloud traces. They carry strong solution/technique knowledge but "
        "little explicit intermediate reasoning, so genuine reasoning-chain counts are honestly low.",
        "- The 2019 Rahul R source is a single multi-challenge walkthrough; it is kept as one record "
        "(not split) and its category is technique-vote inferred.",
        "- One 2019 Medium writeup remains ACCESS_BLOCKED at the source layer and is intentionally NOT "
        "extracted (no bypass attempted).",
        "- The three 2019 GitHub writeups are JS-rendered blob pages: the frozen static HTML captured "
        "in the source phase is largely GitHub UI chrome, so the actual markdown solution body is NOT "
        "present in the raw. Their records honestly carry identity (challenge/author/event/year) but "
        "MISSING solution/trajectory content; a future JS-render (or raw.githubusercontent.com fetch) "
        "would recover them. No content was invented to fill the gap.",
        "- Categories are EXPLICIT when a page states 'is a <category> challenge' (generic words like "
        "'CTF' are rejected), otherwise technique-vote INFERRED; unmatched cases are left MISSING "
        "rather than guessed.",
    ]
    _write(REPORTS / "domectf_extraction_report.md", "\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
