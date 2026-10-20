
import importlib.util


def test_generated_is_even_function():
    path = "results/is_even.py"

    spec = importlib.util.spec_from_file_location(
        "generated_solution", path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.is_even(2) is True
    assert module.is_even(3) is False
    assert module.is_even(0) is True
    assert module.is_even(-4) is True
    assert module.is_even(-5) is False
