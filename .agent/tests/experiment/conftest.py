from __future__ import annotations

from pathlib import Path
from typing import Sequence, Tuple

import pytest

from ctf_ingest.models import (
    ChallengeMetadata,
    KnowledgeRecord,
    Provenance,
    ReasoningTrajectory,
    SourceType,
    Technique,
    TrajectoryStep,
    TrajectoryStepKind,
)


def make_record(
    record_id: str,
    category: str,
    title: str,
    techniques: Sequence[Tuple[str, str, Tuple[str, ...]]] = (),
    *,
    summary: str = "",
    insight: str = "",
    duplicate_of: str | None = None,
) -> KnowledgeRecord:
    tech = tuple(
        Technique(technique_id=tid, name=name, category=category, keywords=kw, confidence=0.7)
        for tid, name, kw in techniques
    )
    steps = (
        (
            TrajectoryStep(0, TrajectoryStepKind.EXPLOIT_SOLUTION, insight, 0.7, "Solution"),
        )
        if insight
        else ()
    )
    return KnowledgeRecord(
        record_id=record_id,
        content_hash=f"hash-{record_id}",
        provenance=Provenance(SourceType.LOCAL_DIRECTORY, "corpus", f"{record_id}.md"),
        metadata=ChallengeMetadata(name=title, category=category),
        techniques=tech,
        trajectory=ReasoningTrajectory(steps=steps, completeness=0.3 if steps else 0.0),
        title=title,
        summary=summary or title,
        duplicate_of=duplicate_of,
    )


@pytest.fixture
def labeled_corpus():
    """A controlled corpus with known relevant/irrelevant records per query."""
    records = [
        make_record(
            "web-ssti-1", "web", "SSTI in profile renderer",
            (("ssti", "Server-Side Template Injection", ("ssti", "template injection", "jinja2")),),
            summary="server side template injection with jinja2 rendering name",
            insight="inject {{7*7}} into the template to confirm evaluation",
        ),
        make_record(
            "web-ssti-2", "web", "Template injection to RCE",
            (("ssti", "Server-Side Template Injection", ("ssti", "template", "rce")),),
            summary="template injection escalated to remote code execution",
        ),
        make_record(
            "web-sqli-1", "web", "Union-based SQL injection",
            (("sql-injection", "SQL Injection", ("sql injection", "union select")),),
            summary="union based sql injection dumping users table",
        ),
        make_record(
            "crypto-xor-1", "crypto", "Single-byte XOR",
            (("xor-cipher", "XOR Cipher", ("xor", "single-byte xor")),),
            summary="single byte xor brute force over 256 keys",
        ),
        make_record(
            "crypto-rsa-1", "crypto", "RSA low exponent",
            (("rsa-attack", "RSA Attack", ("rsa", "low exponent", "hastad")),),
            summary="rsa low public exponent hastad broadcast attack",
        ),
        make_record(
            "pwn-rop-1", "pwn", "ret2libc ROP chain",
            (("rop", "Return-Oriented Programming", ("rop", "ret2libc", "gadget")),),
            summary="return oriented programming ret2libc gadget chain",
        ),
    ]
    return records


@pytest.fixture
def audit_root() -> Path:
    # tests/experiment/<file> -> parents[2] == .agent, parents[3] == workspace root
    return Path(__file__).resolve().parents[3] / ".agent_audit"
