from typing import Any

import pytest
import requests

from ubuntu_ai.services.ollama import OllamaService


class FakeResponse:
    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict[str, Any]:
        return self._data


class FakeSession:
    def __init__(self, response_data: dict[str, Any]) -> None:
        self.response_data = response_data
        self.last_url: str | None = None
        self.last_json: dict[str, Any] | None = None
        self.last_timeout: int | None = None

    def post(
        self,
        url: str,
        *,
        json: dict[str, Any],
        timeout: int,
    ) -> FakeResponse:
        self.last_url = url
        self.last_json = json
        self.last_timeout = timeout

        return FakeResponse(self.response_data)


class FailingSession:
    def post(
        self,
        url: str,
        *,
        json: dict[str, Any],
        timeout: int,
    ) -> FakeResponse:
        raise requests.ConnectionError("Ollama indisponível")


def test_ollama_service_generates_text() -> None:
    session = FakeSession({"response": "Docker é uma plataforma de containers."})
    service = OllamaService(
        base_url="http://localhost:11434/",
        timeout=45,
        session=session,
    )

    result = service.generate(
        prompt="Explique Docker",
        model="qwen2.5:3b",
    )

    assert result == "Docker é uma plataforma de containers."
    assert session.last_url == "http://localhost:11434/api/generate"
    assert session.last_timeout == 45
    assert session.last_json == {
        "model": "qwen2.5:3b",
        "prompt": "Explique Docker",
        "stream": False,
    }


def test_ollama_service_rejects_empty_response() -> None:
    service = OllamaService(
        session=FakeSession({"response": "   "}),
    )

    with pytest.raises(ValueError, match="resposta vazia ou inválida"):
        service.generate(
            prompt="Explique Docker",
            model="qwen2.5:3b",
        )


def test_ollama_service_converts_request_error() -> None:
    service = OllamaService(session=FailingSession())

    with pytest.raises(RuntimeError, match="Falha ao gerar resposta"):
        service.generate(
            prompt="Explique Docker",
            model="qwen2.5:3b",
        )

def test_ollama_service_applies_generation_limits() -> None:
    session = FakeSession({"response": '{"goal": "Teste"}'})
    service = OllamaService(
        session=session,
        response_format="json",
        num_predict=384,
        temperature=0.1,
        keep_alive="10m",
    )

    service.generate(prompt="Crie um plano", model="qwen2.5:3b")

    assert session.last_json == {
        "model": "qwen2.5:3b",
        "prompt": "Crie um plano",
        "stream": False,
        "format": "json",
        "keep_alive": "10m",
        "options": {
            "num_predict": 384,
            "temperature": 0.1,
        },
    }
