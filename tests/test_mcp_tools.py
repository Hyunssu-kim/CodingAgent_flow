import importlib.util

from services.mcp_server.tools.lint import run_lint
from services.mcp_server.tools.test import run_test
from services.mcp_server.tools.coverage import run_coverage


def _available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def test_lint_tool():
    code = "def add(a: int, b: int) -> int:\n    return a + b\n"
    if _available("ruff"):
        result = run_lint({"code": code})
        assert result["status"] in {"ok", "violations"}
        assert "count" in result["detail"]
    else:
        result = run_lint({"code": code})
        assert result["status"] == "error"
        assert "ruff is not installed" in result["detail"]["message"]


def test_pytest_tool():
    code = (
        "def add(a: int, b: int) -> int:\n"
        "    return a + b\n\n"
        "def test_add():\n"
        "    assert add(1, 2) == 3\n"
    )
    if _available("pytest"):
        result = run_test({"code": code})
        assert result["status"] in {"passed", "failed"}
        assert "summary" in result["detail"]
    else:
        result = run_test({"code": code})
        assert result["status"] == "error"
        assert "pytest is not installed" in result["detail"]["message"]


def test_coverage_tool():
    code = (
        "def add(a: int, b: int) -> int:\n"
        "    return a + b\n\n"
        "def test_add():\n"
        "    assert add(1, 2) == 3\n"
    )
    if _available("coverage") and _available("pytest"):
        result = run_coverage({"code": code})
        assert result["status"] in {"ok", "failed"}
        assert "coverage_percent" in result["detail"]
    else:
        result = run_coverage({"code": code})
        assert result["status"] == "error"
