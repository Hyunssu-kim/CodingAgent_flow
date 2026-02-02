import json
from typing import Any, List, Tuple


def _format_args(args: List[Any]) -> str:
    return ", ".join(repr(a) for a in args)


def generate_pytest_from_cases(tests_text: str) -> Tuple[str, str | None]:
    """Convert JSON test cases to pytest code.

    Expected JSON:
    {
      "cases": [
        {"name": "case_1", "call": "add", "input": [1, 2], "expected": 3},
        {"name": "case_2", "call": "add", "input": ["a", 1], "raises": "TypeError"}
      ]
    }
    """
    text = tests_text.strip()
    if not text:
        return "", None

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Assume already Python test code.
        return text, None

    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) == 0:
        return "", "no test cases provided"

    calls = []
    needs_pytest = False
    for idx, case in enumerate(cases):
        if not isinstance(case, dict):
            return "", "invalid test case format"
        call = case.get("call")
        if not call:
            return "", "test case missing 'call' field"
        args = case.get("input", [])
        if not isinstance(args, list):
            return "", "test case 'input' must be a list"
        if "raises" in case:
            needs_pytest = True
        else:
            approx = case.get("approx")
            if approx:
                needs_pytest = True
        calls.append(call)

    unique_calls = sorted(set(calls))
    lines: List[str] = []
    if needs_pytest:
        lines.append("import pytest")
    if unique_calls:
        lines.append(f"from app import {', '.join(unique_calls)}")
    lines.append("")

    # Rebuild test bodies with imports at top
    body_lines = []
    for idx, case in enumerate(cases):
        name = case.get("name") or f"case_{idx + 1}"
        call = case.get("call")
        args = case.get("input", [])
        args_expr = _format_args(args)
        body_lines.append(f"def test_{name}():")
        indent = "    "
        if "raises" in case:
            exc = case.get("raises") or "Exception"
            body_lines.append(f"{indent}with pytest.raises({exc}):")
            body_lines.append(f"{indent}    {call}({args_expr})")
        else:
            expected = case.get("expected")
            approx = case.get("approx")
            if approx:
                if isinstance(approx, dict):
                    kwargs = ", ".join(f"{k}={repr(v)}" for k, v in approx.items())
                    exp_expr = f"pytest.approx({repr(expected)}, {kwargs})"
                else:
                    exp_expr = f"pytest.approx({repr(expected)})"
                body_lines.append(f"{indent}result = {call}({args_expr})")
                body_lines.append(f"{indent}assert result == {exp_expr}")
            else:
                body_lines.append(f"{indent}assert {call}({args_expr}) == {repr(expected)}")
        body_lines.append("")

    lines.extend(body_lines)
    return "\n".join(lines).rstrip() + "\n", None
