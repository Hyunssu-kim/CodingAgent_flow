from ..config import settings
from ..models.report import QualityReport
from ..models.run import RunRequest, RunResponse
from .llm_gateway import LLMGateway
from .memory_manager import MemoryManager
from .prompt_registry import PromptRegistry
from .rag_retriever import RAGRetriever
from .mcp_client import MCPClient


class AgentLoop:
    def __init__(
        self,
        prompt_registry: PromptRegistry,
        rag_retriever: RAGRetriever,
        memory_manager: MemoryManager,
        llm_gateway: LLMGateway,
        mcp_client: MCPClient,
    ) -> None:
        self.prompt_registry = prompt_registry
        self.rag_retriever = rag_retriever
        self.memory_manager = memory_manager
        self.llm_gateway = llm_gateway
        self.mcp_client = mcp_client

    def run(self, request: RunRequest) -> RunResponse:
        prompt = self.prompt_registry.get(request.task_type, "v1")
        if not prompt:
            raise ValueError(f"Prompt not found for type={request.task_type}")

        retrieved = self.rag_retriever.retrieve(request.user_input, k=settings.top_k)
        snapshot = self.memory_manager.update(request.project_id, retrieved)

        formatted_prompt = prompt.template.format(
            memory=snapshot.summary,
            context="\n".join(retrieved),
            input=request.user_input,
        )
        llm_output = self.llm_gateway.generate(formatted_prompt, request.options)

        quality_report = self._run_quality_tools(llm_output)

        return RunResponse(
            llm_output=llm_output,
            memory_snapshot=snapshot.summary,
            retrieved_context=retrieved,
            quality_report=quality_report,
        )

    def _run_quality_tools(self, code: str) -> QualityReport:
        extracted_code, extracted_tests = self._extract_code_blocks(code)
        payload = {"code": extracted_code, "tests": extracted_tests}
        lint = self.mcp_client.run_tool("lint", payload)
        test = self.mcp_client.run_tool("test", payload)
        coverage = self.mcp_client.run_tool("coverage", payload)
        return QualityReport(lint=lint, test=test, coverage=coverage)

    def _extract_code_blocks(self, text: str) -> tuple[str, str]:
        import re

        blocks = re.findall(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
        if not blocks:
            return text, ""
        code = blocks[0].strip()
        tests = blocks[1].strip() if len(blocks) > 1 else ""
        return code, tests
