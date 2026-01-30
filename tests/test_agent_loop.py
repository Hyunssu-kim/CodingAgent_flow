import tempfile

from apps.orchestrator.core.agent_loop import AgentLoop
from apps.orchestrator.core.llm_gateway import LLMGateway
from apps.orchestrator.core.mcp_client import MCPClient
from apps.orchestrator.core.memory_manager import MemoryManager
from apps.orchestrator.core.prompt_registry import PromptRegistry
from apps.orchestrator.core.rag_retriever import RAGRetriever
from apps.orchestrator.models.run import RunRequest
from apps.orchestrator.storage.vector_db import VectorDB


class FakeLLM(LLMGateway):
    def generate(self, prompt: str, options: dict | None = None) -> str:
        return f"LLM_OUTPUT::{prompt[:50]}"


class FakeMCP(MCPClient):
    def __init__(self) -> None:
        super().__init__("http://fake")

    def run_tool(self, name: str, payload: dict) -> dict:
        return {"status": "ok", "detail": {"tool": name, "payload_keys": list(payload.keys())}}


def test_agent_loop_e2e():
    db = VectorDB()
    rag = RAGRetriever(db)
    rag.ingest_docs(["SOURCE:ARCHITECTURE.md\nTitle\n\nSystem overview paragraph."])

    registry = PromptRegistry()
    with tempfile.TemporaryDirectory() as tmpdir:
        memory = MemoryManager(store_dir=tmpdir, history_limit=5, top_k=3)
        agent = AgentLoop(
            prompt_registry=registry,
            rag_retriever=rag,
            memory_manager=memory,
            llm_gateway=FakeLLM(),
            mcp_client=FakeMCP(),
        )

        req = RunRequest(
            task_type="code_generation",
            user_input="Create a hello function.",
            project_id="demo",
        )
        resp = agent.run(req)

        assert resp.llm_output.startswith("LLM_OUTPUT::")
        assert resp.retrieved_context
        assert "Memory Snapshot" in resp.memory_snapshot
        assert resp.quality_report.lint["status"] == "ok"
        assert resp.quality_report.test["status"] == "ok"
        assert resp.quality_report.coverage["status"] == "ok"
