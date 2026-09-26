"""Parsing helpers: turn raw markdown/text/HTML into headed sections + clean body text."""

from __future__ import annotations

import re
from html import unescape
from typing import List, Tuple

from .models import MediaType, WriteupSection

_ATX_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_HTML_HEADING = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
_TAG = re.compile(r"<[^>]+>")
_SCRIPT_STYLE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
_MULTI_BLANK = re.compile(r"\n{3,}")
_TRAILING_WS = re.compile(r"[ \t]+\n")


def strip_html(text: str) -> str:
    text = _SCRIPT_STYLE.sub(" ", text)
    text = _HTML_HEADING.sub(lambda m: f"\n{'#' * int(m.group(1))} {m.group(2).strip()}\n", text)
    text = re.sub(r"</(p|div|li|ul|ol|tr|table|section|article|br)\s*>", "\n", text, flags=re.I)
    text = _TAG.sub(" ", text)
    return unescape(text)


def clean_body(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _TRAILING_WS.sub("\n", text)
    text = _MULTI_BLANK.sub("\n\n", text)
    return text.strip()


def _iter_heading_lines(lines: List[str]) -> List[Tuple[int, int, str]]:
    """Return (line_index, level, heading_text) for ATX and setext headings."""
    headings: List[Tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        match = _ATX_HEADING.match(line)
        if match:
            headings.append((index, len(match.group(1)), match.group(2).strip()))
            continue
        # setext: a text line followed by === or ---
        if index + 1 < len(lines) and line.strip():
            underline = lines[index + 1].strip()
            if underline and set(underline) <= {"="}:
                headings.append((index, 1, line.strip()))
            elif underline and set(underline) <= {"-"} and len(underline) >= 3:
                headings.append((index, 2, line.strip()))
    return headings


def parse_sections(text: str, media_type: MediaType) -> Tuple[str, Tuple[WriteupSection, ...]]:
    """Parse text into (title, sections). Section bodies exclude their heading line."""
    if media_type is MediaType.HTML:
        text = strip_html(text)
    text = clean_body(text)
    lines = text.split("\n")
    headings = _iter_heading_lines(lines)

    if not headings:
        title = _first_nonempty(lines)
        return title, (
            WriteupSection(order=0, heading=title or "document", level=1, body=text),
        )

    title = headings[0][2] if headings[0][1] == 1 else _first_nonempty(lines)
    sections: List[WriteupSection] = []
    heading_line_set = {index for index, _, _ in headings}
    for order, (line_index, level, heading_text) in enumerate(headings):
        start = line_index + 1
        end = headings[order + 1][0] if order + 1 < len(headings) else len(lines)
        body_lines = [
            lines[i]
            for i in range(start, end)
            # skip setext underline immediately after a heading
            if i not in heading_line_set and not _is_setext_underline(lines[i])
        ]
        body = clean_body("\n".join(body_lines))
        sections.append(
            WriteupSection(order=order, heading=heading_text, level=level, body=body)
        )
    return title, tuple(sections)


def _is_setext_underline(line: str) -> bool:
    s = line.strip()
    return bool(s) and (set(s) <= {"="} or (set(s) <= {"-"} and len(s) >= 3))


def _first_nonempty(lines: List[str]) -> str:
    for line in lines:
        stripped = line.strip().lstrip("#").strip()
        if stripped:
            return stripped[:200]
    return ""
