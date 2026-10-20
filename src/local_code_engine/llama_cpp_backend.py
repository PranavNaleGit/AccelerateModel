import time
import requests
from dataclasses import dataclass


@dataclass
class GenerationResult:
    model: str
    response: str
    eval_count: int
    eval_duration_ns: int
    wall_time_seconds: float

    @property
    def tokens_per_second(self):
        if not self.eval_count or not self.eval_duration_ns:
            return 0.0
        return self.eval_count / (
            self.eval_duration_ns / 1_000_000_000
        )


class LlamaCppBackend:
    """Backend for a local llama.cpp server."""

    def __init__(self, host="http://127.0.0.1:8080", timeout=600):
        self.host = host.rstrip("/")
        self.timeout = timeout

    def health(self):
        response = requests.get(
            f"{self.host}/health",
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def generate(
        self,
        prompt,
        model="local-model",
        num_predict=256,
    ):
        payload = {
            "prompt": prompt,
            "n_predict": num_predict,
            "temperature": 0,
            "stream": False,
            "cache_prompt": False,
        }

        started = time.perf_counter()
        response = requests.post(
            f"{self.host}/completion",
            json=payload,
            timeout=self.timeout,
        )
        elapsed = time.perf_counter() - started
        response.raise_for_status()
        data = response.json()
        timings = data.get("timings", {})

        return GenerationResult(
            model=data.get("model", model),
            response=data.get("content", ""),
            eval_count=timings.get("predicted_n", 0),
            eval_duration_ns=int(
                timings.get("predicted_ms", 0) * 1_000_000
            ),
            wall_time_seconds=elapsed,
        )
