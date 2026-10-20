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
        return self.eval_count / (self.eval_duration_ns / 1_000_000_000)


class OllamaBackend:
    def __init__(self, host="http://127.0.0.1:11434", timeout=600):
        self.host = host.rstrip("/")
        self.timeout = timeout

    def health(self):
        response = requests.get(
            f"{self.host}/api/tags", timeout=10
        )
        response.raise_for_status()
        return response.json()

    def generate(
        self,
        prompt,
        model="qwen2.5-coder:1.5b",
        num_predict=256,
    ):
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "5m",
            "options": {"num_predict": num_predict},
        }

        started = time.perf_counter()
        response = requests.post(
            f"{self.host}/api/generate",
            json=payload,
            timeout=self.timeout,
        )
        elapsed = time.perf_counter() - started
        response.raise_for_status()
        data = response.json()

        return GenerationResult(
            model=data.get("model", model),
            response=data.get("response", ""),
            eval_count=data.get("eval_count", 0),
            eval_duration_ns=data.get("eval_duration", 0),
            wall_time_seconds=elapsed,
        )
