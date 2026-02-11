# Design-Aware AI Coding Platform (MVP)

A lightweight AI coding platform that keeps design documents in context (RAG), runs quality tools via an MCP Tool Server, and provides an operations dashboard for prompts, memory, and run history.

## What Works Today
- FastAPI orchestrator with `/run`, `/runs`, `/prompts`, and `/memory` APIs
- RAG over local design docs (`docs/ARCHITECTURE.md`, `docs/CODING_RULES.md`, `docs/API_CONTRACT.md`)
- Memory snapshots persisted to JSON (`data/memory/*.json`)
- MCP Tool Server for lint/test/coverage (ruff/pytest/coverage)
- Run history persisted to JSON (`data/run_store.json`) with stats endpoints
- Minimal UI for running tasks and viewing ops telemetry

## Architecture
```
+-------------------+       +------------------------+
|       UI          |       |   MCP Tool Server      |
| (Run + Ops UI)    |       |  /tool/lint|test|cov   |
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

### 5) Open UI
`http://localhost:8080/ui`

## Configuration Notes
- Default `.env` uses `LLM_PROVIDER=stub`, which echoes the prompt for offline demos.
- To call Gemini, set `LLM_PROVIDER=gemini` and `LLM_API_KEY=...`.
- MCP tools require `ruff`, `pytest`, and `coverage` installed (already in `requirements.txt`).

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
    "coverage": {"status": "ok", "detail": {"coverage_percent": 95.0, "missing_lines": []}}
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

### POST /memory/refresh
Placeholder. Returns an updated snapshot but does not re-ingest docs yet.

### GET /memory/{project_id}/history
Fetch memory history.

### DELETE /memory/{project_id}
Delete stored memory for a project.

### GET /memory/stats
Memory usage statistics.

## UI
- Run console: submit tasks and view LLM output, retrieved context, memory snapshot, quality report
- Ops dashboard: run history, prompt registry, memory stats

## Demo Assets
- Demo guide: `docs/DEMO.md`
- Example payloads: `examples/demo_requests.json`
- PowerShell demo runner: `scripts/demo_requests.ps1`

## Implementation Notes (Current Behavior)
- RAG uses a deterministic hash-based embedding (placeholder), stored in `data/vectordb/vector_db.json`.
- Design docs are ingested on startup; `/memory/refresh` does not re-ingest yet.
- The agent extracts the first fenced code block as code and the second as test cases.
- MCP tools convert JSON test cases to pytest (see `services/mcp_server/tools/testgen.py`).
- Prompt registry is in-memory; new prompts are lost on restart.

## Project Structure
```
apps/
  orchestrator/   # FastAPI orchestrator
  ui/             # management UI
services/
  mcp_server/     # MCP Tool Server
scripts/          # demo helpers
examples/         # sample scenarios
docs/             # design documents
```

## Roadmap
- Vector store integration (FAISS/Chroma)
- Auth + multi-tenant project isolation
- MCP tool sandboxing
- IDE extensions (VS Code / IntelliJ)
