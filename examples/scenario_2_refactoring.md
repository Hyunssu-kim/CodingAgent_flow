# Scenario 2: Refactoring

## Goal
Refactor existing code while preserving behavior and report performance impact.

## cURL Request
```
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{"task_type":"refactoring","user_input":"Refactor a loop-heavy function for readability and performance.\n\nCODE:\n```python\nfor i in range(len(items)):\n    if items[i] is not None:\n        result.append(items[i].strip())\n```","project_id":"demo"}'
```

## Expected Output (shape)
```
{
  "llm_output": "analysis + refactor code + performance impact",
  "memory_snapshot": "...",
  "quality_report": {"lint": {...}, "test": {...}, "coverage": {...}}
}
```

## Demo Tips
- Confirm that the response includes before/after comparison.
- Note performance discussion in the output.
