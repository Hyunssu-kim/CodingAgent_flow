# Demo Guide

This guide helps you produce a clean portfolio demo using the Run Console UI and the Ops Dashboard.

## 1) Start services
Terminal A (Orchestrator)
```
.\.venv\Scripts\python -m uvicorn apps.orchestrator.main:app --reload --port 8080
```

Terminal B (MCP Tool Server)
```
.\.venv\Scripts\python -m uvicorn services.mcp_server.server:app --reload --port 8090
```

## 2) Open UI
Navigate to `http://localhost:8080/ui`.

## 3) Run demo scenarios
Use the payloads in `examples/demo_requests.json`.

Recommended sequence:
1. Code generation
2. Refactoring
3. Code review

## 4) Capture screenshots
Suggested shots for portfolio:
1. Run Console with filled request
2. Quality Report + Memory Snapshot
3. Ops Dashboard with Run History + Prompt Registry + Memory Stats

## 5) CLI demo (optional)
You can use the PowerShell helper:
```
.\scripts\demo_requests.ps1
```

## Notes
- The system uses a stub LLM unless you set `LLM_PROVIDER=gemini` and `LLM_API_KEY` in `.env`.
- The demo is safe to run offline. Quality tools execute locally via MCP.
