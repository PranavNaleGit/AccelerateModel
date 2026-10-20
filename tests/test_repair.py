
from types import SimpleNamespace

from local_code_engine.repair import repair_code


class FakeController:
    """Return incorrect code first, then corrected code."""

    def __init__(self):
        self.calls = []

        self.responses = [
            "def is_even(number):\n    return number % 2 == 1",
            "def is_even(number):\n    return number % 2 == 0",
        ]

    def generate(self, request):
        self.calls.append(request)

        response = self.responses.pop(0)

        return SimpleNamespace(response=response)


def test_repair_retries_until_supplied_tests_pass(tmp_path):
    controller = FakeController()

    tests_file = tmp_path / "is_even_tests.py"
    tests_file.write_text(
        "assert is_even(2) is True\n"
        "assert is_even(3) is False\n"
        "assert is_even(0) is True\n"
        "assert is_even(-4) is True\n"
        "assert is_even(-5) is False\n",
        encoding="utf-8",
    )

    output_file = tmp_path / "is_even.py"

    result = repair_code(
        controller,
        prompt=(
            "Write a function named is_even that returns "
            "True for even integers and False otherwise."
        ),
        attempts=1,
        output_path=str(output_file),
        tests_file=str(tests_file),
    )

    assert result["ok"] is True
    assert result["repair_attempts"] == 1
    assert len(controller.calls) == 2
    assert result["history"][0]["ok"] is False
    assert result["history"][1]["ok"] is True
    assert output_file.exists()
