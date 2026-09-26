"""Challenge-level extraction for the verified DomeCTF corpus (extends ctf_ingest, additive).

Mirrors the additive pattern of ``redbud_extract.py``: it reuses the existing model
(`KnowledgeRecord`, `TrajectoryStep`, `ReasoningTrajectory`, `FailureCorrection`, `Provenance`),
the existing `normalize`, the existing generic technique table via `extract_techniques`, and the
existing `KnowledgeStore`/`Deduplicator`. It adds ONLY a DomeCTF-aware layer:

- an English section-heading -> trajectory-stage map grounded in the actual writeup structure
  (Beagle Security "Story"/"Solution" sections; GitHub/blog headings; GitHub/site chrome skipped);
- extraction of DomeCTF page metadata (challenge author, category statement, canonical link);
- per-field EXPLICIT / INFERRED / MISSING provenance.

Honesty rules (identical in spirit to the Redbud layer):
- Reasoning-trajectory stages are recorded ONLY when a real section heading denotes them; the two
  concrete-artifact stages (a solution when a code block is present, a verification when a flag
  string is present) may be recorded from content because they are artifacts, not reasoning.
- Purely-reasoning stages (clue/hypothesis/test/observation/interpretation/update/next action) are
  NEVER inferred from prose or from code — a writeup that jumps from description to exploit leaves
  those MISSING.
- Techniques come from the existing generic table plus a small, literal DomeCTF supplement.
- The source artifacts under domectf_sources_v1/ are read-only inputs; this module never writes.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .extract import _FLAG_RE, extract_techniques
from .models import (
    ChallengeMetadata,
    FailureCorrection,
    KnowledgeRecord,
    MediaType,
    NormalizedWriteup,
    Provenance,
    RawDocument,
    ReasoningTrajectory,
    SourceType,
    Technique,
    TRAJECTORY_ORDER,
    TrajectoryStep,
    TrajectoryStepKind,
)
from .normalize import normalize

EXTRACTION_VERSION = "domectf-extract-1.0"

EXPLICIT = "explicit"
INFERRED = "inferred"
MISSING = "missing"

# Section headings that are site/GitHub chrome and must never become trajectory stages.
_SKIP_HEADINGS = (
    "related articles", "related", "navigation menu", "files", "breadcrumbs", "footer",
    "footer navigation", "latest commit", "history", "file metadata and controls",
    "table of contents", "comments", "references", "share", "about the author",
)

# Ordered (first match wins) English heading -> trajectory-stage rules. Most specific first.
# Grounded in the real corpus: Beagle writeups use "Story" (challenge context) and "Solution".
_HEADING_RULES: Tuple[Tuple[Tuple[str, ...], TrajectoryStepKind], ...] = (
    (("verification", "verify", "getting the flag", "the flag", "final flag", "flag:"), TrajectoryStepKind.VERIFICATION),
    (("solution", "exploit", "exploitation", "getting shell", "getshell", "solve", "solving",
      "steps to solve", "walkthrough", "attack"), TrajectoryStepKind.EXPLOIT_SOLUTION),
    (("story", "description", "challenge description", "overview", "background", "scenario",
      "the challenge", "about"), TrajectoryStepKind.CHALLENGE_CONTEXT),
    (("approach", "idea", "plan", "strategy", "thought process", "how i", "methodology"), TrajectoryStepKind.HYPOTHESIS),
    (("analysis", "understanding", "recon", "reconnaissance", "enumeration", "investigation",
      "observations note", "explanation", "how it works"), TrajectoryStepKind.INTERPRETATION),
    (("hint", "hints", "clue", "clues"), TrajectoryStepKind.OBSERVED_CLUE),
    (("testing", "test", "trial", "experiment"), TrajectoryStepKind.DISCRIMINATING_TEST),
    (("result", "results", "output", "observation", "observations"), TrajectoryStepKind.OBSERVATION),
    (("next step", "next steps", "then ", "afterwards"), TrajectoryStepKind.NEXT_ACTION),
    (("correction", "revised", "revisit", "second attempt", "fix"), TrajectoryStepKind.HYPOTHESIS_UPDATE),
)

# Explicit failure/correction heading cues (recorded only when explicitly present).
_FAILURE_HEADING_CUES = ("failed attempt", "failed", "mistake", "didn't work", "did not work",
                         "gotcha", "pitfall", "wrong approach", "dead end", "rabbit hole")

# Small DomeCTF technique supplement — ONLY matched when the literal term appears in the source.
# Kept intentionally minimal; the goal is reusable knowledge, not maximising technique count.
_SUPP_TECHNIQUES: Tuple[Tuple[str, str, str, Tuple[str, ...]], ...] = (
    ("osint", "OSINT / Open-Source Intelligence", "osint", ("osint", "open-source intelligence", "open source intelligence", "geolocation", "reverse image")),
    ("hardware-tpm", "TPM / Hardware Security", "hardware", ("tpm", "trusted platform module", "hardware challenge", "firmware", "jtag", "uart")),
    ("steganography", "Steganography", "forensics", ("steganography", "steghide", "lsb", "zsteg", "exiftool", "spectrogram")),
    ("pcap-analysis", "PCAP / Network Forensics", "forensics", ("pcap", "wireshark", "tshark", "follow tcp stream", "network capture")),
    ("format-string", "Format String", "pwn", ("format string", "%p%p", "%n", "printf leak")),
    ("buffer-overflow", "Buffer Overflow", "pwn", ("buffer overflow", "stack overflow", "ret2", "return address", "overwrite eip", "overwrite rip")),
    ("rop", "Return-Oriented Programming", "pwn", ("rop", "gadget", "ret2libc", "return-oriented")),
    ("sqli", "SQL Injection", "web", ("sql injection", "sqli", "union select", "' or 1=1")),
    ("jwt-attack", "JWT Attack", "web", ("jwt", "jsonwebtoken", "alg:none", "none algorithm")),
    ("rsa-attack", "RSA Attack", "crypto", ("rsa", "modulus", "private exponent", "factordb", "wiener", "low exponent")),
    ("reversing", "Reverse Engineering", "reverse", ("ghidra", "ida pro", "radare2", "objdump", "decompile", "disassembl")),
)

# Map an explicit category statement / alias to a normalized category token.
_CATEGORY_ALIASES = {
    "pwn": "pwn", "binary": "pwn", "binary exploitation": "pwn",
    "web": "web", "crypto": "crypto", "cryptography": "crypto",
    "forensics": "forensics", "forensic": "forensics",
    "reversing": "reverse", "reverse": "reverse", "re": "reverse", "reverse engineering": "reverse",
    "osint": "osint", "hardware": "hardware", "misc": "misc", "miscellaneous": "misc",
    "stego": "forensics", "steganography": "forensics", "network": "forensics",
}

_META_AUTHOR_RE = (
    re.compile(r'<meta[^>]+name=["\']author["\'][^>]+content=["\']([^"\']*)["\']', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']author["\']', re.I),
)
_META_DESC_RE = (
    re.compile(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)["\']', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']description["\']', re.I),
)
_CANONICAL_RE = re.compile(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']*)["\']', re.I)
# "X is a pwn challenge", "This is an OSINT challenge", "a hardware challenge"
_CATEGORY_STMT_RE = re.compile(r"\bis an?\s+([A-Za-z][A-Za-z ]{1,24}?)\s+challenge", re.I)
_DIFFICULTY_RE = re.compile(r"\b(easy|medium|hard|insane|beginner|trivial)\b", re.I)


@dataclass
class DomectfExtraction:
    record: KnowledgeRecord
    field_provenance: Dict[str, str]
    genuine_trajectory: bool  # context -> reasoning -> solution/verification, not just a technique list

    def to_dict(self) -> Dict[str, object]:
        data = self.record.to_dict()
        data["field_provenance"] = self.field_provenance
        data["genuine_trajectory"] = self.genuine_trajectory
        return data


def map_heading_to_stage(heading: str) -> Optional[TrajectoryStepKind]:
    low = heading.strip().lower()
    if not low:
        return None
    for cue in _SKIP_HEADINGS:
        if low == cue or low.startswith(cue):
            return None
    # A GitHub-rendered markdown page repeats the challenge name as a heading; that is context-less
    # chrome for our purposes and is handled by the caller (it is neither a skip cue nor a stage).
    for cues, stage in _HEADING_RULES:
        if any(cue in low for cue in cues):
            return stage
    return None


def _meta(html: str, patterns) -> str:
    for rx in patterns:
        m = rx.search(html)
        if m:
            return m.group(1).strip()
    return ""


def canonical_link(html: str) -> str:
    m = _CANONICAL_RE.search(html)
    return m.group(1).strip() if m else ""


def _normalize_category(raw: str) -> str:
    token = raw.strip().lower()
    if token in _CATEGORY_ALIASES:
        return _CATEGORY_ALIASES[token]
    first = token.split()[0] if token.split() else ""
    return _CATEGORY_ALIASES.get(first, first)


# Words that appear in "is a <word> challenge" but are NOT real categories (generic filler). When
# one of these is stated, we fall back to technique-vote inference rather than trusting the word.
_GENERIC_NONCATEGORIES = {
    "ctf", "base", "challenge", "simple", "fun", "cool", "nice", "great", "standard", "normal",
    "basic", "interesting", "easy", "hard", "medium", "good", "small", "little", "quick",
}


def category_from_statement(text: str) -> str:
    """Return a normalized category if the source literally says 'is a(n) <cat> challenge'.

    Only trusted when the stated word is a plausible category (not generic filler like "CTF"),
    so a sentence like "is a CTF challenge" does not become a bogus category.
    """
    m = _CATEGORY_STMT_RE.search(text)
    if not m:
        return ""
    word = m.group(1).strip().lower()
    if word in _GENERIC_NONCATEGORIES or word.split()[0] in _GENERIC_NONCATEGORIES:
        return ""
    return _normalize_category(word)


def _supp_techniques(text: str) -> List[Technique]:
    low = text.lower()
    out: List[Technique] = []
    for tid, name, cat, kws in _SUPP_TECHNIQUES:
        hits = [k for k in kws if k in low]
        if hits:
            out.append(Technique(tid, name, cat, tuple(hits), round(min(1.0, 0.4 + 0.15 * len(hits)), 3), _ctx(text, hits[0])))
    return out


def _ctx(text: str, needle: str, width: int = 120) -> str:
    i = text.lower().find(needle.lower())
    if i < 0:
        return ""
    return " ".join(text[max(0, i - width // 2): i + len(needle) + width // 2].split())


def _infer_category(techniques: List[Technique]) -> str:
    from collections import Counter

    votes = Counter(t.category for t in techniques if t.category)
    return votes.most_common(1)[0][0] if votes else ""


def build_extraction(
    html: str,
    *,
    source_url: str,
    canonical_url: str,
    raw_artifact_relpath: str,
    content_sha256: str,
    event: str,
    year: Optional[int],
    challenge_id: str,
    reference_author: str,
    reference_challenge_name: str,
    source_origin: str,
    retrieved_at: str,
) -> DomectfExtraction:
    """Extract one DomeCTF writeup into a KnowledgeRecord + per-field E/I/M provenance."""
    doc = RawDocument(
        doc_id=hashlib.sha256(source_url.encode("utf-8")).hexdigest()[:16],
        media_type=MediaType.HTML,
        text=html,
        provenance=Provenance(SourceType.HTTP, source_url, raw_artifact_relpath),
    )
    writeup: NormalizedWriteup = normalize(doc)
    body = writeup.body_text
    fp: Dict[str, str] = {}

    # -- identity: name -----------------------------------------------------------------------
    meta_author = _meta(html, _META_AUTHOR_RE)
    meta_desc = _meta(html, _META_DESC_RE)
    page_title = re.sub(r"\s*(writeup|write-up)\s*$", "", writeup.title.strip(), flags=re.IGNORECASE).strip()
    name = reference_challenge_name.strip() or page_title or challenge_id
    fp["event"] = EXPLICIT
    fp["year"] = EXPLICIT if year else MISSING
    fp["challenge_name"] = EXPLICIT if (reference_challenge_name or page_title) else INFERRED

    # -- author -------------------------------------------------------------------------------
    author = meta_author or reference_author or ""
    if meta_author:
        fp["author"] = EXPLICIT           # stated on the page itself
    elif reference_author:
        fp["author"] = INFERRED           # only from the reference document anchor
    else:
        fp["author"] = MISSING

    # -- techniques (generic table + minimal literal DomeCTF supplement) ----------------------
    techniques = list(extract_techniques(writeup))
    have = {t.technique_id for t in techniques}
    for t in _supp_techniques(body + " " + meta_desc):
        if t.technique_id not in have:
            techniques.append(t)
            have.add(t.technique_id)
    techniques.sort(key=lambda t: t.confidence, reverse=True)
    fp["techniques_mechanisms"] = EXPLICIT if techniques else MISSING

    # -- category: EXPLICIT if the page states "is a <cat> challenge"; else technique-vote ----
    stmt_cat = category_from_statement(meta_desc) or category_from_statement(body[:200])
    if stmt_cat:
        category, fp["category"] = stmt_cat, EXPLICIT
    else:
        category = _infer_category(techniques)
        fp["category"] = INFERRED if category else MISSING

    # -- difficulty (explicit only if stated) -------------------------------------------------
    dm = _DIFFICULTY_RE.search(meta_desc) or _DIFFICULTY_RE.search(body[:400])
    difficulty = dm.group(1).lower() if dm else ""
    fp["difficulty"] = EXPLICIT if dm else MISSING

    # -- flags / final outcome (presence only; correctness NOT judged) ------------------------
    flags = tuple(dict.fromkeys(m.group(0) for m in _FLAG_RE.finditer(body)))
    fp["final_outcome"] = EXPLICIT if flags else MISSING

    # -- reasoning trajectory from section headings (EXPLICIT-only) ---------------------------
    steps: List[TrajectoryStep] = []
    stages_seen = set()
    order = 0
    for section in writeup.sections or ():
        stage = map_heading_to_stage(section.heading)
        if stage is None or stage in stages_seen:
            continue
        stages_seen.add(stage)
        text = (section.heading + ": " + section.body).strip()
        steps.append(TrajectoryStep(order=order, kind=stage, text=text[:400], confidence=0.9, source_heading=section.heading))
        order += 1

    # Concrete artifacts (not fabricated reasoning): code block -> a solution is present; a flag
    # string -> a verification is present. These may register even without a heading.
    has_code = ("<pre" in html.lower()) or ("<code" in html.lower())
    if has_code and TrajectoryStepKind.EXPLOIT_SOLUTION not in stages_seen:
        stages_seen.add(TrajectoryStepKind.EXPLOIT_SOLUTION)
        steps.append(TrajectoryStep(order, TrajectoryStepKind.EXPLOIT_SOLUTION, "solution code block present", 0.7, ""))
        order += 1
    if flags and TrajectoryStepKind.VERIFICATION not in stages_seen:
        stages_seen.add(TrajectoryStepKind.VERIFICATION)
        steps.append(TrajectoryStep(order, TrajectoryStepKind.VERIFICATION, f"flag present: {flags[0]}", 0.7, ""))
        order += 1

    steps.sort(key=lambda s: TRAJECTORY_ORDER.index(s.kind))
    steps = [TrajectoryStep(i, s.kind, s.text, s.confidence, s.source_heading) for i, s in enumerate(steps)]
    completeness = round(len(stages_seen) / len(TRAJECTORY_ORDER), 4)
    trajectory = ReasoningTrajectory(steps=tuple(steps), completeness=completeness)

    # Per-stage field provenance: EXPLICIT if a heading (or concrete artifact) denoted it, else
    # MISSING (never inferred — a description->exploit jump leaves the middle stages MISSING).
    stage_to_field = {
        TrajectoryStepKind.CHALLENGE_CONTEXT: "challenge_description_context",
        TrajectoryStepKind.OBSERVED_CLUE: "supplied_clues",
        TrajectoryStepKind.HYPOTHESIS: "initial_hypotheses",
        TrajectoryStepKind.DISCRIMINATING_TEST: "discriminating_tests",
        TrajectoryStepKind.OBSERVATION: "observations",
        TrajectoryStepKind.INTERPRETATION: "interpretations",
        TrajectoryStepKind.HYPOTHESIS_UPDATE: "hypothesis_changes",
        TrajectoryStepKind.NEXT_ACTION: "next_actions",
        TrajectoryStepKind.EXPLOIT_SOLUTION: "solution_mechanism",
        TrajectoryStepKind.VERIFICATION: "verification_method",
    }
    for stage_kind, fieldname in stage_to_field.items():
        fp[fieldname] = EXPLICIT if stage_kind in stages_seen else MISSING

    # -- commands / tools ---------------------------------------------------------------------
    tools_present = has_code or bool(re.search(
        r"\b(gdb|pwntools|nc |netcat|python|sage|ghidra|ida|radare2|wireshark|tshark|steghide|"
        r"exiftool|binwalk|john|hashcat|burp|curl|nmap|objdump|strings)\b", body, re.IGNORECASE))
    fp["commands_tools"] = EXPLICIT if tools_present else MISSING

    # -- failure / correction (explicit heading cues only) ------------------------------------
    failures: List[FailureCorrection] = []
    for section in writeup.sections or ():
        low = section.heading.lower()
        if any(cue in low for cue in _FAILURE_HEADING_CUES):
            failures.append(FailureCorrection(
                failed_approach=section.heading[:200], failure_reason=section.body[:300],
                correction="", confidence=0.6))
    fp["failures_corrections"] = EXPLICIT if failures else MISSING

    # A genuine trajectory = context/analysis/approach -> solution/verification, not just a
    # technique/command listing. Beagle "Story + Solution" pages have context + solution but no
    # explicit reasoning stage, so they are honestly NOT genuine reasoning chains.
    genuine = (
        TrajectoryStepKind.CHALLENGE_CONTEXT in stages_seen
        and (TrajectoryStepKind.HYPOTHESIS in stages_seen or TrajectoryStepKind.INTERPRETATION in stages_seen)
        and (TrajectoryStepKind.EXPLOIT_SOLUTION in stages_seen or TrajectoryStepKind.VERIFICATION in stages_seen)
    )

    # description/context text (from a context-mapped heading only)
    description = ""
    for section in writeup.sections or ():
        if map_heading_to_stage(section.heading) is TrajectoryStepKind.CHALLENGE_CONTEXT:
            description = section.body[:500]
            break
    fp["challenge_description_context"] = EXPLICIT if description else fp.get("challenge_description_context", MISSING)

    record = KnowledgeRecord(
        record_id=doc.doc_id,
        content_hash=writeup.normalized_sha256,
        provenance=Provenance(
            source_type=SourceType.HTTP,
            source_uri=source_url,
            document_path=raw_artifact_relpath,
            retrieved_at=retrieved_at,
            revision=EXTRACTION_VERSION,
            content_sha256=content_sha256,
            license_note="DomeCTF (c0c0n) historical writeups; see per-source author",
            extra={
                "author": author, "event": event, "year": str(year or ""), "challenge": challenge_id,
                "canonical_url": canonical_url, "raw_artifact": raw_artifact_relpath,
                "source_origin": source_origin,
            },
        ),
        metadata=ChallengeMetadata(
            name=name, category=category, event=event, difficulty=difficulty,
            flags=flags, tags=tuple(t.name for t in techniques)),
        techniques=tuple(techniques),
        trajectory=trajectory,
        failures=tuple(failures),
        title=writeup.title or name,
        summary=(meta_desc or description or body[:280]).strip(),
        schema_version=EXTRACTION_VERSION,
    )
    return DomectfExtraction(record=record, field_provenance=fp, genuine_trajectory=genuine)
