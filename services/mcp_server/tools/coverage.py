import re
import sys
import tempfile
import importlib.util
from typing import Any, Dict, List, Optional
import subprocess


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _run_cmd(args: List[str], cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _parse_coverage_report(report_text: str, target_file: str) -> Dict[str, Any]:
    coverage_percent: Optional[float] = None
    missing_lines: List[str] = []

    line_re = re.compile(r"^(.+?)\\s+(\\d+)\\s+(\\d+)\\s+(\\d+)%\\s*(.*)$")
    for line in report_text.splitlines():
        m = line_re.match(line.strip())
        if not m:
            continue
        name, _stmts, _miss, pct, missing = m.groups()
        if name.strip() == "TOTAL":
            coverage_percent = float(pct)
        if name.endswith(target_file):
            if missing:
                missing_lines = [s.strip() for s in missing.split(",") if s.strip()]

    return {
        "coverage_percent": coverage_percent,
        "missing_lines": missing_lines,
    }


def run_coverage(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not _module_available("coverage"):
        return {
            "status": "error",
            "detail": {"message": "coverage is not installed"},
        }
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
        code_name = "app.py"
        test_name = "test_generated.py"
        code_path = f"{tmpdir}/{code_name}"
        test_path = f"{tmpdir}/{test_name}"
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code)
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("from app import *\n")
            f.write(tests)

        run_args = [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "-m",
            "pytest",
            "-q",
            "--disable-warnings",
            test_path,
        ]
        run_proc = _run_cmd(run_args, tmpdir)

        report_args = [sys.executable, "-m", "coverage", "report", "-m"]
        report_proc = _run_cmd(report_args, tmpdir)
        parsed = _parse_coverage_report(report_proc.stdout, code_name)

        combined = (run_proc.stdout + "\n" + run_proc.stderr).lower()
        if "no tests ran" in combined or "no tests collected" in combined or "no data to report" in report_proc.stdout.lower():
            status = "skipped"
        else:
            status = "ok" if run_proc.returncode == 0 else "failed"
        return {
            "status": status,
            "detail": {
                "coverage_percent": parsed["coverage_percent"],
                "missing_lines": parsed["missing_lines"],
                "stdout": run_proc.stdout,
                "stderr": run_proc.stderr,
                "report": report_proc.stdout,
            },
        }
