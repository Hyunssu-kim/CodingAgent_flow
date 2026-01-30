from typing import List
from ..storage.vector_db import VectorDB


class RAGRetriever:
    def __init__(self, vector_db: VectorDB) -> None:
        self.vector_db = vector_db

    def ingest_docs(self, docs: List[str]) -> None:
        chunks = self._chunk_docs(docs)
        for chunk in chunks:
            embedding = self._embed(chunk)
            self.vector_db.upsert(chunk, embedding)

    def retrieve(self, query: str, k: int = 3) -> List[str]:
        q_emb = self._embed(query)
        return self.vector_db.search(q_emb, top_k=k)

    def _chunk_docs(self, docs: List[str]) -> List[str]:
        chunks: List[str] = []
        for doc in docs:
            source = None
            lines = doc.splitlines()
            if lines and lines[0].startswith("SOURCE:"):
                source = lines[0].replace("SOURCE:", "").strip()
                doc_body = "\n".join(lines[1:]).strip()
            else:
                doc_body = doc

            for paragraph in doc_body.split("\n\n"):
                p = paragraph.strip()
                if not p:
                    continue
                if source:
                    chunks.append(f"[{source}] {p}")
                else:
                    chunks.append(p)
        return chunks

    def _embed(self, text: str) -> List[float]:
        # Placeholder embedding: deterministic hash-based vector.
        # Replace with real embedding model in production.
        seed = abs(hash(text)) % 1000
        return [(seed + i) / 1000.0 for i in range(16)]
