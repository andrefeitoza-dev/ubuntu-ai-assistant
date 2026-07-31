from dataclasses import dataclass
from typing import Any

import requests


@dataclass(slots=True)
class OllamaInfo:
    available: bool
    version: str | None
    models: list[str]


class OllamaService:
    """Responsável pela comunicação com a API local do Ollama."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: int = 300,
        session: requests.Session | None = None,
        *,
        response_format: str | None = None,
        num_predict: int | None = None,
        temperature: float | None = None,
        keep_alive: str | None = None,
    ) -> None:
        if timeout <= 0:
            raise ValueError("O timeout deve ser maior que zero.")
        if num_predict is not None and num_predict <= 0:
            raise ValueError("num_predict deve ser maior que zero.")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = session or requests.Session()
        self._response_format = response_format
        self._num_predict = num_predict
        self._temperature = temperature
        self._keep_alive = keep_alive

    def get_info(self) -> OllamaInfo:
        """Obtém informações sobre o servidor e os modelos instalados."""

        try:
            version_response = self._session.get(
                f"{self.base_url}/api/version",
                timeout=self.timeout,
            )
            version_response.raise_for_status()

            models_response = self._session.get(
                f"{self.base_url}/api/tags",
                timeout=self.timeout,
            )
            models_response.raise_for_status()

            version_data = version_response.json()
            models_data = models_response.json()

            models = [
                model["name"]
                for model in models_data.get("models", [])
                if "name" in model
            ]

            return OllamaInfo(
                available=True,
                version=version_data.get("version"),
                models=models,
            )

        except requests.RequestException:
            return OllamaInfo(
                available=False,
                version=None,
                models=[],
            )

    def generate(self, prompt: str, model: str) -> str:
        """Gera uma resposta textual usando um modelo do Ollama."""

        normalized_prompt = prompt.strip()
        normalized_model = model.strip()
        if not normalized_prompt:
            raise ValueError("O prompt não pode estar vazio.")
        if not normalized_model:
            raise ValueError("O modelo não pode estar vazio.")

        payload: dict[str, Any] = {
            "model": normalized_model,
            "prompt": normalized_prompt,
            "stream": False,
        }
        if self._response_format is not None:
            payload["format"] = self._response_format
        if self._keep_alive is not None:
            payload["keep_alive"] = self._keep_alive

        options: dict[str, int | float] = {}
        if self._num_predict is not None:
            options["num_predict"] = self._num_predict
        if self._temperature is not None:
            options["temperature"] = self._temperature
        if options:
            payload["options"] = options

        try:
            response = self._session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.Timeout as error:
            raise RuntimeError(
                "O Ollama não respondeu dentro do tempo configurado "
                f"({self.timeout}s)."
            ) from error
        except requests.RequestException as error:
            raise RuntimeError(
                "Falha ao gerar resposta com o Ollama."
            ) from error

        data = response.json()
        content = data.get("response")

        if not isinstance(content, str) or not content.strip():
            raise ValueError("O Ollama retornou uma resposta vazia ou inválida.")

        return content.strip()
