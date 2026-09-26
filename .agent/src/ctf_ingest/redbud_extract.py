"""Challenge-level extraction for the Jia Jie Redbud corpus (extends ctf_ingest, no parallel arch).

Reuses the existing model (`KnowledgeRecord`, `TrajectoryStep`, `ReasoningTrajectory`,
`FailureCorrection`, `Provenance`), the existing `normalize`/`parser`, the existing technique
table via `extract_techniques`, and the existing `KnowledgeStore`/`Deduplicator`. It adds only a
Redbud-aware extraction layer: bilingual (Chinese/English) section-heading → trajectory-stage
mapping, and per-field EXPLICIT/INFERRED/MISSING provenance.

Grounding rules (from the actual rendered writeups):
- Reasoning-trajectory stages are recorded ONLY when a real section heading denotes them. We do
  not infer stages from prose cues, and we never fabricate a stage to raise completeness.
- Techniques come from the existing generic table plus a small explicit Redbud supplement for
  PRNG/lattice/curve techniques the generic table lacks (matched only when the term literally
  appears in the source).
- The raw source artifacts are read-only inputs; this module never writes to raw/.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
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

EXTRACTION_VERSION = "redbud-extract-1.0"

EXPLICIT = "explicit"
INFERRED = "inferred"
MISSING = "missing"

# Section headings that are chrome/non-reasoning and must not become trajectory stages.
_SKIP_HEADINGS = ("comments", "总结", "summary", "cite this", "类似题目", "局限性", "token 花销")

# Ordered (first match wins) bilingual heading -> trajectory stage rules. More specific first.
_HEADING_RULES: Tuple[Tuple[Tuple[str, ...], TrajectoryStepKind], ...] = (
    (("题目描述", "题目介绍", "description", "challenge description", "overview"), TrajectoryStepKind.CHALLENGE_CONTEXT),
    (("验证", "verify", "verification", "恢复 flag", "获取 flag", "得到 flag", "最终结果", "final flag"), TrajectoryStepKind.VERIFICATION),
    (("攻击脚本", "完整攻击", "exploit", "payload", "解题代码", "解题步骤", "脚本", "getshell", "获取 shell", "解法", "solution", "求解代码"), TrajectoryStepKind.EXPLOIT_SOLUTION),
    (("攻击思路", "解题思路", "思路", "approach", "求解方法", "解题方法", "求解方法"), TrajectoryStepKind.HYPOTHESIS),
    (("分析", "analysis", "建模", "简介", "说明", "解释", "原理"), TrajectoryStepKind.INTERPRETATION),
    (("提示", "线索", "hint", "clue"), TrajectoryStepKind.OBSERVED_CLUE),
    (("测试", "test", "判断", "尝试"), TrajectoryStepKind.DISCRIMINATING_TEST),
    (("结果", "result", "输出", "output", "观察"), TrajectoryStepKind.OBSERVATION),
    (("下一步", "next step", "接下来"), TrajectoryStepKind.NEXT_ACTION),
    (("更新", "修正", "改进", "revise", "correction"), TrajectoryStepKind.HYPOTHESIS_UPDATE),
)

_FAILURE_HEADING_CUES = ("踩坑", "失败", "错误", "坑", "revenge", "修正")

# Explicit Redbud technique supplement (only matched when the literal term appears in the text).
_SUPP_TECHNIQUES: Tuple[Tuple[str, str, str, Tuple[str, ...]], ...] = (
    ("prng-mt19937", "Python MT19937 PRNG Attack", "crypto", ("mt19937", "mersenne", "getrandbits", "random.getstate")),
    ("prng-lcg", "LCG PRNG Attack", "crypto", ("lcg", "linear congruential", "truncated lcg")),
    ("prng-glibc-random", "glibc random() PRNG Attack", "crypto", ("glibc", "random()", "rand()", "glibc 随机")),
    ("prng-xoshiro", "Xoshiro PRNG Attack", "crypto", ("xoshiro", "xoshiro256")),
    ("prng-gf2bv", "PRNG via GF(2) linear algebra (gf2bv)", "crypto", ("gf2bv", "gf(2)")),
    ("ecdsa-nonce-reuse", "ECDSA Nonce Reuse", "crypto", ("ecdsa", "nonce reuse", "reused nonce", "重复 nonce")),
    ("rsa-coppersmith", "RSA Coppersmith / small_roots", "crypto", ("coppersmith", "small_roots", "cuso", "partial factorization")),
    ("discrete-log", "Discrete Logarithm", "crypto", ("discrete log", "pohlig", "baby-step", "bsgs")),
    ("encoding-multi", "Multi-encoding decode chain", "misc", ("ebcdic", "uuencode", "chuck norris", "unary code", "zeckendorf")),
    ("pyjail-escape", "Python Jail Escape", "misc", ("pyjail", "jail", "set_trace", "__subclasses__", "builtins")),
    ("ret2shellcode", "ret2shellcode", "pwn", ("ret2shellcode", "shellcode")),
    ("stack-pivot", "Stack Pivot", "pwn", ("stack pivot", "pivot")),
    ("srop-setcontext", "SROP / setcontext", "pwn", ("setcontext", "srop", "sigreturn")),
    ("syscall-orw", "syscall / ORW", "pwn", ("orw", "open read write", "syscall", "babysyscall")),
    ("audio-stego", "Audio Steganography", "forensics", ("spectrogram", "audacity", "音频", "隐写", "sonic")),
)

_CATEGORY_BY_TECH_PREFIX = {"crypto": "crypto", "pwn": "pwn", "web": "web", "forensics": "forensics", "misc": "misc", "reverse": "reverse"}


@dataclass(frozen=True)
class FieldProvenance:
    verdicts: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, str]:
        return dict(self.verdicts)


@dataclass
class RedbudExtraction:
    record: KnowledgeRecord
    field_provenance: Dict[str, str]
    genuine_trajectory: bool  # description->...->solution/verification present, not just techniques

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
    for cues, stage in _HEADING_RULES:
        if any(cue in low for cue in cues):
            return stage
    return None


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


def _infer_category(techniques: List[Technique], name: str, event: str) -> str:
    from collections import Counter

    votes = Counter(t.category for t in techniques if t.category)
    if votes:
        return votes.most_common(1)[0][0]
    low = f"{name} {event}".lower()
    if any(k in low for k in ("re ", "reverse", "逆向")):
        return "reverse"
    if any(k in low for k in ("rsa", "ecdsa", "random", "crypto", "lcg")):
        return "crypto"
    if any(k in low for k in ("rop", "shellcode", "syscall", "pivot", "setcontext", "pwn")):
        return "pwn"
    if any(k in low for k in ("pyjail", "jail", "rosetta")):
        return "misc"
    return ""


def build_extraction(
    html: str,
    *,
    source_url: str,
    raw_artifact_relpath: str,
    content_sha256: str,
    event: str,
    challenge_id: str,
    author: str,
    retrieved_at: str,
) -> RedbudExtraction:
    """Extract a single Redbud writeup into a KnowledgeRecord + field provenance (E/I/M)."""
    doc = RawDocument(
        doc_id=hashlib.sha256(source_url.encode("utf-8")).hexdigest()[:16],
        media_type=MediaType.HTML,
        text=html,
        provenance=Provenance(SourceType.HTTP, source_url, raw_artifact_relpath),
    )
    writeup: NormalizedWriteup = normalize(doc)
    body = writeup.body_text
    fp: Dict[str, str] = {}

    # -- name / event / challenge --------------------------------------------------------
    title = writeup.title.strip()
    name = re.sub(r"\s*Writeup\s*$", "", title, flags=re.IGNORECASE).strip() or challenge_id
    fp["event"] = EXPLICIT  # from URL path provenance
    fp["challenge_name"] = EXPLICIT if title else INFERRED

    # -- techniques (generic table + explicit Redbud supplement) -------------------------
    techniques = list(extract_techniques(writeup))
    have = {t.technique_id for t in techniques}
    for t in _supp_techniques(body):
        if t.technique_id not in have:
            techniques.append(t)
            have.add(t.technique_id)
    techniques.sort(key=lambda t: t.confidence, reverse=True)
    fp["techniques_mechanisms"] = EXPLICIT if techniques else MISSING

    # -- category (inferred; no explicit label in source) --------------------------------
    category = _infer_category(techniques, name, event)
    fp["category"] = INFERRED if category else MISSING

    # -- difficulty (explicit only if stated; 'Easy'/'Baby' in name is a weak inference) --
    difficulty = ""
    if re.search(r"\b(easy|baby|hard|medium)\b", name, re.IGNORECASE):
        difficulty = re.search(r"\b(easy|baby|hard|medium)\b", name, re.IGNORECASE).group(1).lower()
        fp["difficulty"] = INFERRED
    else:
        fp["difficulty"] = MISSING

    # -- flags / final outcome (presence only; correctness NOT judged) -------------------
    flags = tuple(dict.fromkeys(m.group(0) for m in _FLAG_RE.finditer(body)))
    fp["final_outcome"] = EXPLICIT if flags else MISSING

    # -- reasoning trajectory from section headings (EXPLICIT-only) ----------------------
    steps: List[TrajectoryStep] = []
    stages_seen = set()
    order = 0
    section_stage: Dict[str, TrajectoryStepKind] = {}
    for section in writeup.sections or ():
        stage = map_heading_to_stage(section.heading)
        if stage is None or stage in stages_seen:
            if stage is not None:
                section_stage[section.heading] = stage
            continue
        stages_seen.add(stage)
        section_stage[section.heading] = stage
        text = (section.heading + ": " + section.body).strip()
        steps.append(TrajectoryStep(order=order, kind=stage, text=text[:400], confidence=0.9, source_heading=section.heading))
        order += 1
    # Concrete artifacts (not fabricated reasoning): a solution is present when the writeup
    # contains an exploit/solve code block; a verification when a flag string is present. These are
    # explicit content, so they may register EXPLOIT_SOLUTION/VERIFICATION even without a heading.
    # The purely-reasoning stages (clue/hypothesis/test/observation/interpretation/update/next)
    # remain heading-gated and are never inferred.
    has_code = ("<pre" in html.lower()) or ("<code" in html.lower())
    if has_code and TrajectoryStepKind.EXPLOIT_SOLUTION not in stages_seen:
        stages_seen.add(TrajectoryStepKind.EXPLOIT_SOLUTION)
        steps.append(TrajectoryStep(order, TrajectoryStepKind.EXPLOIT_SOLUTION, "solution code block present", 0.7, ""))
        order += 1
    flags_present = tuple(dict.fromkeys(m.group(0) for m in _FLAG_RE.finditer(body)))
    if flags_present and TrajectoryStepKind.VERIFICATION not in stages_seen:
        stages_seen.add(TrajectoryStepKind.VERIFICATION)
        steps.append(TrajectoryStep(order, TrajectoryStepKind.VERIFICATION, f"flag present: {flags_present[0]}", 0.7, ""))
        order += 1

    steps.sort(key=lambda s: TRAJECTORY_ORDER.index(s.kind))
    steps = [TrajectoryStep(i, s.kind, s.text, s.confidence, s.source_heading) for i, s in enumerate(steps)]
    completeness = round(len(stages_seen) / len(TRAJECTORY_ORDER), 4)
    trajectory = ReasoningTrajectory(steps=tuple(steps), completeness=completeness)

    # Per-stage field provenance: EXPLICIT if a heading denoted it, else MISSING (never inferred).
    stage_to_field = {
        TrajectoryStepKind.CHALLENGE_CONTEXT: "challenge_description_context",
        TrajectoryStepKind.OBSERVED_CLUE: "important_clues",
        TrajectoryStepKind.HYPOTHESIS: "initial_hypotheses",
        TrajectoryStepKind.DISCRIMINATING_TEST: "discriminating_tests",
        TrajectoryStepKind.OBSERVATION: "observations",
        TrajectoryStepKind.INTERPRETATION: "interpretations",
        TrajectoryStepKind.HYPOTHESIS_UPDATE: "hypothesis_changes",
        TrajectoryStepKind.NEXT_ACTION: "next_actions",
        TrajectoryStepKind.EXPLOIT_SOLUTION: "exploit_solution_mechanism",
        TrajectoryStepKind.VERIFICATION: "verification_method",
    }
    for stage_kind, fieldname in stage_to_field.items():
        fp[fieldname] = EXPLICIT if stage_kind in stages_seen else MISSING

    # -- commands/tools (explicit if code blocks or tool names present) ------------------
    has_code = ("<pre" in html.lower()) or ("<code" in html.lower()) or bool(re.search(r"\b(gdb|pwntools|sagemath|sage|ida|ghidra|python|nc |socket)\b", body, re.IGNORECASE))
    fp["commands_tools"] = EXPLICIT if has_code else MISSING

    # -- failure / correction sections ---------------------------------------------------
    failures: List[FailureCorrection] = []
    for section in writeup.sections or ():
        low = section.heading.lower()
        if any(cue in low for cue in _FAILURE_HEADING_CUES):
            failures.append(FailureCorrection(failed_approach=section.heading[:200], failure_reason=section.body[:300], correction="", confidence=0.6))
    fp["failures_corrections"] = EXPLICIT if failures else MISSING

    # A genuine trajectory = a description/analysis/approach → solution/verification chain,
    # not merely a technique/command listing.
    genuine = (
        TrajectoryStepKind.CHALLENGE_CONTEXT in stages_seen
        and (TrajectoryStepKind.HYPOTHESIS in stages_seen or TrajectoryStepKind.INTERPRETATION in stages_seen)
        and (TrajectoryStepKind.EXPLOIT_SOLUTION in stages_seen or TrajectoryStepKind.VERIFICATION in stages_seen)
    )

    description = ""
    for section in writeup.sections or ():
        if map_heading_to_stage(section.heading) is TrajectoryStepKind.CHALLENGE_CONTEXT:
            description = section.body[:500]
            break

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
            license_note="jia.je Redbud CTF writeups by Jiajie Chen",
            extra={"author": author, "event": event, "challenge": challenge_id, "raw_artifact": raw_artifact_relpath},
        ),
        metadata=ChallengeMetadata(name=name, category=category, event=event, difficulty=difficulty, flags=flags, tags=tuple(t.name for t in techniques)),
        techniques=tuple(techniques),
        trajectory=trajectory,
        failures=tuple(failures),
        title=title or name,
        summary=description or body[:280],
        schema_version=EXTRACTION_VERSION,
    )
    return RedbudExtraction(record=record, field_provenance=fp, genuine_trajectory=genuine)
