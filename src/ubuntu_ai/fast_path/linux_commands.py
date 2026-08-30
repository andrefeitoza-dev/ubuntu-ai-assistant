from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class LinuxCommand:
    name: str
    description: str
    example: str
    warning: str | None = None


class LinuxCommandCatalog:
    """Catálogo local de comandos; explica sem autorizar execução."""

    _CATEGORIES: dict[str, tuple[LinuxCommand, ...]] = {
        "navegação": (
            LinuxCommand("pwd", "mostra o diretório atual", "pwd"),
            LinuxCommand("ls", "lista arquivos e diretórios", "ls -la"),
            LinuxCommand("cd", "muda o diretório atual", "cd ~/Documentos"),
        ),
        "arquivos": (
            LinuxCommand("cp", "copia arquivos ou diretórios", "cp origem.txt copia.txt"),
            LinuxCommand("mv", "move ou renomeia arquivos", "mv antigo.txt novo.txt"),
            LinuxCommand("mkdir", "cria diretórios", "mkdir projetos"),
            LinuxCommand("find", "localiza arquivos e diretórios", "find . -name '*.pdf'"),
            LinuxCommand("rg", "pesquisa texto rapidamente", "rg 'erro' logs/"),
            LinuxCommand(
                "rm",
                "remove arquivos",
                "rm arquivo.txt",
                "A remoção pode ser irreversível; confira o caminho antes de executar.",
            ),
        ),
        "leitura": (
            LinuxCommand("cat", "mostra conteúdo textual", "cat arquivo.txt"),
            LinuxCommand("less", "lê conteúdo de forma paginada", "less arquivo.log"),
            LinuxCommand("head", "mostra o início de um arquivo", "head -n 20 arquivo.log"),
            LinuxCommand("tail", "mostra o final de um arquivo", "tail -f aplicativo.log"),
        ),
        "sistema": (
            LinuxCommand("uname", "mostra informações do kernel", "uname -a"),
            LinuxCommand("hostnamectl", "mostra identidade e sistema", "hostnamectl"),
            LinuxCommand("free", "mostra uso de memória", "free -h"),
            LinuxCommand("uptime", "mostra carga e tempo ligado", "uptime"),
        ),
        "armazenamento": (
            LinuxCommand("df", "mostra espaço dos sistemas de arquivos", "df -h"),
            LinuxCommand("du", "calcula o tamanho de arquivos e pastas", "du -sh ~/Downloads"),
            LinuxCommand("lsblk", "lista discos e partições", "lsblk -f"),
        ),
        "processos": (
            LinuxCommand("ps", "lista processos", "ps aux"),
            LinuxCommand("top", "acompanha processos e recursos", "top"),
            LinuxCommand(
                "kill",
                "envia um sinal a um processo",
                "kill PID",
                "Encerrar processos pode interromper trabalho ou serviços.",
            ),
        ),
        "rede": (
            LinuxCommand("ip", "mostra e administra interfaces e rotas", "ip -brief address"),
            LinuxCommand("ss", "mostra conexões e portas", "ss -ltn"),
            LinuxCommand("ping", "testa alcance de rede", "ping -c 4 ubuntu.com"),
            LinuxCommand("curl", "faz requisições e transfere dados", "curl -I https://ubuntu.com"),
        ),
        "serviços": (
            LinuxCommand("systemctl", "consulta e controla serviços", "systemctl status ssh"),
            LinuxCommand("journalctl", "consulta registros do systemd", "journalctl -u ssh -n 50"),
        ),
        "pacotes": (
            LinuxCommand("apt", "gerencia pacotes no Ubuntu", "apt list --installed"),
            LinuxCommand("dpkg", "consulta pacotes Debian", "dpkg -l"),
        ),
        "permissões": (
            LinuxCommand(
                "chmod",
                "altera permissões",
                "chmod u+x script.sh",
                "Permissões incorretas podem expor dados ou impedir acesso.",
            ),
            LinuxCommand(
                "chown",
                "altera proprietário e grupo",
                "chown usuario:grupo arquivo",
                "Normalmente exige privilégios administrativos.",
            ),
        ),
    }

    _ALIASES = {
        "navegacao": "navegação",
        "arquivo": "arquivos",
        "diretorio": "arquivos",
        "disco": "armazenamento",
        "processo": "processos",
        "servico": "serviços",
        "pacote": "pacotes",
        "permissao": "permissões",
    }

    def respond(self, request: str) -> str | None:
        direct_explanation = self._direct_explanation(request)
        if direct_explanation is not None:
            return direct_explanation

        if "comando" not in request and request not in {"linux", "terminal"}:
            return None

        command = self._requested_command(request)
        if command is not None:
            return self._describe(command)

        if "instalados" in request or "disponiveis neste computador" in request:
            return self._installed()

        for alias, category in self._ALIASES.items():
            if alias in request:
                return self._render_category(category)
        for category in self._CATEGORIES:
            plain = category.translate(str.maketrans("ãçõ", "aco"))
            if category in request or plain in request:
                return self._render_category(category)

        if any(word in request for word in ("localizar", "encontrar", "procurar")):
            return self._render_commands((self._find("find"), self._find("rg")))

        if any(
            word in request
            for word in ("principais", "todos", "lista", "mostrar", "quais", "usados")
        ):
            return self._overview(include_all="todos" in request)
        return None

    def _direct_explanation(self, request: str) -> str | None:
        words = request.split()
        if not any(
            marker in request
            for marker in ("como usar", "o que faz", "para que serve", "qual a funcao")
        ):
            return None
        for word in words:
            try:
                command = self._find(word)
            except KeyError:
                continue
            return self._describe(command.name)
        return None

    def _overview(self, *, include_all: bool) -> str:
        if include_all:
            lines = ["Catálogo de comandos Linux:"]
            for category in self._CATEGORIES:
                names = ", ".join(command.name for command in self._CATEGORIES[category])
                lines.append(f"• {category.title()}: {names}")
            lines.append(
                "Peça “explique o comando NOME” para descrição e exemplo. "
                "Esta lista orienta; nenhum comando foi executado."
            )
            return "\n".join(lines)

        lines = ["Principais comandos Linux por categoria:"]
        for category, commands in self._CATEGORIES.items():
            lines.append(f"• {category.title()}: {', '.join(item.name for item in commands)}")
        lines.append("Peça “comandos de rede” ou “explique o comando chmod” para detalhes.")
        return "\n".join(lines)

    def _render_category(self, category: str) -> str:
        return f"Comandos de {category}:\n" + self._render_commands(self._CATEGORIES[category])

    @staticmethod
    def _render_commands(commands: tuple[LinuxCommand, ...]) -> str:
        lines = []
        for command in commands:
            line = f"• {command.name} — {command.description}. Exemplo: {command.example}"
            if command.warning:
                line += f"\n  Atenção: {command.warning}"
            lines.append(line)
        return "\n".join(lines)

    def _describe(self, name: str) -> str:
        try:
            command = self._find(name)
        except KeyError:
            return (
                f"O comando “{name}” não está no catálogo local. "
                "Posso mostrar os principais comandos ou pesquisar por categoria."
            )
        return self._render_commands((command,)) + "\nNenhum comando foi executado."

    def _find(self, name: str) -> LinuxCommand:
        for commands in self._CATEGORIES.values():
            for command in commands:
                if command.name == name:
                    return command
        raise KeyError(name)

    def _requested_command(self, request: str) -> str | None:
        markers = ("explique o comando ", "como usar o comando ", "o que faz o comando ")
        for marker in markers:
            if marker in request:
                return request.split(marker, 1)[1].split()[0]
        return None

    @staticmethod
    def _installed() -> str:
        names: set[str] = set()
        for raw_directory in os.environ.get("PATH", "").split(os.pathsep):
            directory = Path(raw_directory)
            if not directory.is_dir():
                continue
            try:
                names.update(
                    entry.name
                    for entry in directory.iterdir()
                    if entry.is_file() and os.access(entry, os.X_OK)
                )
            except OSError:
                continue
        ordered = sorted(names)
        preview = ", ".join(ordered[:60]) or "nenhum"
        suffix = (
            "\nA lista foi limitada aos primeiros 60. Peça uma categoria ou nome "
            "para refinar a consulta."
            if len(ordered) > 60
            else ""
        )
        return f"Comandos executáveis encontrados: {len(ordered)}.\n{preview}{suffix}"
