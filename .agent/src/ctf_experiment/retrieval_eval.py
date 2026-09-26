"""Independent retrieval-quality evaluation for the knowledge retrieval layer.

Two complementary measurements:

1. Labeled precision@k / recall@k / MRR against an explicit relevance set. This is the
   rigorous, non-circular measurement (used with a controlled synthetic corpus whose
   relevant/irrelevant documents are known).

2. Category-consistency@k over an arbitrary store: the fraction of a query's top-k results
   whose extracted category matches the query's target category. This is a descriptive
   quality signal for the real writeups corpus, not a ground-truth relevance metric.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from ctf_ingest.retrieval import KnowledgeRetriever, RetrievalQuery


@dataclass(frozen=True)
class LabeledQuery:
    query_id: str
    query: RetrievalQuery
    relevant_ids: Tuple[str, ...]


@dataclass(frozen=True)
class PerQueryResult:
    query_id: str
    precision_at_k: float
    recall_at_k: float
    reciprocal_rank: float
    retrieved_ids: Tuple[str, ...]


@dataclass(frozen=True)
class RetrievalQualityReport:
    k: int
    mean_precision_at_k: float
    mean_recall_at_k: float
    mean_reciprocal_rank: float
    per_query: Tuple[PerQueryResult, ...] = ()

    def to_dict(self) -> Dict[str, object]:
        return {
            "k": self.k,
            "mean_precision_at_k": round(self.mean_precision_at_k, 4),
            "mean_recall_at_k": round(self.mean_recall_at_k, 4),
            "mean_reciprocal_rank": round(self.mean_reciprocal_rank, 4),
            "per_query": [
                {
                    "query_id": q.query_id,
                    "precision_at_k": round(q.precision_at_k, 4),
                    "recall_at_k": round(q.recall_at_k, 4),
                    "reciprocal_rank": round(q.reciprocal_rank, 4),
                    "retrieved_ids": list(q.retrieved_ids),
                }
                for q in self.per_query
            ],
        }


def evaluate_retrieval(
    retriever: KnowledgeRetriever, queries: Sequence[LabeledQuery], k: int = 5
) -> RetrievalQualityReport:
    per_query: List[PerQueryResult] = []
    for labeled in queries:
        results = retriever.retrieve(labeled.query, k=k)
        retrieved_ids = tuple(r.record.record_id for r in results)
        relevant = set(labeled.relevant_ids)
        hits = [rid for rid in retrieved_ids if rid in relevant]
        precision = len(hits) / len(retrieved_ids) if retrieved_ids else 0.0
        recall = len(set(hits)) / len(relevant) if relevant else 0.0
        reciprocal = 0.0
        for rank, rid in enumerate(retrieved_ids, start=1):
            if rid in relevant:
                reciprocal = 1.0 / rank
                break
        per_query.append(
            PerQueryResult(
                query_id=labeled.query_id,
                precision_at_k=precision,
                recall_at_k=recall,
                reciprocal_rank=reciprocal,
                retrieved_ids=retrieved_ids,
            )
        )
    return RetrievalQualityReport(
        k=k,
        mean_precision_at_k=statistics.mean(q.precision_at_k for q in per_query) if per_query else 0.0,
        mean_recall_at_k=statistics.mean(q.recall_at_k for q in per_query) if per_query else 0.0,
        mean_reciprocal_rank=statistics.mean(q.reciprocal_rank for q in per_query) if per_query else 0.0,
        per_query=tuple(per_query),
    )


def category_consistency_at_k(
    retriever: KnowledgeRetriever,
    category_queries: Sequence[RetrievalQuery],
    k: int = 5,
) -> Dict[str, object]:
    """Descriptive: fraction of top-k results whose category matches each query's category."""
    per_query: List[Dict[str, object]] = []
    scores: List[float] = []
    for query in category_queries:
        results = retriever.retrieve(query, k=k)
        if not results:
            per_query.append({"category": query.category, "retrieved": 0, "consistency": 0.0})
            scores.append(0.0)
            continue
        matches = sum(
            1 for r in results if (r.record.metadata.category or "").lower() == query.category.lower()
        )
        consistency = matches / len(results)
        scores.append(consistency)
        per_query.append(
            {"category": query.category, "retrieved": len(results), "consistency": round(consistency, 4)}
        )
    return {
        "k": k,
        "mean_category_consistency": round(statistics.mean(scores), 4) if scores else 0.0,
        "per_query": per_query,
    }
