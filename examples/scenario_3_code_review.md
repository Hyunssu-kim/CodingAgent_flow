# Scenario 3: Code Review

## Goal
Review code with a checklist and severity levels, then provide actionable fixes.

## cURL Request
```
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{"task_type":"code_review","user_input":"Review the following code for security and reliability.\n\nCODE:\n```python\nimport os\n\ndef read_path(p):\n    return open(p).read()\n```","project_id":"demo"}'
```

## Expected Output (shape)
```
{
  "llm_output": "findings with severity and fixes",
  "memory_snapshot": "...",
  "quality_report": {"lint": {...}, "test": {...}, "coverage": {...}}
}
```

## Demo Tips
- Ensure findings include security issues (e.g., path validation, file handling).
- Check severity labels (critical/high/medium/low).
