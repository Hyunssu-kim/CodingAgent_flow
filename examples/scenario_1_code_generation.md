# Scenario 1: Code Generation

## Goal
Generate a production-ready Python function with design-aware context and quality checks.

## cURL Request
```
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{"task_type":"code_generation","user_input":"Create a safe file reader that limits file size.","project_id":"demo"}'
```

## Expected Output (shape)
```
{
  "llm_output": "...python code...",
  "memory_snapshot": "Memory Snapshot (recent/high-signal): ...",
  "retrieved_context": ["..."],
  "quality_report": {
    "lint": {"status": "ok|violations|error"},
    "test": {"status": "passed|failed|error"},
    "coverage": {"status": "ok|failed|error"}
  }
}
```

## Demo Tips
- Use a small, focused task and verify that Memory Snapshot includes design doc cues.
- Check that MCP quality tools return results.
