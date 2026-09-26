from __future__ import annotations

from typing import Tuple

from .base import (
    SpecialistAnalysis,
    SpecialistContext,
    ToolMechanism,
    analyze_with_tool,
)


# Identify artifact -> determine likely hiding mechanism -> extract -> validate. Do NOT run every
# forensic tool blindly: only mechanisms whose indicators are present are proposed.
_MECHANISMS: Tuple[ToolMechanism, ...] = (
    ToolMechanism(
        "trailer", "appended trailer / carved payload", "appended-data",
        ("trailer", "append", "carve", "binwalk", "embedded", "overlay", "extra data", "zip"),
        "trailer_scan",
        "a payload after the file's logical end contains flag-format data",
        "no trailing payload found", 1,
    ),
    ToolMechanism(
        "exif", "EXIF / document metadata", "metadata",
        ("exif", "metadata", "comment", "author", "jpeg", "png", "document", "pdf"),
        "exif_comment",
        "a metadata/comment field carries the flag",
        "no metadata field contains flag-format data", 1,
    ),
    ToolMechanism(
        "strings", "plaintext in the artifact", "strings",
        ("strings", "plaintext", "log", "capture", "pcap", "dump", "memory"),
        "strings",
        "a flag-format string is present in the raw bytes",
        "no readable flag-format string present", 1,
    ),
    ToolMechanism(
        "lsb", "LSB steganography indicator", "stego-lsb",
        ("stego", "lsb", "least significant", "hidden", "steg", "bitplane"),
        "lsb",
        "LSB extraction yields flag-format data",
        "LSB planes show no structured payload", 2,
    ),
)


class ForensicsSpecialist:
    name = "forensics"
    category = "forensics"

    def relevance(self, context: SpecialistContext) -> float:
        from .base import score_relevance

        indicators = tuple(kw for m in _MECHANISMS for kw in m.indicators) + (
            "forensics",
            "stego",
            "disk",
            "filesystem",
            "artifact",
            "recover",
        )
        return score_relevance(context, self.category, indicators)

    def analyze(self, context: SpecialistContext) -> SpecialistAnalysis:
        return analyze_with_tool(
            context,
            specialist=self.name,
            category=self.category,
            id_prefix="forensics",
            mechanisms=_MECHANISMS,
            tool_default=("analyze_tool", "forensics_tool"),
            extra_relevance_indicators=("forensics", "stego", "disk", "recover", "artifact"),
            memory_keywords=("exif", "trailer", "strings", "stego", "carve"),
            reasoning_summary=(
                "Identified the artifact type, enumerated only the hiding mechanisms its indicators "
                "support, and ordered by cheapest extraction first. A tool failure blocks the "
                "specific extraction; it does not disprove that the data is hidden by another "
                "mechanism."
            ),
            uncertainty=(
                "The hiding mechanism is unresolved until an extraction returns; multiple "
                "mechanisms may be plausible simultaneously and are tested cheapest-first."
            ),
        )
