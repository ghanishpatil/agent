from __future__ import annotations

from typing import Tuple

from .base import (
    SpecialistAnalysis,
    SpecialistContext,
    ToolMechanism,
    analyze_with_tool,
    score_relevance,
)


# Static-first: cheap static inspection (strings/consts) before expensive dynamic analysis.
_MECHANISMS: Tuple[ToolMechanism, ...] = (
    ToolMechanism(
        "strings", "embedded plaintext / constant", "static-strings",
        ("binary", "elf", "exe", "strings", "reverse", "crackme", "executable"),
        "strings",
        "a human-readable flag-format constant appears in the binary",
        "no readable constant; the flag is computed/encoded rather than stored", 1,
    ),
    ToolMechanism(
        "decode", "reversible encoding transform", "static-decode",
        ("xor", "encode", "obfuscat", "transform", "rot", "base64", "key"),
        "decode",
        "applying the recovered transform yields flag-format text",
        "the transform does not yield readable text", 2,
    ),
    ToolMechanism(
        "keycheck", "hidden comparison / key-derivation check", "keycheck",
        ("compare", "password", "serial", "license", "check", "validate", "key"),
        "keycheck",
        "the comparison target (expected input) is recovered from the check",
        "the check is dynamic/opaque and needs a different angle", 3,
    ),
)


class ReverseSpecialist:
    name = "reverse"
    category = "reverse"

    def relevance(self, context: SpecialistContext) -> float:
        indicators = tuple(kw for m in _MECHANISMS for kw in m.indicators) + (
            "rev",
            "disassemble",
            "decompile",
            "ghidra",
            "assembly",
            "bytecode",
            "vm",
        )
        # Corpus uses "rev" for this category; count that too.
        base = score_relevance(context, self.category, indicators)
        if context.challenge.metadata.category.lower() == "rev":
            base = round(min(1.0, base + 0.6), 4)
        return base

    def analyze(self, context: SpecialistContext) -> SpecialistAnalysis:
        analysis = analyze_with_tool(
            context,
            specialist=self.name,
            category=self.category,
            id_prefix="reverse",
            mechanisms=_MECHANISMS,
            tool_default=("analyze_tool", "reverse_tool"),
            extra_relevance_indicators=("rev", "disassemble", "decompile", "bytecode", "vm"),
            memory_keywords=("strings", "xor", "decode", "reverse", "crackme"),
            reasoning_summary=(
                "Reasoned from executable structure: try the cheapest static inspection (embedded "
                "constants) before more expensive transform/keycheck analysis; distinguish "
                "stored-vs-computed flags by what the artifact actually reveals. Suspicious "
                "artifacts are only ever run through the controlled adapter, never directly."
            ),
            uncertainty=(
                "Whether the flag is stored, encoded, or computed is unresolved until a static "
                "probe returns; dynamic analysis is deferred unless static is inconclusive."
            ),
        )
        # Preserve the category-aware relevance (analyze_with_tool computed a base score).
        if context.challenge.metadata.category.lower() == "rev":
            from dataclasses import replace

            analysis = replace(analysis, relevance=self.relevance(context))
        return analysis
