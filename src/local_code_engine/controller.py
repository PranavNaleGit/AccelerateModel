from dataclasses import dataclass
from .ollama_backend import OllamaBackend


@dataclass
class GenerationRequest:
    prompt: str
    model: str = "qwen2.5-coder:1.5b"
    max_tokens: int = 256


class GenerationController:
    def __init__(self, backend: OllamaBackend):
        self.backend = backend

    def generate(self, request: GenerationRequest):
        if not request.prompt.strip():
            raise ValueError("Prompt must not be empty.")
        if request.max_tokens < 1:
            raise ValueError("max_tokens must be at least 1.")

        return self.backend.generate(
            prompt=request.prompt,
            model=request.model,
            num_predict=request.max_tokens,
        )
