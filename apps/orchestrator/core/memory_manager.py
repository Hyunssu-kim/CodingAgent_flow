from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from ..models.memory import MemoryContext, MemoryHistoryItem, MemorySnapshot, MemoryStats


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _safe_project_id(project_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", project_id) or "default"


def _extract_source(text: str, default_source: str) -> tuple[str, str]:
    match = re.match(r"^\\[(.+?)\\]\\s+(.*)$", text.strip(), re.DOTALL)
    if match:
        source = match.group(1).strip()
        content = match.group(2).strip()
        return source, content
    return default_source, text.strip()


@dataclass
class _MemoryEntry:
    id: str
    content: str
    source: str
    first_seen: datetime
    last_seen: datetime
    frequency: int = 0

    def to_model(self, importance: float) -> MemoryContext:
        return MemoryContext(
            id=self.id,
            content=self.content,
            source=self.source,
            first_seen=self.first_seen,
            last_seen=self.last_seen,
            frequency=self.frequency,
            importance=importance,
        )


@dataclass
class _ProjectState:
    project_id: str
    entries: Dict[str, _MemoryEntry] = field(default_factory=dict)
    history: List[MemoryHistoryItem] = field(default_factory=list)
    updated_at: datetime = field(default_factory=_utcnow)


class MemoryManager:
    def __init__(self, store_dir: str = "./data/memory", history_limit: int = 50, top_k: int = 5) -> None:
        self._store_dir = Path(store_dir)
        self._history_limit = history_limit
        self._top_k = top_k
        self._states: Dict[str, _ProjectState] = {}
        self._store_dir.mkdir(parents=True, exist_ok=True)

    def get(self, project_id: str) -> MemorySnapshot:
        state = self._load(project_id)
        snapshot = self._build_snapshot(state)
        state.updated_at = snapshot.updated_at
        self._save(state)
        return snapshot

    def update(self, project_id: str, retrieved_context: List[str], source: str = "rag") -> MemorySnapshot:
        state = self._load(project_id)
        now = _utcnow()

        contexts: List[MemoryContext] = []
        for text in retrieved_context:
            src, cleaned = _extract_source(text, source)
            if not cleaned:
                continue
            key = _normalize(cleaned)
            entry = state.entries.get(key)
            if not entry:
                entry = _MemoryEntry(
                    id=f"ctx_{abs(hash(key))}",
                    content=cleaned,
                    source=src,
                    first_seen=now,
                    last_seen=now,
                    frequency=0,
                )
                state.entries[key] = entry
            entry.frequency += 1
            entry.last_seen = now
            contexts.append(entry.to_model(importance=0.0))

        if contexts:
            state.history.insert(0, MemoryHistoryItem(ts=now, contexts=contexts))
            state.history = state.history[: self._history_limit]

        snapshot = self._build_snapshot(state)
        state.updated_at = snapshot.updated_at
        self._save(state)
        return snapshot

    def get_history(self, project_id: str) -> List[MemoryHistoryItem]:
        state = self._load(project_id)
        return state.history

    def delete(self, project_id: str) -> bool:
        pid = _safe_project_id(project_id)
        if pid in self._states:
            del self._states[pid]
        path = self._project_path(pid)
        if path.exists():
            path.unlink()
            return True
        return False

    def stats(self) -> MemoryStats:
        self._load_all()
        latest: Optional[datetime] = None
        total_entries = 0
        total_history = 0
        for state in self._states.values():
            total_entries += len(state.entries)
            total_history += len(state.history)
            if latest is None or state.updated_at > latest:
                latest = state.updated_at
        return MemoryStats(
            project_count=len(self._states),
            total_entries=total_entries,
            total_history_items=total_history,
            latest_update=latest,
        )

    def _build_snapshot(self, state: _ProjectState) -> MemorySnapshot:
        now = _utcnow()
        entries = list(state.entries.values())
        if not entries:
            return MemorySnapshot(project_id=state.project_id, summary="(empty)", updated_at=now, top_contexts=[])

        max_freq = max(e.frequency for e in entries) or 1
        scored: List[MemoryContext] = []
        for entry in entries:
            age_seconds = (now - entry.last_seen).total_seconds()
            recency = max(0.0, 1.0 - (age_seconds / (7 * 24 * 3600)))
            freq_norm = entry.frequency / max_freq
            importance = round(0.6 * freq_norm + 0.4 * recency, 3)
            scored.append(entry.to_model(importance=importance))

        scored.sort(key=lambda x: x.importance, reverse=True)
        top_contexts = scored[: self._top_k]

        recent = self._recent_unique_contexts(state.history, limit=self._top_k)
        if recent:
            bullets = "\n".join([f"- [{c.source}] {c.content[:200]}" for c in recent])
            summary = f"Memory Snapshot (recent/high-signal):\n{bullets}"
        else:
            summary = "(empty)"

        return MemorySnapshot(
            project_id=state.project_id,
            summary=summary,
            updated_at=now,
            top_contexts=top_contexts,
        )

    def _recent_unique_contexts(
        self, history: List[MemoryHistoryItem], limit: int = 5
    ) -> List[MemoryContext]:
        seen: set[str] = set()
        result: List[MemoryContext] = []
        for item in history:
            for ctx in item.contexts:
                key = _normalize(ctx.content)
                if key in seen:
                    continue
                seen.add(key)
                result.append(ctx)
                if len(result) >= limit:
                    return result
        return result

    def _project_path(self, project_id: str) -> Path:
        pid = _safe_project_id(project_id)
        return self._store_dir / f"{pid}.json"

    def _load(self, project_id: str) -> _ProjectState:
        pid = _safe_project_id(project_id)
        if pid in self._states:
            return self._states[pid]
        path = self._project_path(pid)
        if not path.exists():
            state = _ProjectState(project_id=pid)
            self._states[pid] = state
            return state

        raw = json.loads(path.read_text(encoding="utf-8"))
        entries: Dict[str, _MemoryEntry] = {}
        for key, e in raw.get("entries", {}).items():
            entries[key] = _MemoryEntry(
                id=e["id"],
                content=e["content"],
                source=e.get("source", "rag"),
                first_seen=datetime.fromisoformat(e["first_seen"]),
                last_seen=datetime.fromisoformat(e["last_seen"]),
                frequency=e.get("frequency", 1),
            )

        history: List[MemoryHistoryItem] = []
        for h in raw.get("history", []):
            contexts = [
                MemoryContext(
                    id=c["id"],
                    content=c["content"],
                    source=c.get("source", "rag"),
                    first_seen=datetime.fromisoformat(c["first_seen"]),
                    last_seen=datetime.fromisoformat(c["last_seen"]),
                    frequency=c.get("frequency", 1),
                    importance=c.get("importance", 0.0),
                )
                for c in h.get("contexts", [])
            ]
            history.append(MemoryHistoryItem(ts=datetime.fromisoformat(h["ts"]), contexts=contexts))

        updated_at = datetime.fromisoformat(raw.get("updated_at")) if raw.get("updated_at") else _utcnow()
        state = _ProjectState(project_id=pid, entries=entries, history=history, updated_at=updated_at)
        self._states[pid] = state
        return state

    def _load_all(self) -> None:
        for path in self._store_dir.glob("*.json"):
            pid = path.stem
            if pid not in self._states:
                self._load(pid)

    def _save(self, state: _ProjectState) -> None:
        payload = {
            "project_id": state.project_id,
            "updated_at": state.updated_at.isoformat(),
            "entries": {
                key: {
                    "id": entry.id,
                    "content": entry.content,
                    "source": entry.source,
                    "first_seen": entry.first_seen.isoformat(),
                    "last_seen": entry.last_seen.isoformat(),
                    "frequency": entry.frequency,
                }
                for key, entry in state.entries.items()
            },
            "history": [
                {
                    "ts": item.ts.isoformat(),
                    "contexts": [
                        {
                            "id": ctx.id,
                            "content": ctx.content,
                            "source": ctx.source,
                            "first_seen": ctx.first_seen.isoformat(),
                            "last_seen": ctx.last_seen.isoformat(),
                            "frequency": ctx.frequency,
                            "importance": ctx.importance,
                        }
                        for ctx in item.contexts
                    ],
                }
                for item in state.history
            ],
        }
        path = self._project_path(state.project_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
