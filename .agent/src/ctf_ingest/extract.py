"""Heuristic extraction stages.

These extractors are deliberately conservative: they recover structure when clear cues
exist and otherwise leave fields empty or low-confidence. They never invent a flag,
technique, or reasoning step that is not supported by the source text.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from .models import (
    ChallengeMetadata,
    FailureCorrection,
    NormalizedWriteup,
    ReasoningTrajectory,
    Technique,
    TrajectoryStep,
    TrajectoryStepKind,
    TRAJECTORY_ORDER,
    WriteupSection,
)

# --------------------------------------------------------------------------------------
# Challenge metadata.
# --------------------------------------------------------------------------------------

_CATEGORY_KEYWORDS: Dict[str, Tuple[str, ...]] = {
    "web": ("web", "http", "sql injection", "xss", "ssti", "ssrf", "cookie", "jwt", "csrf"),
    "crypto": ("crypto", "cipher", "rsa", "aes", "xor", "encrypt", "decrypt", "hash", "ecc"),
    "pwn": ("pwn", "buffer overflow", "rop", "shellcode", "heap", "format string", "libc", "ret2"),
    "reverse": ("reverse", "reversing", "disassembl", "decompil", "ghidra", "ida", "binary ninja"),
    "forensics": ("forensic", "pcap", "wireshark", "memory dump", "volatility", "carve", "stego"),
    "misc": ("misc", "jail", "escape", "scripting"),
    "osint": ("osint", "geolocat", "open source intelligence"),
    "blockchain": ("blockchain", "solidity", "smart contract", "ethereum", "evm"),
    "hardware": ("hardware", "firmware", "uart", "jtag", "logic analyzer"),
}

_FLAG_RE = re.compile(r"[A-Za-z0-9_]{2,32}\{[^}\n]{1,200}\}")
_FLAG_FORMAT_RE = re.compile(r"([A-Za-z0-9_]{2,32})\{\s*(?:\.\.\.|[A-Za-z0-9_ ]{0,40})\s*\}")
_POINTS_RE = re.compile(r"\b(\d{2,4})\s*(?:pts?|points)\b", re.IGNORECASE)
_DIFFICULTY_RE = re.compile(r"\b(easy|medium|hard|insane|beginner|trivial)\b", re.IGNORECASE)
# Tolerate markdown/markup around an explicit label, e.g. "**Category:** Forensics",
# "## Category - Web", "`category`: crypto". Leading emphasis/heading/quote markers and
# emphasis around the word "category" and the separator are stripped before the value.
_CATEGORY_LABEL_RE = re.compile(
    r"^[\s>#*_`~-]*category[\s*_`~]*[:\-][\s*_`~]*([A-Za-z][A-Za-z/ +-]*)",
    re.IGNORECASE | re.MULTILINE,
)


def extract_metadata(writeup: NormalizedWriteup) -> ChallengeMetadata:
    body = writeup.body_text
    lower = body.lower()

    flags = _dedupe_preserve(match.group(0) for match in _FLAG_RE.finditer(body))
    flag_format = ""
    techniques = extract_techniques(writeup)
    # Category labels may live in a heading (dropped from body_text) or in the body; search both.
    label_search = "\n".join(
        [writeup.title, *(section.heading for section in writeup.sections or ()), body]
    )
    labelled = _CATEGORY_LABEL_RE.search(label_search)
    category = _normalize_category(labelled.group(1)) if labelled else ""
    if not category:
        category = _infer_category(lower, techniques)

    fmt_match = _FLAG_FORMAT_RE.search(body)
    if fmt_match:
        flag_format = f"{fmt_match.group(1)}{{...}}"
    elif flags:
        prefix = flags[0].split("{", 1)[0]
        flag_format = f"{prefix}{{...}}"

    points = None
    points_match = _POINTS_RE.search(body)
    if points_match:
        points = int(points_match.group(1))

    difficulty_match = _DIFFICULTY_RE.search(body)
    difficulty = difficulty_match.group(1).lower() if difficulty_match else ""

    tags = tuple(technique.name for technique in techniques)
    return ChallengeMetadata(
        name=writeup.title,
        category=category,
        points=points,
        difficulty=difficulty,
        flag_format=flag_format,
        flags=flags,
        tags=tags,
    )


def _infer_category(lower: str, techniques: Tuple["Technique", ...] = ()) -> str:
    """Infer category from technique-category votes (primary) + keyword hits (secondary).

    Generic keyword counting alone lets high-frequency crypto/web vocabulary drown out
    distinctive-but-sparse signals (e.g. a forensics writeup that also decodes ciphertext).
    Extracted techniques carry a precise category and a confidence, so a confidence-weighted
    technique vote is the stronger signal; keyword hits only break ties / seed empty cases.
    """
    scores: Dict[str, float] = {category: 0.0 for category in _CATEGORY_KEYWORDS}
    for technique in techniques:
        if technique.category in scores:
            scores[technique.category] += 2.0 * max(technique.confidence, 0.1)
    for category, keywords in _CATEGORY_KEYWORDS.items():
        hits = sum(lower.count(keyword) for keyword in keywords)
        scores[category] += min(hits, 3) * 0.5  # cap keyword influence so it cannot dominate
    best = max(scores, key=lambda c: (scores[c], c)) if scores else ""
    return best if scores.get(best, 0.0) > 0.0 else ""


_CATEGORY_ALIASES = {
    "rev": "reverse",
    "re": "reverse",
    "reversing": "reverse",
    "cry": "crypto",
    "crypto": "crypto",
    "cryptography": "crypto",
    "cryptanalysis": "crypto",
    "for": "forensics",
    "forensic": "forensics",
    "forensics": "forensics",
    "binary": "pwn",
    "exploitation": "pwn",
    "pwning": "pwn",
    "miscellaneous": "misc",
    "stego": "forensics",
    "steganography": "forensics",
}


def _normalize_category(raw: str) -> str:
    token = raw.strip().lower().split()[0] if raw.strip() else ""
    token = token.strip("*_`~#:- ")
    return _CATEGORY_ALIASES.get(token, token)


# --------------------------------------------------------------------------------------
# Techniques.
# --------------------------------------------------------------------------------------

_TECHNIQUE_TABLE: Tuple[Tuple[str, str, str, Tuple[str, ...]], ...] = (
    ("sql-injection", "SQL Injection", "web", ("sql injection", "sqli", "union select", "' or '1'='1")),
    ("xss", "Cross-Site Scripting", "web", ("xss", "cross-site scripting", "<script>")),
    ("ssti", "Server-Side Template Injection", "web", ("ssti", "template injection", "{{7*7}}", "jinja2")),
    ("ssrf", "Server-Side Request Forgery", "web", ("ssrf", "server-side request forgery")),
    ("jwt-attack", "JWT Attack", "web", ("jwt", "algorithm confusion", "alg none", "kid injection")),
    ("idor", "Insecure Direct Object Reference", "web", ("idor", "insecure direct object")),
    ("path-traversal", "Path Traversal", "web", ("path traversal", "directory traversal", "../")),
    ("rsa-attack", "RSA Attack", "crypto", ("rsa", "modulus", "common modulus", "wiener", "hastad", "low exponent")),
    ("xor-cipher", "XOR Cipher", "crypto", ("xor", "single-byte xor", "repeating key xor")),
    ("aes-mode-attack", "AES Mode Attack", "crypto", ("aes", "ecb", "cbc", "padding oracle", "bit flip")),
    ("classical-cipher", "Classical Cipher", "crypto", ("caesar", "vigenere", "substitution cipher", "rot13")),
    ("hash-attack", "Hash Attack", "crypto", ("hash", "length extension", "collision", "md5", "sha1")),
    ("buffer-overflow", "Buffer Overflow", "pwn", ("buffer overflow", "stack overflow", "smash the stack")),
    ("rop", "Return-Oriented Programming", "pwn", ("rop", "return-oriented", "gadget", "ret2libc", "ret2")),
    ("format-string", "Format String", "pwn", ("format string", "%n", "%p%p")),
    ("heap-exploit", "Heap Exploitation", "pwn", ("heap", "tcache", "fastbin", "use-after-free", "double free")),
    ("static-analysis", "Static Analysis", "reverse", ("ghidra", "ida", "disassembl", "decompil", "radare")),
    ("dynamic-analysis", "Dynamic Analysis", "reverse", ("gdb", "debugger", "ltrace", "strace", "breakpoint")),
    ("steganography", "Steganography", "forensics", ("steg", "lsb", "zsteg", "steghide", "hidden data")),
    ("pcap-analysis", "PCAP Analysis", "forensics", ("pcap", "wireshark", "tshark", "packet capture")),
    ("memory-forensics", "Memory Forensics", "forensics", ("volatility", "memory dump", "memdump")),
)


def extract_techniques(writeup: NormalizedWriteup) -> Tuple[Technique, ...]:
    lower = writeup.body_text.lower()
    found: List[Technique] = []
    for technique_id, name, category, keywords in _TECHNIQUE_TABLE:
        hits = [keyword for keyword in keywords if keyword in lower]
        if not hits:
            continue
        total = sum(lower.count(keyword) for keyword in hits)
        confidence = min(1.0, 0.4 + 0.15 * total)
        evidence = _first_context(writeup.body_text, hits[0])
        found.append(
            Technique(
                technique_id=technique_id,
                name=name,
                category=category,
                keywords=tuple(hits),
                confidence=round(confidence, 3),
                evidence=evidence,
            )
        )
    found.sort(key=lambda t: t.confidence, reverse=True)
    return tuple(found)


def _first_context(text: str, needle: str, width: int = 120) -> str:
    index = text.lower().find(needle.lower())
    if index < 0:
        return ""
    start = max(0, index - width // 2)
    end = min(len(text), index + len(needle) + width // 2)
    return " ".join(text[start:end].split())


# --------------------------------------------------------------------------------------
# Reasoning trajectory.
# --------------------------------------------------------------------------------------

_STEP_CUES: Dict[TrajectoryStepKind, Tuple[str, ...]] = {
    TrajectoryStepKind.CHALLENGE_CONTEXT: (
        "challenge", "we are given", "we're given", "description", "the task", "provided with",
    ),
    TrajectoryStepKind.OBSERVED_CLUE: (
        "notice", "noticed", "we see", "observe", "interesting", "the hint", "clue", "found that",
    ),
    TrajectoryStepKind.CANDIDATE_MECHANISM: (
        "might be", "could be", "possibly", "candidate", "suspect", "looks like", "seems like",
    ),
    TrajectoryStepKind.HYPOTHESIS: (
        "hypothesis", "i think", "we think", "assume", "guess that", "theory", "likely that",
    ),
    TrajectoryStepKind.DISCRIMINATING_TEST: (
        "to test", "let's test", "let us test", "to confirm", "to check", "probe", "verify whether",
    ),
    TrajectoryStepKind.OBSERVATION: (
        "the result", "response was", "output was", "returned", "we get", "we got", "it printed",
    ),
    TrajectoryStepKind.INTERPRETATION: (
        "this means", "which means", "indicates", "so the", "therefore", "implies", "confirms",
    ),
    TrajectoryStepKind.HYPOTHESIS_UPDATE: (
        "so it is not", "ruled out", "instead it", "actually", "turns out", "revised", "updated",
    ),
    TrajectoryStepKind.NEXT_ACTION: (
        "next", "then we", "now we", "proceed", "the next step", "afterwards", "we then",
    ),
    TrajectoryStepKind.EXPLOIT_SOLUTION: (
        "exploit", "payload", "final script", "solve script", "the solution", "we craft", "poc",
    ),
    TrajectoryStepKind.VERIFICATION: (
        "the flag is", "we get the flag", "flag:", "submitted", "verified", "accepted", "correct flag",
    ),
}

_HEADING_CUES: Dict[str, TrajectoryStepKind] = {
    "description": TrajectoryStepKind.CHALLENGE_CONTEXT,
    "challenge": TrajectoryStepKind.CHALLENGE_CONTEXT,
    "overview": TrajectoryStepKind.CHALLENGE_CONTEXT,
    "recon": TrajectoryStepKind.OBSERVED_CLUE,
    "analysis": TrajectoryStepKind.INTERPRETATION,
    "approach": TrajectoryStepKind.HYPOTHESIS,
    "solution": TrajectoryStepKind.EXPLOIT_SOLUTION,
    "exploit": TrajectoryStepKind.EXPLOIT_SOLUTION,
    "flag": TrajectoryStepKind.VERIFICATION,
}

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


def extract_trajectory(writeup: NormalizedWriteup) -> ReasoningTrajectory:
    steps: List[TrajectoryStep] = []
    order = 0
    for section in writeup.sections or ():
        heading_kind = _heading_kind(section.heading)
        for sentence in _sentences(section.body):
            kind = _classify_sentence(sentence, heading_kind)
            if kind is None:
                continue
            steps.append(
                TrajectoryStep(
                    order=order,
                    kind=kind,
                    text=sentence[:400],
                    confidence=_step_confidence(sentence, kind, heading_kind),
                    source_heading=section.heading,
                )
            )
            order += 1

    steps = _collapse_adjacent_duplicates(steps)
    present = {step.kind for step in steps}
    completeness = round(len(present & set(TRAJECTORY_ORDER)) / len(TRAJECTORY_ORDER), 3)
    return ReasoningTrajectory(steps=tuple(steps), completeness=completeness)


def _sentences(body: str) -> List[str]:
    return [s.strip() for s in _SENTENCE_SPLIT.split(body) if s.strip()]


def _heading_kind(heading: str) -> Optional[TrajectoryStepKind]:
    low = heading.lower()
    for cue, kind in _HEADING_CUES.items():
        if cue in low:
            return kind
    return None


def _classify_sentence(
    sentence: str, heading_kind: Optional[TrajectoryStepKind]
) -> Optional[TrajectoryStepKind]:
    low = sentence.lower()
    best: Optional[TrajectoryStepKind] = None
    best_score = 0
    for kind, cues in _STEP_CUES.items():
        score = sum(1 for cue in cues if cue in low)
        if score > best_score:
            best_score = score
            best = kind
    if best is not None:
        return best
    return heading_kind


def _step_confidence(
    sentence: str, kind: TrajectoryStepKind, heading_kind: Optional[TrajectoryStepKind]
) -> float:
    low = sentence.lower()
    cue_hits = sum(1 for cue in _STEP_CUES[kind] if cue in low)
    base = 0.3 if cue_hits == 0 else min(0.9, 0.5 + 0.15 * cue_hits)
    if heading_kind is kind:
        base = min(1.0, base + 0.1)
    return round(base, 3)


def _collapse_adjacent_duplicates(steps: List[TrajectoryStep]) -> List[TrajectoryStep]:
    collapsed: List[TrajectoryStep] = []
    for step in steps:
        if collapsed and collapsed[-1].kind is step.kind and collapsed[-1].text == step.text:
            continue
        collapsed.append(step)
    # Re-number order densely.
    return [
        TrajectoryStep(order=i, kind=s.kind, text=s.text, confidence=s.confidence, source_heading=s.source_heading)
        for i, s in enumerate(collapsed)
    ]


# --------------------------------------------------------------------------------------
# Failure / correction.
# --------------------------------------------------------------------------------------

_FAILURE_CUES = (
    "didn't work", "did not work", "doesn't work", "failed", "no luck", "dead end",
    "this was wrong", "not the intended", "red herring", "got stuck", "wasn't it",
)
_CORRECTION_CUES = ("instead", "turned out", "actually", "the trick was", "the real", "however", "but then")


def extract_failures(writeup: NormalizedWriteup) -> Tuple[FailureCorrection, ...]:
    results: List[FailureCorrection] = []
    for section in writeup.sections or ():
        sentences = _sentences(section.body)
        for index, sentence in enumerate(sentences):
            low = sentence.lower()
            if not any(cue in low for cue in _FAILURE_CUES):
                continue
            correction = ""
            reason = sentence[:300]
            for follow in sentences[index + 1 : index + 3]:
                if any(cue in follow.lower() for cue in _CORRECTION_CUES):
                    correction = follow[:300]
                    break
            confidence = 0.6 if correction else 0.4
            results.append(
                FailureCorrection(
                    failed_approach=sentence[:300],
                    failure_reason=reason,
                    correction=correction,
                    confidence=confidence,
                )
            )
    return tuple(results)


def _dedupe_preserve(items) -> Tuple[str, ...]:
    seen = set()
    out: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return tuple(out)
