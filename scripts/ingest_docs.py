import sys
from pathlib import Path
from typing import List

sys.path.append(str(Path(__file__).resolve().parents[1]))

from apps.orchestrator.core.rag_retriever import RAGRetriever
from apps.orchestrator.storage.vector_db import VectorDB

DOCS_DIR = Path(__file__).resolve().parents[1] / "docs"


def load_docs() -> List[str]:
    docs: List[str] = []
    for path in sorted(DOCS_DIR.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        docs.append(f"SOURCE:{path.name}\n{content}")
    return docs


def chunk_docs(docs: List[str]) -> List[str]:
    chunks: List[str] = []
    for doc in docs:
        for paragraph in doc.split("\n\n"):
            p = paragraph.strip()
            if p:
                chunks.append(p)
    return chunks


def main() -> None:
    if not DOCS_DIR.exists():
        print(f"Docs directory not found: {DOCS_DIR}")
        return

    docs = load_docs()
    if not docs:
        print("No .md files found in docs/")
        return

    vector_db = VectorDB()
    rag = RAGRetriever(vector_db)

    chunks = chunk_docs(docs)
    rag.ingest_docs(docs)

    total_chunks = len(chunks)
    avg_len = round(sum(len(c) for c in chunks) / total_chunks, 2) if total_chunks else 0

    print("Ingest complete.")
    print(f"- docs: {len(docs)}")
    print(f"- chunks: {total_chunks}")
    print(f"- avg_chunk_len_chars: {avg_len}")


if __name__ == "__main__":
    main()
