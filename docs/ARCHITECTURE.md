# Architecture

## System Overview
The system provides a Design-Aware AI Coding Platform that keeps project design documents in memory via RAG and runs code quality checks through a separate MCP Tool Server. The FastAPI Orchestrator manages prompt templates, retrieval, memory snapshots, and LLM calls. The MCP Tool Server executes lint, test, and coverage tools and returns structured JSON reports.

Key responsibilities:
- **FastAPI Orchestrator**: prompt registry, RAG retriever, memory snapshot updates, agent loop, LLM gateway, MCP client.
- **MCP Tool Server**: lint/test/coverage execution in an isolated service.
- **Run Store**: persists run history and exposes ops stats.
- **UI**: minimal run console for submitting tasks and viewing outputs.

## Component Diagram (ASCII)
```
+-------------------+       +------------------------+
|       UI          |       |   MCP Tool Server      |
| (Run Console)     |       |  /tool/lint|test|cov   |
+---------+---------+       +------------+-----------+
          |                              ^
          v                              |
+-------------------+    HTTP JSON       |
| FastAPI Orchestr. |--------------------+
| - Prompt Registry |
| - RAG Retriever   |
| - Memory Manager  |
| - LLM Gateway     |
| - MCP Client      |
+---------+---------+
          |
          v
+-------------------+
| Design Docs (RAG) |
| ARCH/CODING/API   |
+-------------------+
```

## Data Flow
1) **User Request** arrives at `/run` with task type + input text.
2) **RAG Retrieval** searches design docs for top-k relevant paragraphs.
3) **Memory Snapshot Update** summarizes retrieved context for persistence.
4) **Prompt Assembly** combines role/constraints/schema + memory + context.
5) **LLM Call** generates candidate output.
6) **MCP Tools** run lint/test/coverage on generated code and return JSON.
7) **Run Store** persists the run metadata for ops visibility.
8) **Response** returns LLM output + memory snapshot + retrieved context + quality report.

## Technology Stack
- **Backend**: Python 3.11+, FastAPI
- **RAG**: Simple vector store (MVP), extensible to Chroma/FAISS
- **LLM Gateway**: Stubbed in MVP, pluggable
- **MCP Server**: FastAPI + subprocess for lint/test/coverage
- **Quality Tools**: ruff, pytest, coverage.py
- **UI**: HTML/CSS/JS (minimal)

## Deployment Architecture
- **Local Dev**: Two processes
  - Orchestrator: `uvicorn apps.orchestrator.main:app --port 8080`
  - MCP Server: `uvicorn services.mcp_server.server:app --port 8090`
- **Production**: Two services (Docker or separate VM/containers)
  - Orchestrator (API gateway)
  - MCP Tool Server (isolated execution environment)
- **Scaling**: Orchestrator can scale horizontally; MCP server scales independently by queueing tool jobs.
