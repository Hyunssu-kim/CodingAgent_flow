# Design-Aware AI Coding Platform (MVP)

A lightweight AI coding platform that keeps design documents in context (RAG), runs quality tools via an MCP Tool Server, and provides an operations dashboard for prompts, memory, and run history.

## Highlights
- Prompt + context engineering (design docs + memory snapshot)
- RAG retrieval over design documents
- MCP Tool Server for lint/test/coverage execution
- Run history storage and management APIs
- Minimal management UI (run console + ops dashboard)

## Architecture
```
+-------------------+       +------------------------+
|       UI          |       |   MCP Tool Server      |
| (Ops Console)     |       |  /tool/lint|test|cov   |
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
| - Run Store       |
+---------+---------+
          |
          v
+-------------------+
| Design Docs (RAG) |
| ARCH/CODING/API   |
+-------------------+
```

## Quickstart
### 1) Create venv
```
python -m venv .venv
```

### 2) Install dependencies
```
.\.venv\Scripts\python -m pip install -r requirements.txt
```

### 3) Configure env
```
copy .env.example .env
```

### 4) Run services (two terminals)
Orchestrator
```
.\.venv\Scripts\python -m uvicorn apps.orchestrator.main:app --reload --port 8080
```

MCP Tool Server
```
.\.venv\Scripts\python -m uvicorn services.mcp_server.server:app --reload --port 8090
```

## API
### POST /run
```
{
  "task_type": "code_generation",
  "user_input": "Implement a safe file reader",
  "project_id": "default",
  "options": {}
}
```

Response (sample)
```
{
  "llm_output": "...",
  "memory_snapshot": "Memory Snapshot: ...",
  "retrieved_context": ["..."],
  "quality_report": {
    "lint": {"status": "ok", "detail": {"count": 0, "violations": []}},
    "test": {"status": "passed", "detail": {"summary": {"passed": 1}}},
    "coverage": {"status": "ok", "detail": {"coverage_percent": 95.0}}
  },
  "run_id": "...",
  "duration_ms": 123
}
```

### GET /runs
List recent runs. Optional `project_id`, `limit`.

### GET /runs/{run_id}
Retrieve a single run record.

### DELETE /runs/{run_id}
Delete a run record.

### GET /runs/stats
Aggregate stats (count by task type, latest run time).

### GET /prompts
List prompt templates.

### POST /prompts
Create a new prompt template.

### GET /memory
Fetch memory snapshot for a project.

### GET /memory/{project_id}/history
Fetch memory history.

### GET /memory/stats
Memory usage statistics.

## UI
Open `http://localhost:8080/ui` to use the run console and ops dashboard.

## Demo Assets
- Demo guide: `docs/DEMO.md`
- Example payloads: `examples/demo_requests.json`
- PowerShell demo runner: `scripts/demo_requests.ps1`

## Project Structure
```
apps/
  orchestrator/   # FastAPI orchestrator
  ui/             # management UI
services/
  mcp_server/     # MCP Tool Server
scripts/          # ingest + seed utilities
examples/         # sample scenarios
docs/             # design documents
```

## Roadmap
- Vector store integration (FAISS/Chroma)
- Auth + multi-tenant project isolation
- MCP tool sandboxing
- IDE extensions (VS Code / IntelliJ)
