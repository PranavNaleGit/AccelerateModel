
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

from .controller import GenerationRequest


DEFAULT_PROMPT = (
    "Write a Python function named is_prime(n) that returns True "
    "if n is prime and False otherwise. Return only the function."
)


def run_benchmark(
    controller,
    model="qwen2.5-coder:1.5b",
    runs=5,
    max_tokens=256,
    warmup=True,
):
    if runs < 1:
        raise ValueError("runs must be at least 1")

    if max_tokens < 1:
        raise ValueError("max_tokens must be at least 1")

    if warmup:
        controller.generate(
            GenerationRequest(DEFAULT_PROMPT, model, max_tokens)
        )

    samples = []

    for index in range(runs):
        result = controller.generate(
            GenerationRequest(DEFAULT_PROMPT, model, max_tokens)
        )

        samples.append(
            {
                "run": index + 1,
                "tokens_per_second": round(
                    result.tokens_per_second, 3
                ),
                "generated_tokens": result.eval_count,
                "generation_seconds": round(
                    result.wall_time_seconds, 4
                ),
            }
        )

    speeds = [
        sample["tokens_per_second"]
        for sample in samples
    ]

    latencies = [
        sample["generation_seconds"]
        for sample in samples
    ]

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "runs": runs,
        "warmup": warmup,
        "samples": samples,
        "summary": {
            "average_tokens_per_second": round(
                statistics.mean(speeds), 3
            ),
            "median_tokens_per_second": round(
                statistics.median(speeds), 3
            ),
            "minimum_tokens_per_second": round(
                min(speeds), 3
            ),
            "maximum_tokens_per_second": round(
                max(speeds), 3
            ),
            "average_generation_seconds": round(
                statistics.mean(latencies), 4
            ),
            "median_generation_seconds": round(
                statistics.median(latencies), 4
            ),
        },
    }


def save_results(
    results,
    path="results/benchmark-results.json",
):
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )
