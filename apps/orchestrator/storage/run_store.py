import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..models.run_record import RunRecord, RunStats


class RunStore:
    def __init__(self, path: str = "./data/run_store.json", limit: int = 200) -> None:
        self._path = Path(path)
        if self._path.suffix != ".json":
            self._path = self._path / "run_store.json"
        self._limit = limit
        self._records: Dict[str, RunRecord] = {}
        self._load()

    def add(self, record: RunRecord) -> None:
        self._records[record.id] = record
        self._trim()
        self._save()

    def list(self, project_id: Optional[str] = None, limit: int = 50) -> List[RunRecord]:
        records = self._list_sorted()
        if project_id:
            records = [r for r in records if r.project_id == project_id]
        return records[:limit]

    def get(self, run_id: str) -> Optional[RunRecord]:
        return self._records.get(run_id)

    def delete(self, run_id: str) -> bool:
        if run_id in self._records:
            del self._records[run_id]
            self._save()
            return True
        return False

    def stats(self) -> RunStats:
        records = self._list_sorted()
        task_counts: Dict[str, int] = {}
        project_ids = set()
        latest: Optional[datetime] = None
        for record in records:
            task_counts[record.task_type] = task_counts.get(record.task_type, 0) + 1
            project_ids.add(record.project_id)
            if latest is None or record.created_at > latest:
                latest = record.created_at
        return RunStats(
            total_runs=len(records),
            project_count=len(project_ids),
            task_type_counts=task_counts,
            latest_run_at=latest,
        )

    def _list_sorted(self) -> List[RunRecord]:
        return sorted(self._records.values(), key=lambda r: r.created_at, reverse=True)

    def _trim(self) -> None:
        if len(self._records) <= self._limit:
            return
        records = self._list_sorted()[: self._limit]
        self._records = {r.id: r for r in records}

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return
        if not isinstance(payload, list):
            return
        for item in payload:
            if not isinstance(item, dict):
                continue
            created_at = item.get("created_at")
            if isinstance(created_at, str):
                try:
                    item["created_at"] = datetime.fromisoformat(created_at)
                except ValueError:
                    continue
            try:
                record = RunRecord(**item)
            except Exception:
                continue
            self._records[record.id] = record

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = [self._serialize(r) for r in self._list_sorted()]
        self._path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _serialize(record: RunRecord) -> Dict[str, object]:
        data = record.dict()
        data["created_at"] = record.created_at.isoformat()
        return data
