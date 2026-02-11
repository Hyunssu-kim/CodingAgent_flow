# API Contract

## FastAPI Orchestrator

### POST /run
Run the full agent loop.

**Request JSON**
```
{
  "task_type": "code_generation | refactoring | code_review",
  "user_input": "string",
  "project_id": "string",
  "options": { "any": "object" }
}
```

**Response JSON**
```
{
  "llm_output": "string",
  "memory_snapshot": "string",
  "retrieved_context": ["string"],
  "quality_report": {
    "lint": { "status": "ok|violations|error", "detail": {"count": 0, "violations": []} },
    "test": { "status": "passed|failed|error", "detail": {"summary": {"passed":0}} },
    "coverage": { "status": "ok|failed|error", "detail": {"coverage_percent": 0.0, "missing_lines": []} }
  },
  "run_id": "string",
  "duration_ms": 123
}
```

**Errors**
- 400: invalid task type or prompt missing
- 500: unexpected errors

---

### GET /prompts
Return all prompt templates.

**Response JSON**
```
[
  {
    "type": "code_generation",
    "version": "v1",
    "role": "string",
    "constraints": "string",
    "output_schema": "string",
    "template": "string",
    "tags": ["string"],
    "description": "string"
  }
]
```

### POST /prompts
Create a new prompt template.

**Request JSON**
```
{
  "type": "code_generation",
  "version": "v2",
  "role": "string",
  "constraints": "string",
  "output_schema": "string",
  "template": "string",
  "tags": ["string"],
  "description": "string"
}
```

**Errors**
- 409: prompt already exists

---

### GET /memory
Fetch latest memory snapshot.

**Query**
- project_id: string (optional, default: "default")

**Response JSON**
```
{
  "project_id": "string",
  "summary": "string",
  "updated_at": "2026-01-30T12:00:00Z",
  "top_contexts": [
    {
      "id": "string",
      "content": "string",
      "source": "string",
      "first_seen": "2026-01-30T12:00:00Z",
      "last_seen": "2026-01-30T12:00:00Z",
      "frequency": 1,
      "importance": 0.8
    }
  ]
}
```

### POST /memory/refresh
Refresh memory (re-ingest docs).

**Query**
- project_id: string (optional, default: "default")

**Response JSON**
```
{
  "project_id": "string",
  "summary": "string",
  "updated_at": "2026-01-30T12:00:00Z",
  "top_contexts": []
}
```

---

### GET /runs
List recent runs.

**Query**
- project_id: string (optional)
- limit: int (optional, default: 20)

**Response JSON**
```
[
  {
    "id": "string",
    "task_type": "code_generation|refactoring|code_review",
    "project_id": "string",
    "user_input": "string",
    "llm_output": "string",
    "memory_snapshot": "string",
    "retrieved_context": ["string"],
    "quality_report": {},
    "created_at": "2026-01-30T12:00:00Z",
    "duration_ms": 123
  }
]
```

### GET /runs/{run_id}
Get a single run record.

### DELETE /runs/{run_id}
Delete a run record.

### GET /runs/stats
Run statistics by task type.

**Response JSON**
```
{
  "total_runs": 10,
  "project_count": 2,
  "task_type_counts": {"code_generation": 7},
  "latest_run_at": "2026-01-30T12:00:00Z"
}
```

---

## MCP Tool Server

### POST /tool/lint
Run Ruff linting.

**Request JSON**
```
{
  "payload": {
    "code": "string",
    "tests": "string (optional, JSON test cases or pytest code)"
  }
}
```

**Response JSON**
```
{
  "status": "ok|violations|error",
  "detail": {
    "count": 0,
    "violations": [
      {
        "code": "E501",
        "message": "line too long",
        "file": "generated.py",
        "line": 10,
        "column": 1,
        "severity": "warning"
      }
    ]
  }
}
```

### POST /tool/test
Run pytest.

**Request JSON**
```
{
  "payload": {
    "code": "string",
    "tests": "string (optional, JSON test cases or pytest code)"
  }
}
```

**Response JSON**
```
{
  "status": "passed|failed|error",
  "detail": {
    "summary": {
      "passed": 1,
      "failed": 0,
      "skipped": 0,
      "xfailed": 0,
      "xpassed": 0,
      "duration_s": 0.12
    }
  }
}
```

### POST /tool/coverage
Run coverage.

**Request JSON**
```
{
  "payload": {
    "code": "string",
    "tests": "string (optional, JSON test cases or pytest code)"
  }
}
```

**Response JSON**
```
{
  "status": "ok|failed|error",
  "detail": {
    "coverage_percent": 85.0,
    "missing_lines": ["12", "15-18"]
  }
}
```

---

## Error Codes
- **400**: Bad request (invalid payload or missing prompt)
- **404**: Unknown endpoint/tool
- **409**: Conflict (prompt exists)
- **500**: Internal server error
