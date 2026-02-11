from datetime import datetime, timezone
import tempfile
from pathlib import Path

from apps.orchestrator.models.report import QualityReport
from apps.orchestrator.models.run_record import RunRecord
from apps.orchestrator.storage.run_store import RunStore


def test_run_store_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "runs.json"
        store = RunStore(path=str(path), limit=10)

        record = RunRecord(
            id="run_1",
            task_type="code_generation",
            project_id="demo",
            user_input="Build a safe parser",
            llm_output="print('ok')",
            memory_snapshot="snapshot",
            retrieved_context=["doc chunk"],
            quality_report=QualityReport(lint={"status": "ok"}, test={"status": "ok"}, coverage={"status": "ok"}),
            created_at=datetime.now(timezone.utc),
            duration_ms=123,
        )

        store.add(record)
        assert store.get("run_1") is not None
        assert store.list(limit=5)[0].id == "run_1"

        stats = store.stats()
        assert stats.total_runs == 1
        assert stats.project_count == 1
        assert stats.task_type_counts["code_generation"] == 1

        assert store.delete("run_1") is True
        assert store.get("run_1") is None
