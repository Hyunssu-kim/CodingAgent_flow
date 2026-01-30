from pathlib import Path
from .prompt_registry import PromptRegistry
from .rag_retriever import RAGRetriever
from .memory_manager import MemoryManager
from .llm_gateway import LLMGateway
from .mcp_client import MCPClient
from .agent_loop import AgentLoop
from ..storage.vector_db import VectorDB
from ..config import settings

vector_db = VectorDB()
prompt_registry = PromptRegistry()
rag_retriever = RAGRetriever(vector_db)
memory_manager = MemoryManager()
llm_gateway = LLMGateway()
mcp_client = MCPClient(settings.mcp_server_url, timeout_s=settings.mcp_timeout_s)
agent_loop = AgentLoop(
    prompt_registry, rag_retriever, memory_manager, llm_gateway, mcp_client
)


def _load_design_docs() -> list[str]:
    root = Path(__file__).resolve().parents[3]
    docs_dir = root / "docs"
    docs = []
    for name in ["ARCHITECTURE.md", "CODING_RULES.md", "API_CONTRACT.md"]:
        path = docs_dir / name
        if path.exists():
            content = path.read_text(encoding="utf-8")
            docs.append(f"SOURCE:{name}\n{content}")
    return docs


docs = _load_design_docs()
if docs:
    rag_retriever.ingest_docs(docs)
