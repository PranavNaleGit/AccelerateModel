import pytest
from types import SimpleNamespace

from local_code_engine.benchmark import run_benchmark


class FakeController:
    def __init__(self):
        self.calls = []

    def generate(self, request):
        self.calls.append(request)
        return SimpleNamespace(
            tokens_per_second=100.0 + len(self.calls),
            eval_count=50,
            wall_time_seconds=0.5,
        )


def test_benchmark_runs_requested_number_of_samples():
    controller = FakeController()

    result = run_benchmark(controller, runs=3, warmup=False)

    assert len(result["samples"]) == 3
    assert len(controller.calls) == 3
    assert result["runs"] == 3


def test_warmup_is_excluded_from_samples():
    controller = FakeController()

    result = run_benchmark(controller, runs=2, warmup=True)

    assert len(controller.calls) == 3
    assert len(result["samples"]) == 2
    assert result["samples"][0]["tokens_per_second"] == 102.0


def test_summary_statistics_are_calculated():
    controller = FakeController()

    result = run_benchmark(controller, runs=3, warmup=False)

    assert result["summary"]["average_tokens_per_second"] == 102.0
    assert result["summary"]["median_tokens_per_second"] == 102.0
    assert result["summary"]["minimum_tokens_per_second"] == 101.0
    assert result["summary"]["maximum_tokens_per_second"] == 103.0


def test_zero_runs_are_rejected():
    with pytest.raises(ValueError, match="at least 1"):
        run_benchmark(FakeController(), runs=0)
