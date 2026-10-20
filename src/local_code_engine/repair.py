
import re
import tempfile
from pathlib import Path

from .controller import GenerationRequest
from .verify import check_python_syntax, run_python_checks


def extract_code(response):
    """Extract Python code from model output."""
    match = re.search(
        r"```(?:python)?\s*(.*?)```",
        response,
        re.DOTALL | re.IGNORECASE,
    )
    return match.group(1).strip() if match else response.strip()


def repair_code(
    controller,
    prompt,
    model="qwen2.5-coder:1.5b",
    max_tokens=512,
    attempts=2,
    output_path="results/generated_solution.py",
    execute=False,
    timeout=5,
    tests_file=None,
):
    if not prompt.strip():
        raise ValueError("Prompt must not be empty.")

    if attempts < 0:
        raise ValueError("Attempts cannot be negative.")

    if max_tokens < 1:
        raise ValueError("max_tokens must be at least 1.")

    test_source = None

    if tests_file:
        test_path = Path(tests_file)
        test_source = test_path.read_text(encoding="utf-8-sig")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    request = GenerationRequest(
        prompt=(
            "Write a complete Python solution for this task.\n"
            "Return only Python code, without explanations.\n\n"
            f"Task: {prompt}"
        ),
        model=model,
        max_tokens=max_tokens,
    )

    generated = controller.generate(request)
    code = extract_code(generated.response)
    history = []

    for attempt in range(attempts + 1):
        output.write_text(code + "\n", encoding="utf-8")
        check = None

        if test_source is not None:
            # Run the solution and its supplied assertions together.
            # This is not a security sandbox.
            with tempfile.TemporaryDirectory() as temp_dir:
                test_program = Path(temp_dir) / "solution_with_tests.py"
                test_program.write_text(
                    code + "\n\n" + test_source + "\n",
                    encoding="utf-8",
                )
                check = run_python_checks(
                    test_program, timeout=timeout
                )

        elif execute:
            check = run_python_checks(output, timeout=timeout)

        else:
            check = check_python_syntax(output)

        history.append({
            "attempt": attempt + 1,
            "ok": check["ok"],
            "message": check["message"],
        })

        if check["ok"]:
            return {
                "ok": True,
                "path": str(output),
                "repair_attempts": attempt,
                "executed": execute or test_source is not None,
                "tests_file": str(tests_file) if tests_file else None,
                "history": history,
                "message": (
                    "Code passed the supplied tests."
                    if test_source is not None
                    else "Code generated and checks passed."
                    if execute
                    else "Code generated and syntax is valid."
                ),
            }

        if attempt == attempts:
            break

        error_details = (
            check.get("stderr")
            or check.get("message", "Unknown error")
        )

        repair_prompt = (
            "Fix the following Python solution.\n"
            "Return only the complete corrected Python code.\n"
            "Preserve the original task and functionality.\n\n"
            f"Original task:\n{prompt}\n\n"
            f"Current code:\n{code}\n\n"
            f"Error details:\n{error_details}"
        )

        if test_source is not None:
            repair_prompt += (
                "\n\nThe following tests must pass:\n"
                + test_source
            )

        repaired = controller.generate(
            GenerationRequest(
                prompt=repair_prompt,
                model=model,
                max_tokens=max_tokens,
            )
        )
        code = extract_code(repaired.response)

    return {
        "ok": False,
        "path": str(output),
        "repair_attempts": attempts,
        "executed": execute or test_source is not None,
        "tests_file": str(tests_file) if tests_file else None,
        "history": history,
        "message": "Code still failed after all attempts.",
    }
