
from local_code_engine.verify import (
    check_python_syntax,
    run_python_checks,
)


def test_valid_python_file(tmp_path):
    file = tmp_path / "valid.py"
    file.write_text("print('hello')", encoding="utf-8")

    result = check_python_syntax(file)

    assert result["ok"] is True


def test_invalid_python_file(tmp_path):
    file = tmp_path / "invalid.py"
    file.write_text("def broken(:", encoding="utf-8")

    result = check_python_syntax(file)

    assert result["ok"] is False


def test_successful_execution(tmp_path):
    file = tmp_path / "working.py"
    file.write_text(
        "print('All checks passed.')",
        encoding="utf-8",
    )

    result = run_python_checks(file)

    assert result["ok"] is True
    assert "All checks passed." in result["stdout"]


def test_failed_execution(tmp_path):
    file = tmp_path / "failing.py"
    file.write_text(
        "assert 1 == 2",
        encoding="utf-8",
    )

    result = run_python_checks(file)

    assert result["ok"] is False
    assert result["return_code"] != 0
