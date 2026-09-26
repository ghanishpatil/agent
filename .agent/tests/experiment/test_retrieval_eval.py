from __future__ import annotations

from ctf_experiment.retrieval_eval import (
    LabeledQuery,
    category_consistency_at_k,
    evaluate_retrieval,
)
from ctf_ingest.retrieval import KnowledgeRetriever, RetrievalQuery


def test_labeled_precision_recall_mrr(labeled_corpus) -> None:
    retriever = KnowledgeRetriever.from_records(labeled_corpus)
    queries = [
        LabeledQuery(
            "ssti",
            RetrievalQuery(text="server side template injection jinja2", category="web", keywords=("ssti",)),
            relevant_ids=("web-ssti-1", "web-ssti-2"),
        ),
        LabeledQuery(
            "xor",
            RetrievalQuery(text="single byte xor cipher brute force", category="crypto", keywords=("xor",)),
            relevant_ids=("crypto-xor-1",),
        ),
    ]
    report = evaluate_retrieval(retriever, queries, k=3)
    # Top result for each query is relevant -> MRR should be perfect.
    assert report.mean_reciprocal_rank == 1.0
    assert report.mean_recall_at_k > 0.5
    assert 0.0 < report.mean_precision_at_k <= 1.0
    assert report.to_dict()["k"] == 3


def test_irrelevant_query_yields_zero_when_no_match(labeled_corpus) -> None:
    retriever = KnowledgeRetriever.from_records(labeled_corpus)
    q = [
        LabeledQuery(
            "nomatch",
            RetrievalQuery(text="zzzzz nonexistent topic", category="hardware"),
            relevant_ids=("web-ssti-1",),
        )
    ]
    report = evaluate_retrieval(retriever, q, k=3)
    assert report.mean_reciprocal_rank == 0.0
    assert report.mean_recall_at_k == 0.0


def test_category_consistency_descriptive_metric(labeled_corpus) -> None:
    retriever = KnowledgeRetriever.from_records(labeled_corpus)
    result = category_consistency_at_k(
        retriever,
        [
            RetrievalQuery(text="template injection sql", category="web", keywords=("web",)),
            RetrievalQuery(text="rsa xor cipher", category="crypto", keywords=("crypto",)),
        ],
        k=3,
    )
    assert 0.0 <= result["mean_category_consistency"] <= 1.0
    assert len(result["per_query"]) == 2
