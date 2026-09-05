from __future__ import annotations

import unicodedata

from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.domain.risk import RiskLevel


class SafeMaintenancePlanner:
    """Planos fechados de manutenção privilegiada para a interface gráfica."""

    _CLEANUP = {
        "libere espaco removendo pacotes nao usados",
        "remova pacotes nao utilizados",
        "limpe pacotes desnecessarios",
        "faca uma limpeza segura de pacotes",
    }
    _UPDATE = {
        "atualize os pacotes",
        "atualize meu ubuntu",
        "instale as atualizacoes disponiveis",
        "aplique as atualizacoes do sistema",
    }
    _FIREWALL = {
        "ative o firewall",
        "ative o ufw",
        "habilite o firewall",
        "habilite o ufw",
    }

    def try_create_plan(self, request: str) -> Plan | None:
        normalized = self._normalize(request)
        if normalized in self._CLEANUP:
            return self._cleanup_plan()
        if normalized in self._UPDATE:
            return self._update_plan()
        if normalized in self._FIREWALL:
            return self._firewall_plan()
        return None

    @staticmethod
    def _cleanup_plan() -> Plan:
        return Plan(
            goal="Liberar espaço de pacotes com confirmação",
            estimated_seconds=180,
            risk=RiskLevel.HIGH,
            planner="builtin",
            steps=[
                PlanStep(
                    title="Remover dependências não utilizadas",
                    description=(
                        "Remove somente pacotes marcados pelo APT como automáticos e órfãos."
                    ),
                    command=["pkexec", "apt-get", "autoremove", "-y"],
                ),
                PlanStep(
                    title="Limpar cache do APT",
                    description=(
                        "Remove arquivos de pacotes já baixados; não remove documentos pessoais."
                    ),
                    command=["pkexec", "apt-get", "clean"],
                ),
            ],
        )

    @staticmethod
    def _update_plan() -> Plan:
        return Plan(
            goal="Atualizar pacotes do Ubuntu com confirmação",
            estimated_seconds=900,
            risk=RiskLevel.HIGH,
            planner="builtin",
            steps=[
                PlanStep(
                    title="Atualizar índices",
                    description="Obtém a lista atual de pacotes dos repositórios configurados.",
                    command=["pkexec", "apt-get", "update"],
                ),
                PlanStep(
                    title="Aplicar atualizações",
                    description="Atualiza pacotes instalados sem executar dist-upgrade.",
                    command=["pkexec", "apt-get", "upgrade", "-y"],
                ),
            ],
        )

    @staticmethod
    def _firewall_plan() -> Plan:
        return Plan(
            goal="Ativar o firewall UFW com confirmação",
            estimated_seconds=30,
            risk=RiskLevel.CRITICAL,
            planner="builtin",
            steps=[
                PlanStep(
                    title="Ativar firewall",
                    description=(
                        "Ativa a política atual do UFW. Pode afetar conexões e serviços de rede."
                    ),
                    command=["pkexec", "ufw", "enable"],
                ),
                PlanStep(
                    title="Verificar firewall",
                    description="Consulta o estado resultante sem alterar novas regras.",
                    command=["ufw", "status", "verbose"],
                ),
            ],
        )

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value.strip().lower())
        ascii_text = "".join(
            character for character in normalized if not unicodedata.combining(character)
        )
        return " ".join(ascii_text.rstrip("?.!").split())
