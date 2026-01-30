from typing import List, Tuple


class VectorDB:
    def __init__(self) -> None:
        self._rows: List[Tuple[str, List[float]]] = []

    def upsert(self, text: str, embedding: List[float]) -> None:
        self._rows.append((text, embedding))

    def search(self, query_embedding: List[float], top_k: int = 3) -> List[str]:
        scored = []
        for text, emb in self._rows:
            score = self._dot(query_embedding, emb)
            scored.append((score, text))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [text for _, text in scored[:top_k]]

    def _dot(self, a: List[float], b: List[float]) -> float:
        size = min(len(a), len(b))
        return sum(a[i] * b[i] for i in range(size))
