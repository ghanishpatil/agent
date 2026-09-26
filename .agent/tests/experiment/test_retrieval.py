from __future__ import annotations

from pathlib import Path

from ctf_ingest import KnowledgeStore
from ctf_ingest.retrieval import KnowledgeRetriever, RetrievalQuery


def test_retrieval_ranks_relevant_category_first(labeled_corpus) -> None:
    retriever = KnowledgeRetriever.from_records(labeled_corpus)
    query = RetrievalQuery(
        text="a page renders our name with a server-side template",
        category="web",
        keywords=("template injection", "ssti"),
    )
    results = retriever.retrieve(query, k=3)
    assert results
    assert results[0].record.record_id.startswith("web-ssti")
    assert results[0].category_match
    assert results[0].score >= results[-1].score


def test_retrieval_returns_matched_terms_and_scores(labeled_corpus) -> None:
    retriever = KnowledgeRetriever.from_records(labeled_corpus)
    results = retriever.retrieve(RetrievalQuery(text="single byte xor cipher", category="crypto"), k=2)
    top = results[0]
    assert top.record.metadata.category == "crypto"
    assert "xor" in top.matched_terms
    assert top.score > 0


def test_retrieval_excludes_duplicates(labeled_corpus) -> None:
    from .conftest import make_record

    dup = make_record("web-ssti-dup", "web", "dup", duplicate_of="web-ssti-1")
    retriever = KnowledgeRetriever.from_records([*labeled_corpus, dup])
    ids = {r.record.record_id for r in retriever.retrieve(RetrievalQuery(text="template", category="web"), k=10)}
    assert "web-ssti-dup" not in ids


def test_retrieval_empty_query_returns_nothing(labeled_corpus) -> None:
    retriever = KnowledgeRetriever.from_records(labeled_corpus)
    assert retriever.retrieve(RetrievalQuery(text="", category=""), k=5) == ()


def test_retriever_rehydrates_from_store(labeled_corpus, tmp_path: Path) -> None:
    store = KnowledgeStore(tmp_path / "kstore")
    store.write(labeled_corpus)
    retriever = KnowledgeRetriever.from_store(store)
    results = retriever.retrieve(
        RetrievalQuery(text="server side template injection", category="web", keywords=("ssti",)),
        k=3,
    )
    assert results
    assert any(r.category_match for r in results)
    # Rehydrated records preserve provenance and techniques.
    assert results[0].record.provenance.document_path
    assert results[0].record.techniques
