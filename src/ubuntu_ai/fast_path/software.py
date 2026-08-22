from __future__ import annotations

import subprocess
from collections.abc import Callable


class InstalledSoftwareResponder:
    """Consulta pacotes Debian instalados com uma operação local somente de leitura."""

    def __init__(
        self,
        provider: Callable[[], tuple[tuple[str, str], ...]] | None = None,
        *,
        preview_limit: int = 60,
    ) -> None:
        self._provider = provider or self._query_dpkg
        self._preview_limit = preview_limit

    def respond(self, request: str) -> str | None:
        if request.startswith(("como ", "explique ")):
            return None
        if not self._is_inventory_request(request):
            return None

        try:
            packages = self._provider()
        except (OSError, subprocess.SubprocessError):
            return (
                "Não foi possível consultar os programas instalados. "
                "Nenhuma instalação ou alteração foi realizada."
            )

        if not packages:
            return "Nenhum pacote instalado foi encontrado pelo gerenciador dpkg."

        visible = packages[: self._preview_limit]
        lines = [
            f"Este computador possui {len(packages)} pacotes registrados pelo dpkg.",
            "Primeiros itens em ordem alfabética:",
            *(f"• {name} — {version}" for name, version in visible),
        ]
        if len(packages) > len(visible):
            lines.append(
                f"Exibindo {len(visible)} de {len(packages)}. "
                "Peça pelo nome de um programa ou por uma categoria para refinar."
            )
        lines.append("Consulta somente de leitura; nenhum pacote foi alterado.")
        return "\n".join(lines)

    @staticmethod
    def _is_inventory_request(request: str) -> bool:
        installed = any(word in request for word in ("instalado", "instalados", "instaladas"))
        software = any(
            word in request
            for word in (
                "programa",
                "programas",
                "aplicativo",
                "aplicativos",
                "pacote",
                "pacotes",
            )
        )
        intent = request.startswith(("qual", "quais", "liste", "listar", "mostre", "mostrar"))
        return installed and software and intent

    @staticmethod
    def _query_dpkg() -> tuple[tuple[str, str], ...]:
        result = subprocess.run(
            ("dpkg-query", "-W", "-f=${binary:Package}\t${Version}\n"),
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
            shell=False,
        )
        packages = []
        for line in result.stdout.splitlines():
            name, separator, version = line.partition("\t")
            if separator and name:
                packages.append((name, version))
        return tuple(sorted(packages))
