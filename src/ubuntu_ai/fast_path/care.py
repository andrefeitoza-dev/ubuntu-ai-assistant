from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import psutil

from ubuntu_ai.context.health import SystemHealthService


@dataclass(frozen=True, slots=True)
class CareCommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


class CareDiagnosticResponder:
    """Executa somente verificações locais e sugere próximos passos seguros."""

    _DISK_REQUESTS = {
        "analise por que o disco esta cheio",
        "por que o disco esta cheio",
        "diagnostique a falta de espaco",
        "como posso liberar espaco",
        "verifique o espaco em disco",
    }
    _SECURITY_REQUESTS = {
        "faca uma auditoria basica de seguranca deste computador",
        "faca uma auditoria de seguranca",
        "verifique a seguranca deste computador",
        "como esta a seguranca do computador",
        "auditoria basica de seguranca",
    }
    _OVERVIEW_REQUESTS = {
        "como esta o computador",
        "como esta este computador",
        "como esta meu computador",
        "estado geral do computador",
        "resumo da saude do computador",
    }

    def __init__(
        self,
        *,
        home: Path | None = None,
        runner: Callable[[tuple[str, ...]], CareCommandResult] | None = None,
        health_service: SystemHealthService | None = None,
    ) -> None:
        self._home = (home or Path.home()).expanduser()
        self._runner = runner or self._run
        self._health = health_service or SystemHealthService()

    def respond(self, normalized_request: str) -> str | None:
        if normalized_request in self._OVERVIEW_REQUESTS:
            return self._overview_report()
        if normalized_request in self._DISK_REQUESTS:
            return self._disk_report()
        if normalized_request in self._SECURITY_REQUESTS:
            return self._security_report()
        return None

    def _overview_report(self) -> str:
        snapshot = self._health.snapshot()
        if snapshot.metrics is None:
            return "Não foi possível obter o estado atual do computador."
        metrics = snapshot.metrics
        network = (
            "interface ativa detectada"
            if metrics.active_network_interfaces
            else "sem interface ativa detectada"
        )
        firewall = self._summary_status("ufw", ("ufw", "status"), active_word="active")
        security_updates = self._summary_status(
            "systemctl",
            ("systemctl", "is-enabled", "unattended-upgrades.service"),
            active_word="enabled",
        )
        labels = {
            "healthy": "saudável",
            "attention": "requer atenção",
            "critical": "está em estado crítico",
            "unknown": "tem estado desconhecido",
        }
        return "\n".join(
            (
                f"Resumo seguro: o computador {labels[snapshot.status.value]}.",
                f"• CPU: {metrics.cpu_percent:.1f}%",
                f"• Memória RAM: {metrics.memory_percent:.1f}% usada; "
                f"{metrics.memory_available_mb} MiB disponíveis",
                f"• Processos em andamento: {metrics.process_count}",
                f"• Disco: {metrics.disk_percent:.1f}% usado; "
                f"{metrics.disk_free_gb:.1f} GiB livres",
                f"• Rede: {network} ({metrics.active_network_interfaces} interface(s) ativa(s))",
                f"• Firewall: {firewall}",
                f"• Atualizações automáticas de segurança: {security_updates}",
                "",
                "Este resumo não expõe endereços, portas, nomes de processos ou dados pessoais.",
                "Nenhuma configuração foi alterada.",
            )
        )

    def _disk_report(self) -> str:
        try:
            usage = psutil.disk_usage(str(self._home))
        except OSError:
            return "Não foi possível consultar o disco pessoal com as permissões atuais."

        free_gib = usage.free / (1024**3)
        lines = [
            "Diagnóstico de espaço em disco:",
            f"• uso: {usage.percent:.1f}%",
            f"• espaço livre: {free_gib:.1f} GiB",
        ]
        if usage.percent >= 90 or free_gib <= 5:
            lines.append("• atenção: o espaço disponível está em nível crítico.")
        elif usage.percent >= 80 or free_gib <= 10:
            lines.append("• atenção: vale investigar os maiores arquivos e diretórios.")
        else:
            lines.append("• situação: não há pressão elevada de armazenamento neste momento.")
        lines.extend(
            (
                "",
                "Próximos pedidos seguros:",
                "• “Mostre os maiores diretórios.”",
                "• “Localize arquivos grandes em Downloads.”",
                "• “Faça uma limpeza segura de pacotes.”",
                "Nada foi removido ou modificado.",
            )
        )
        return "\n".join(lines)

    def _security_report(self) -> str:
        firewall = self._command_status("ufw", ("ufw", "status"), "Firewall UFW")
        updates = self._command_status(
            "systemctl",
            ("systemctl", "is-enabled", "unattended-upgrades.service"),
            "Atualizações automáticas de segurança",
        )
        return "\n".join(
            (
                "Auditoria básica de segurança (somente leitura):",
                f"• {firewall}",
                f"• {updates}",
                "• permissões: nenhuma configuração foi alterada",
                "",
                "Próximos pedidos seguros:",
                "• “Quais atualizações estão disponíveis?”",
                "• “Mostre as permissões do assistente.”",
                "• “Ative o firewall.”",
                "Alterações de firewall ou pacotes exigirão um plano e confirmação.",
            )
        )

    def _command_status(self, executable: str, command: tuple[str, ...], label: str) -> str:
        if shutil.which(executable) is None:
            return f"{label}: recurso não encontrado"
        result = self._runner(command)
        output = " ".join((result.stdout or result.stderr).strip().split())
        if not output:
            output = "ativo" if result.returncode == 0 else "estado não disponível"
        return f"{label}: {output[:160]}"

    def _summary_status(
        self,
        executable: str,
        command: tuple[str, ...],
        *,
        active_word: str,
    ) -> str:
        if shutil.which(executable) is None:
            return "não disponível"
        result = self._runner(command)
        output = (result.stdout or result.stderr).strip().lower()
        if result.returncode == 0 and active_word in output:
            return "ativo"
        if "permission" in output or "root" in output or "permiss" in output:
            return "não confirmado sem permissão administrativa"
        if output:
            return "não confirmado; consulte a auditoria para detalhes"
        return "estado não disponível"

    @staticmethod
    def _run(command: tuple[str, ...]) -> CareCommandResult:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
                shell=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return CareCommandResult(1, stderr=str(exc))
        return CareCommandResult(result.returncode, result.stdout, result.stderr)
