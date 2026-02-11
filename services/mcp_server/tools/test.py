import re
import sys
import tempfile
import importlib.util
from typing import Any, Dict, List
import subprocess

from .testgen import generate_pytest_from_cases


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _run_cmd(args: List[str], cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=20,
    )


def _parse_pytest_summary(output: str) -> Dict[str, Any]:
    output = _strip_ansi(output)
    summary = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0,
        "duration_s": None,
    }
    # Look for line like: "1 failed, 2 passed, 1 skipped in 0.12s"
    match = re.search(r"in\s+([0-9.]+)s", output)
    if match:
        summary["duration_s"] = float(match.group(1))

    for key in ["passed", "failed", "skipped", "xfailed", "xpassed"]:
        m = re.search(rf"(\d+)\s+{key}", output)
        if m:
            summary[key] = int(m.group(1))
    return summary


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text or "")


def run_test(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not _module_available("pytest"):
        return {
            "status": "error",
            "detail": {"message": "pytest is not installed"},
        }

    code = str(payload.get("code", ""))
    tests = str(payload.get("tests", ""))
    if not code.strip():
        return {
            "status": "error",
            "detail": {"message": "empty code payload"},
        }
    with tempfile.TemporaryDirectory() as tmpdir:
        code_path = f"{tmpdir}/app.py"
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code)
        if tests.strip():
            test_path = f"{tmpdir}/test_generated.py"
            test_code, test_err = generate_pytest_from_cases(tests)
            if test_err:
                return {"status": "error", "detail": {"message": test_err}}
            if not test_code.strip():
                return {"status": "skipped", "detail": {"message": "no test cases generated"}}
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(test_code)
        else:
            # Fall back to running pytest on the provided code file.
            # This enables execution when tests are embedded in the code payload.
            test_path = code_path

        args = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--disable-warnings",
            test_path,
        ]
        proc = _run_cmd(args, tmpdir)
        combined = proc.stdout + "\n" + proc.stderr
        summary = _parse_pytest_summary(combined)

        if "no tests ran" in combined.lower() or "no tests collected" in combined.lower():
            status = "skipped"
        else:
            status = "passed" if proc.returncode == 0 else "failed"
        return {
            "status": status,
            "detail": {
                "summary": summary,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            },
        }
