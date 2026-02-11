import json
from pathlib import Path
from typing import List, Tuple


class VectorDB:
    def __init__(self, path: str | None = None) -> None:
        self._rows: List[Tuple[str, List[float]]] = []
        self._path = Path(path) if path else None
        if self._path and self._path.suffix != ".json":
            self._path = self._path / "vector_db.json"
        self._load()

    def upsert(self, text: str, embedding: List[float]) -> None:
        for idx, (stored_text, _stored_emb) in enumerate(self._rows):
            if stored_text == text:
                self._rows[idx] = (text, embedding)
                self._save()
                return
        self._rows.append((text, embedding))
        self._save()

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

    def _load(self) -> None:
        if not self._path or not self._path.exists():
            return
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return
        rows: List[Tuple[str, List[float]]] = []
        for item in payload:
            text = item.get("text")
            embedding = item.get("embedding")
            if not isinstance(text, str) or not isinstance(embedding, list):
                continue
            rows.append((text, [float(x) for x in embedding]))
        self._rows = rows

    def _save(self) -> None:
        if not self._path:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = [{"text": text, "embedding": emb} for text, emb in self._rows]
        self._path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
