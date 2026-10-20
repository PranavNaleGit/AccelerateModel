
import ast
import subprocess
import sys
from pathlib import Path


def check_python_syntax(path):
    file_path = Path(path)

    try:
        source = file_path.read_text(encoding="utf-8-sig")
        ast.parse(source, filename=str(file_path))

        return {
            "ok": True,
            "path": str(file_path),
            "message": "Python syntax is valid.",
        }

    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
        return {
            "ok": False,
            "path": str(file_path),
            "message": str(exc),
        }


def run_python_checks(path, timeout=5):
    file_path = Path(path)

    syntax_result = check_python_syntax(file_path)
    if not syntax_result["ok"]:
        return {
            **syntax_result,
            "executed": False,
            "return_code": None,
            "stdout": "",
            "stderr": "",
        }

    try:
        result = subprocess.run(
            [sys.executable, str(file_path.resolve())],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        return {
            "ok": result.returncode == 0,
            "path": str(file_path),
            "executed": True,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "message": (
                "Python checks passed."
                if result.returncode == 0
                else "Python checks failed."
            ),
        }

    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "path": str(file_path),
            "executed": False,
            "return_code": None,
            "stdout": "",
            "stderr": "",
            "message": f"Execution exceeded the {timeout}-second timeout.",
        }

    except OSError as exc:
        return {
            "ok": False,
            "path": str(file_path),
            "executed": False,
            "return_code": None,
            "stdout": "",
            "stderr": str(exc),
            "message": "Could not execute the Python file.",
        }
