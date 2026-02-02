import json
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
        timeout=10,
    )


def run_lint(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not _module_available("ruff"):
        return {
            "status": "error",
            "detail": {"message": "ruff is not installed"},
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
        test_path = None
        if tests.strip():
            test_path = f"{tmpdir}/test_generated.py"
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(tests)

        args = [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--output-format",
            "json",
            code_path,
        ]
        if test_path:
            args.append(test_path)
        proc = _run_cmd(args, tmpdir)
        if proc.returncode != 0 and "unexpected argument '--output-format'" in proc.stderr:
            args = [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "--format",
                "json",
                code_path,
            ]
            if test_path:
                args.append(test_path)
            proc = _run_cmd(args, tmpdir)

        violations: List[Dict[str, Any]] = []
        stdout = proc.stdout.strip()
        if stdout:
            try:
                items = json.loads(stdout)
                for item in items:
                    location = item.get("location") or {}
                    violations.append(
                        {
                            "code": item.get("code"),
                            "message": item.get("message"),
                            "file": item.get("filename"),
                            "line": location.get("row"),
                            "column": location.get("column"),
                            "severity": "warning",
                        }
                    )
            except json.JSONDecodeError:
                return {
                    "status": "error",
                    "detail": {
                        "message": "failed to parse ruff json output",
                        "stdout": proc.stdout,
                        "stderr": proc.stderr,
                    },
                }

        status = "ok" if proc.returncode == 0 else "violations"
        return {
            "status": status,
            "detail": {
                "count": len(violations),
                "violations": violations,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            },
        }
