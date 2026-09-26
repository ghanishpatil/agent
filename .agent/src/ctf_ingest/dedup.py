"""Deduplication: exact (content hash) and near-duplicate (token Jaccard shingling)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

_TOKEN = re.compile(r"[a-z0-9]{3,}")


def tokenize(text: str) -> Set[str]:
    return set(_TOKEN.findall(text.lower()))


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


@dataclass
class DedupDecision:
    is_duplicate: bool
    duplicate_of: Optional[str]
    similarity: float
    reason: str


class Deduplicator:
    """Tracks accepted records; flags exact and near duplicates.

    - Exact: identical content hash.
    - Near: token Jaccard >= ``near_threshold`` against any accepted record.
    """

    def __init__(self, near_threshold: float = 0.9) -> None:
        self.near_threshold = near_threshold
        self._by_hash: Dict[str, str] = {}
        self._tokens: List[Tuple[str, Set[str]]] = []

    def evaluate(self, record_id: str, content_hash: str, text: str) -> DedupDecision:
        if content_hash in self._by_hash:
            return DedupDecision(True, self._by_hash[content_hash], 1.0, "exact content hash")
        tokens = tokenize(text)
        best_id: Optional[str] = None
        best_sim = 0.0
        for other_id, other_tokens in self._tokens:
            sim = jaccard(tokens, other_tokens)
            if sim > best_sim:
                best_sim = sim
                best_id = other_id
        if best_id is not None and best_sim >= self.near_threshold:
            return DedupDecision(True, best_id, round(best_sim, 3), "near-duplicate token overlap")
        return DedupDecision(False, None, round(best_sim, 3), "unique")

    def accept(self, record_id: str, content_hash: str, text: str) -> None:
        self._by_hash.setdefault(content_hash, record_id)
        self._tokens.append((record_id, tokenize(text)))
