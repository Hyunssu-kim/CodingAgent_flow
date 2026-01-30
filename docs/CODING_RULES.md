# Coding Rules

## Python Coding Standards (PEP 8)
- Follow PEP 8 style guides for naming, spacing, and formatting.
- Use 4 spaces for indentation, no tabs.
- Keep line length <= 100 chars (unless unavoidable in strings).

## Type Hints (Required)
- All public functions and methods must have type annotations.
- Use `Optional[T]` only when `None` is a valid value.
- Prefer `dict[str, Any]`/`list[str]` syntax (Python 3.9+).

## Docstring Rules
- All public modules, classes, and functions must have docstrings.
- Use Google-style docstrings.
- Include Args, Returns, Raises when applicable.

Example:
```
def add(a: int, b: int) -> int:
    """Add two integers.

    Args:
        a: First integer.
        b: Second integer.

    Returns:
        Sum of a and b.
    """
    return a + b
```

## Error Handling Pattern
- Always catch external I/O errors (network, filesystem, subprocess).
- Convert lower-level exceptions to structured errors with clear messages.
- Avoid silent failures; return error status and debug details.
- Use early validation for input payloads.

## Testing Rules
- Use pytest for all tests.
- Tests must be deterministic and isolated.
- Name tests as `test_<feature>.py` and functions as `test_<case>()`.
- Cover both happy path and failure cases.
- For critical logic, add at least one unit test.

## Import Order
1. Standard library
2. Third-party
3. Local application imports

Each group separated by a blank line.

Example:
```
import os
import sys

from fastapi import FastAPI

from apps.orchestrator.core.agent_loop import AgentLoop
```
