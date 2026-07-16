from dataclasses import dataclass

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
        timeout: int = 120,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = session or requests.Session()

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

        try:
            response = self._session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as error:
            raise RuntimeError(
                "Falha ao gerar resposta com o Ollama."
            ) from error

        data = response.json()
        content = data.get("response")

        if not isinstance(content, str) or not content.strip():
            raise ValueError("O Ollama retornou uma resposta vazia ou inválida.")

        return content.strip()