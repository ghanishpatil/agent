"""Deterministic, grounded CTF writeup generator + grounding validator.

Input is the authoritative ``SolveResult`` plus the runtime session journal and recorded
observations. Output is Markdown that reconstructs ONLY what the runtime actually did. The generator
is deterministic (every sentence is derived from a trace field), so it is grounded by construction;
the validator is a defensive double-check and the guard for any future model-assisted phrasing pass.

Hard rules:
* A writeup is produced ONLY when ``result.status == SOLVED``.
* The flag is copied verbatim from ``result.verified_flag`` — never inferred or validated here.
* Sections with no supporting evidence are omitted.
* Attempted / supported / disproven / unresolved / blocked distinctions are preserved.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from ctf_agent.autonomy.contracts import SolveResult, SolveStatus

_FAILURE_CLASSES = {
    "RATE_LIMIT": "was rate-limited",
    "TIMEOUT": "timed out",
    "NETWORK_FAILURE": "failed at the network layer",
    "TOOL_FAILURE": "hit a tool failure",
    "ENVIRONMENT_FAILURE": "hit an environment failure",
    "AUTH_FAILURE": "was rejected by authentication",
    "AUTHZ_FAILURE": "was rejected by authorization",
    "INPUT_REJECTION": "was rejected as invalid input",
}
_FLAGISH = re.compile(r"[A-Za-z0-9_]+\{[^}]*\}")


@dataclass(frozen=True)
class WriteupResult:
    markdown: str
    grounded: bool
    errors: tuple
    flag: Optional[str]


def generate_writeup(
    result: SolveResult,
    session_journal: Sequence[Dict[str, Any]] = (),
    observations: Sequence[Dict[str, Any]] = (),
) -> WriteupResult:
    """Deterministically build a grounded Markdown writeup for a SOLVED result."""
    if result.status is not SolveStatus.SOLVED or not result.verified_flag:
        return WriteupResult("", False, ("writeup only generated for a SOLVED result with a verified flag",), None)

    facts = {f.name: f.value for f in result.understanding.facts} if result.understanding else {}
    obs_texts = [str(o.get("output", "")) for o in observations if o.get("output")]

    lines: List[str] = [f"# {result.challenge_name or 'Challenge'}", ""]

    # ## Description
    desc = facts.get("description") or facts.get("challenge_description")
    if desc:
        lines += ["## Description", str(desc).strip(), ""]

    # ## Initial Analysis (attack surfaces / likely categories, only if present)
    if result.understanding and (result.understanding.attack_surfaces or result.understanding.likely_categories):
        bits = []
        if result.understanding.likely_categories:
            bits.append("Likely category: " + ", ".join(result.understanding.likely_categories) + ".")
        if result.understanding.attack_surfaces:
            bits.append("Attack surface: " + ", ".join(result.understanding.attack_surfaces) + ".")
        lines += ["## Initial Analysis", " ".join(bits), ""]

    # ## Enumeration (executed actions that produced a target response / success, in order)
    enum_lines = []
    for a in result.actions:
        verb = _FAILURE_CLASSES.get(a.result_class)
        if verb:
            continue  # failures belong in Dead Ends, not Enumeration
        enum_lines.append(f"- `{a.tool}` on `{a.target}` ({a.objective}) -> classified `{a.result_class}`.")
    if enum_lines:
        lines += ["## Enumeration"] + enum_lines + [""]

    # ## Hypothesis (supported hypotheses)
    supported = [h for h in result.key_hypotheses if h.status == "SUPPORTED"]
    if supported:
        lines += ["## Hypothesis"]
        for h in supported:
            lines.append(f"- {h.statement}")
        lines.append("")

    # ## Exploitation (actions bound to supported hypotheses + grounded observation snippet)
    exploit_actions = [a for a in result.actions if not _FAILURE_CLASSES.get(a.result_class)]
    if supported and exploit_actions:
        lines += ["## Exploitation"]
        for a in exploit_actions:
            lines.append(f"I ran `{a.tool}` against `{a.target}` to {a.objective.lower()}.")
        snippet = _grounded_flag_snippet(result.verified_flag, obs_texts)
        if snippet:
            lines.append(f"The response included `{snippet}`, which contained the flag.")
        lines.append("")

    # ## Dead Ends (blocked/failed tests + unresolved/disproven hypotheses, correctly labeled)
    dead = []
    for a in result.actions:
        verb = _FAILURE_CLASSES.get(a.result_class)
        if verb:
            dead.append(f"- `{a.tool}` on `{a.target}` {verb} (`{a.result_class}`) — not a disproof of the approach.")
    for h in result.key_hypotheses:
        if h.status == "DISPROVEN":
            dead.append(f"- Hypothesis \"{h.statement}\" was disproven by authoritative evidence.")
        elif h.status == "UNRESOLVED":
            dead.append(f"- Hypothesis \"{h.statement}\" remained unresolved.")
    if dead:
        lines += ["## Dead Ends"] + dead + [""]

    # ## Verification
    if result.final_verification_method:
        n = len(result.verification_evidence_ids)
        lines += ["## Verification",
                  f"The flag was accepted via {result.final_verification_method} "
                  f"(bound to {n} evidence record{'s' if n != 1 else ''}).", ""]

    # ## Flag
    lines += ["## Flag", f"`{result.verified_flag}`", ""]

    markdown = "\n".join(lines).strip() + "\n"
    errors = validate_writeup(markdown, result, session_journal, observations)
    return WriteupResult(markdown, grounded=not errors, errors=tuple(errors), flag=result.verified_flag)


def _grounded_flag_snippet(flag: str, obs_texts: Sequence[str]) -> str:
    for text in obs_texts:
        if flag and flag in text:
            i = text.find(flag)
            start = max(0, i - 12)
            return text[start:i + len(flag)].strip()
    return ""


def validate_writeup(
    markdown: str,
    result: SolveResult,
    session_journal: Sequence[Dict[str, Any]] = (),
    observations: Sequence[Dict[str, Any]] = (),
) -> List[str]:
    """Return a list of grounding violations (empty == grounded). Never mutates anything."""
    errors: List[str] = []
    if result.status is not SolveStatus.SOLVED:
        return ["writeup produced for a non-SOLVED result"]

    grounded_tools = {a.tool for a in result.actions}
    grounded_tools |= {str(j.get("execution_adapter")) for j in session_journal if j.get("execution_adapter")}
    grounded_targets = {a.target for a in result.actions}
    obs_texts = [str(o.get("output", "")) for o in observations]

    # every backticked `tool`-on-`target` claim must be grounded
    for tool, target in re.findall(r"`([^`]+)` on `([^`]+)`", markdown):
        if tool not in grounded_tools:
            errors.append(f"ungrounded tool referenced: {tool!r}")
        if target not in grounded_targets:
            errors.append(f"ungrounded target referenced: {target!r}")
    for tool in re.findall(r"I ran `([^`]+)` against `([^`]+)`", markdown):
        if tool[0] not in grounded_tools:
            errors.append(f"ungrounded tool referenced: {tool[0]!r}")
        if tool[1] not in grounded_targets:
            errors.append(f"ungrounded target referenced: {tool[1]!r}")

    # the ## Flag must be exactly the authoritative verified flag
    m = re.search(r"##\s*Flag\s*\n`([^`]*)`", markdown)
    if not m or m.group(1) != result.verified_flag:
        errors.append("flag in writeup does not equal SolveResult.verified_flag")

    # no OTHER flag-shaped string may be presented as the flag inside Exploitation/Flag
    for candidate in _FLAGISH.findall(markdown):
        if candidate != result.verified_flag and _looks_like_flag_claim(markdown, candidate):
            errors.append(f"writeup presents a non-authoritative flag-like value: {candidate!r}")

    # any quoted observation snippet must exist in a recorded observation
    for snippet in re.findall(r"The response included `([^`]+)`", markdown):
        if not any(snippet in t for t in obs_texts):
            errors.append(f"ungrounded observation snippet: {snippet!r}")

    return errors


def _looks_like_flag_claim(markdown: str, value: str) -> bool:
    # Only treat a flag-shaped value as a "flag claim" if it appears in the Flag section line.
    m = re.search(r"##\s*Flag\s*\n`([^`]*)`", markdown)
    return bool(m and m.group(1) == value)
