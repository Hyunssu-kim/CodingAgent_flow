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
    if not code.strip():
        return {
            "status": "error",
            "detail": {"message": "empty code payload"},
        }

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = f"{tmpdir}/generated.py"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        args = [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--format",
            "json",
            file_path,
        ]
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
