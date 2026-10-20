import ast
from pathlib import Path


def check_python_syntax(path):
    file_path = Path(path)

    try:
        source = file_path.read_text(encoding="utf-8")
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
