"""Canonical synthetic labeled corpus for rigorous retrieval-quality evaluation.

Ground truth is explicit and controlled: each query names the record ids that are truly
relevant. Because the corpus and labels are authored together (not derived from the same
extractor under test), precision@k / recall@k / MRR here are non-circular.
"""

from __future__ import annotations

from typing import List, Tuple

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
from ctf_experiment.retrieval_eval import LabeledQuery
from ctf_ingest.retrieval import RetrievalQuery


def _record(rid, category, title, techniques, summary, insight="") -> KnowledgeRecord:
    tech = tuple(
        Technique(technique_id=t[0], name=t[1], category=category, keywords=t[2], confidence=0.7)
        for t in techniques
    )
    steps = (
        (TrajectoryStep(0, TrajectoryStepKind.EXPLOIT_SOLUTION, insight, 0.7, "Solution"),)
        if insight
        else ()
    )
    return KnowledgeRecord(
        record_id=rid,
        content_hash=f"hash-{rid}",
        provenance=Provenance(SourceType.LOCAL_DIRECTORY, "synthetic", f"{rid}.md"),
        metadata=ChallengeMetadata(name=title, category=category),
        techniques=tech,
        trajectory=ReasoningTrajectory(steps=steps, completeness=0.2 if steps else 0.0),
        title=title,
        summary=summary,
    )


def synthetic_labeled_corpus() -> Tuple[List[KnowledgeRecord], List[LabeledQuery]]:
    records = [
        _record("web-ssti-1", "web", "SSTI in profile renderer",
                [("ssti", "Server-Side Template Injection", ("ssti", "template injection", "jinja2"))],
                "server side template injection with jinja2 rendering user name",
                "inject {{7*7}} to confirm evaluation then read config"),
        _record("web-ssti-2", "web", "Template injection to RCE",
                [("ssti", "Server-Side Template Injection", ("ssti", "template", "rce"))],
                "template injection escalated to remote code execution"),
        _record("web-sqli-1", "web", "Union-based SQL injection",
                [("sql-injection", "SQL Injection", ("sql injection", "union select"))],
                "union based sql injection dumping the users table"),
        _record("web-jwt-1", "web", "JWT algorithm confusion",
                [("jwt-attack", "JWT Attack", ("jwt", "algorithm confusion", "alg none"))],
                "jwt rs256 to hs256 algorithm confusion to forge admin token"),
        _record("crypto-xor-1", "crypto", "Single-byte XOR",
                [("xor-cipher", "XOR Cipher", ("xor", "single-byte xor"))],
                "single byte xor brute force over 256 keys",
                "xor every byte with each key and look for CTF{"),
        _record("crypto-rsa-1", "crypto", "RSA low exponent",
                [("rsa-attack", "RSA Attack", ("rsa", "low exponent", "hastad"))],
                "rsa low public exponent hastad broadcast attack"),
        _record("crypto-caesar-1", "crypto", "Caesar shift",
                [("classical-cipher", "Classical Cipher", ("caesar", "rot13", "substitution cipher"))],
                "classical caesar shift cipher rotation of the alphabet"),
        _record("pwn-rop-1", "pwn", "ret2libc ROP chain",
                [("rop", "Return-Oriented Programming", ("rop", "ret2libc", "gadget"))],
                "return oriented programming ret2libc gadget chain"),
        _record("pwn-fmt-1", "pwn", "Format string leak",
                [("format-string", "Format String", ("format string", "%n", "%p"))],
                "format string vulnerability leaking stack and overwriting got"),
        _record("forensics-pcap-1", "forensics", "PCAP TCP stream",
                [("pcap-analysis", "PCAP Analysis", ("pcap", "wireshark", "tcp stream"))],
                "follow the tcp stream in wireshark to recover the flag"),
    ]
    queries = [
        LabeledQuery(
            "ssti",
            RetrievalQuery(text="a server-side template renders our name; jinja2 hint",
                           category="web", keywords=("ssti", "template injection")),
            relevant_ids=("web-ssti-1", "web-ssti-2"),
        ),
        LabeledQuery(
            "jwt",
            RetrievalQuery(text="forge an admin json web token via algorithm confusion",
                           category="web", keywords=("jwt", "algorithm confusion")),
            relevant_ids=("web-jwt-1",),
        ),
        LabeledQuery(
            "xor",
            RetrievalQuery(text="decode a single byte xor cipher blob",
                           category="crypto", keywords=("xor",)),
            relevant_ids=("crypto-xor-1",),
        ),
        LabeledQuery(
            "rsa",
            RetrievalQuery(text="rsa with a small public exponent broadcast",
                           category="crypto", keywords=("rsa", "hastad")),
            relevant_ids=("crypto-rsa-1",),
        ),
        LabeledQuery(
            "rop",
            RetrievalQuery(text="build a ret2libc rop chain from gadgets",
                           category="pwn", keywords=("rop", "ret2libc")),
            relevant_ids=("pwn-rop-1",),
        ),
        LabeledQuery(
            "pcap",
            RetrievalQuery(text="recover a flag from a network capture stream",
                           category="forensics", keywords=("pcap", "wireshark")),
            relevant_ids=("forensics-pcap-1",),
        ),
    ]
    return records, queries
