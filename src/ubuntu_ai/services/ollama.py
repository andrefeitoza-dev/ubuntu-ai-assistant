from dataclasses import dataclass

import requests


@dataclass(slots=True)
class OllamaInfo:
    available: bool
    version: str | None
    models: list[str]


class OllamaService:
    """Responsável pela comunicação com a API local do Ollama."""

    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        self.base_url = base_url.rstrip("/")

    def get_info(self) -> OllamaInfo:
        try:
            version_response = requests.get(
                f"{self.base_url}/api/version",
                timeout=3,
            )
            version_response.raise_for_status()

            models_response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=3,
            )
            models_response.raise_for_status()

            version_data = version_response.json()
            models_data = models_response.json()

            models = [model["name"] for model in models_data.get("models", []) if "name" in model]

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
