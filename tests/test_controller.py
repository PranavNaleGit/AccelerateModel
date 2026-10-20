import pytest
from local_code_engine.controller import (
    GenerationController,
    GenerationRequest,
)


class FakeBackend:
    def generate(self, **kwargs):
        return kwargs


def test_controller_forwards_request():
    controller = GenerationController(FakeBackend())
    result = controller.generate(
        GenerationRequest("hello", "test-model", 32)
    )
    assert result == {
        "prompt": "hello",
        "model": "test-model",
        "num_predict": 32,
    }


def test_blank_prompt_is_rejected():
    controller = GenerationController(FakeBackend())
    with pytest.raises(ValueError):
        controller.generate(GenerationRequest("  "))


def test_invalid_token_limit_is_rejected():
    controller = GenerationController(FakeBackend())
    with pytest.raises(ValueError):
        controller.generate(GenerationRequest("hello", max_tokens=0))
