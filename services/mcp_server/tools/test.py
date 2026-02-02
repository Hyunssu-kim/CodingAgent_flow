import re
import sys
import tempfile
import importlib.util
from typing import Any, Dict, List
import subprocess


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
    summary = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0,
        "duration_s": None,
    }
    # Look for line like: "1 failed, 2 passed, 1 skipped in 0.12s"
    match = re.search(r"in\\s+([0-9.]+)s", output)
    if match:
        summary["duration_s"] = float(match.group(1))

    for key in ["passed", "failed", "skipped", "xfailed", "xpassed"]:
        m = re.search(rf"(\\d+)\\s+{key}", output)
        if m:
            summary[key] = int(m.group(1))
    return summary


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
    if not tests.strip():
        return {
            "status": "skipped",
            "detail": {"message": "no tests provided"},
        }

    with tempfile.TemporaryDirectory() as tmpdir:
        code_path = f"{tmpdir}/app.py"
        test_path = f"{tmpdir}/test_generated.py"
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code)
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("from app import *\n")
            f.write(tests)

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
