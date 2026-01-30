from apps.orchestrator.core.rag_retriever import RAGRetriever
from apps.orchestrator.storage.vector_db import VectorDB


def test_vector_db_search_ranking():
    db = VectorDB()
    db.upsert("low", [0.0, 0.0])
    db.upsert("mid", [0.5, 0.5])
    db.upsert("high", [1.0, 1.0])

    results = db.search([1.0, 1.0], top_k=2)
    assert results[0] == "high"
    assert "mid" in results


def test_rag_ingest_and_retrieve_with_source_tags():
    db = VectorDB()
    rag = RAGRetriever(db)
    docs = [
        "SOURCE:ARCHITECTURE.md\nTitle\n\nFirst paragraph.\n\nSecond paragraph.",
        "SOURCE:CODING_RULES.md\nRules\n\nUse type hints.",
    ]
    rag.ingest_docs(docs)

    stored_texts = [text for text, _ in db._rows]
    assert any(text.startswith("[ARCHITECTURE.md]") for text in stored_texts)
    assert any(text.startswith("[CODING_RULES.md]") for text in stored_texts)

    results = rag.retrieve("type hints", k=2)
    assert len(results) <= 2
    for item in results:
        assert item in stored_texts
