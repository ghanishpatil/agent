from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Tuple

from ..context import ChallengeMetadata
from .contracts import (
    ChallengeInput,
    ChallengeResource,
    ChallengeUnderstanding,
    InputFact,
    InputFactState,
)


_CATEGORY_INDICATORS = (
    ("web", ("http", "url", "endpoint", "cookie", "jwt", "sql", "template", "api")),
    ("crypto", ("cipher", "encrypt", "rsa", "xor", "nonce", "signature", "modulus")),
    ("pwn", ("overflow", "format string", "heap", "rop", "libc", "gets(")),
    ("reverse", ("crackme", "disassemble", "decompile", "bytecode", "executable", "elf")),
    ("forensics", ("pcap", "memory dump", "metadata", "exif", "stego", "disk", "carve")),
)

_EXTENSION_CATEGORY = {
    ".pcap": "forensics",
    ".pcapng": "forensics",
    ".png": "forensics",
    ".jpg": "forensics",
    ".jpeg": "forensics",
    ".pdf": "forensics",
    ".apk": "reverse",
    ".exe": "reverse",
    ".elf": "reverse",
    ".so": "reverse",
    ".zip": "forensics",
}


def validate_challenge_input(
    challenge: ChallengeInput, resources: Tuple[ChallengeResource, ...]
) -> Tuple[str, ...]:
    errors = []
    if not any((challenge.name, challenge.description, challenge.urls, resources)):
        errors.append("challenge requires at least a name, description, URL, or resource")
    if challenge.points is not None and challenge.points < 0:
        errors.append("points must be non-negative")
    if challenge.solves is not None and challenge.solves < 0:
        errors.append("solves must be non-negative")
    if challenge.attempt_limit is not None and challenge.attempt_limit < 0:
        errors.append("attempt_limit must be non-negative")
    seen = set()
    for resource in resources:
        if not resource.resource_id.strip():
            errors.append("resource_id must be non-empty")
        if resource.resource_id in seen:
            errors.append(f"duplicate resource_id: {resource.resource_id}")
        seen.add(resource.resource_id)
        if resource.path is None and resource.content is None:
            errors.append(f"resource {resource.resource_id} requires path or content")
    return tuple(errors)


def understand_challenge(
    challenge: ChallengeInput, resource_paths: Tuple[str, ...]
) -> ChallengeUnderstanding:
    category, category_state, category_origin = _category(challenge, resource_paths)
    name = (challenge.name or "").strip()
    facts = (
        _fact("name", name or "unnamed-challenge", InputFactState.KNOWN if name else InputFactState.ASSUMED, "challenge" if name else "default label"),
        _fact("category", category, category_state, category_origin),
        _optional_fact("description", challenge.description, "challenge"),
        _optional_fact("points", challenge.points, "challenge"),
        _optional_fact("solves", challenge.solves, "challenge"),
        _optional_fact("flag_format", challenge.flag_format, "challenge"),
        _fact("urls", challenge.urls, InputFactState.KNOWN if challenge.urls else InputFactState.UNKNOWN, "challenge"),
        _fact("resources", resource_paths, InputFactState.KNOWN if resource_paths else InputFactState.UNKNOWN, "supplied resources"),
        _fact("credentials", tuple(sorted(challenge.credentials)), InputFactState.KNOWN if challenge.credentials else InputFactState.UNKNOWN, "challenge-supplied credentials"),
        _optional_fact("attempt_limit", challenge.attempt_limit, "challenge"),
    )
    attack_surfaces = []
    if challenge.urls:
        attack_surfaces.append("remote HTTP target")
    for path in resource_paths:
        attack_surfaces.append(f"local artifact:{Path(path).name}")
    unknowns = tuple(fact.name for fact in facts if fact.state is InputFactState.UNKNOWN)
    likely = (category,) if category != "misc" else ()
    return ChallengeUnderstanding(
        facts=facts,
        likely_categories=likely,
        attack_surfaces=tuple(attack_surfaces),
        unknowns=unknowns,
        constraints=challenge.known_constraints,
    )


def to_metadata(
    challenge: ChallengeInput,
    understanding: ChallengeUnderstanding,
    resource_paths: Tuple[str, ...],
) -> ChallengeMetadata:
    return ChallengeMetadata(
        name=str(understanding.fact("name").value),
        category=str(understanding.fact("category").value),
        points=challenge.points or 0,
        solves=challenge.solves or 0,
        description=challenge.description or "",
        hints=challenge.hints,
        flag_format=challenge.flag_format or "",
        files=resource_paths,
        urls=challenge.urls,
    )


def _category(
    challenge: ChallengeInput, resource_paths: Tuple[str, ...]
) -> Tuple[str, InputFactState, str]:
    if challenge.category and challenge.category.strip():
        return challenge.category.strip().lower(), InputFactState.KNOWN, "challenge"
    corpus = " ".join((challenge.description or "", *challenge.hints)).lower()
    scores = []
    for category, indicators in _CATEGORY_INDICATORS:
        score = sum(1 for indicator in indicators if indicator in corpus)
        scores.append((score, category))
    for path in resource_paths:
        inferred = _EXTENSION_CATEGORY.get(Path(path).suffix.lower())
        if inferred:
            scores.append((2, inferred))
    score, category = max(scores, default=(0, "misc"))
    if score:
        return category, InputFactState.INFERRED, "description/resource indicators"
    return "misc", InputFactState.UNKNOWN, "no category evidence"


def _fact(name: str, value, state: InputFactState, origin: str) -> InputFact:
    return InputFact(name=name, value=value, state=state, origin=origin)


def _optional_fact(name: str, value, origin: str) -> InputFact:
    return _fact(
        name,
        value,
        InputFactState.KNOWN if value is not None and value != "" else InputFactState.UNKNOWN,
        origin if value is not None and value != "" else "not supplied",
    )
