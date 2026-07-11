from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.domain.risk import RiskLevel


class Planner:
    """Transforma solicitações do usuário em planos estruturados."""

    def create_plan(self, request: str) -> Plan:
        normalized_request = request.strip().lower()

        if not normalized_request:
            raise ValueError("A solicitação não pode estar vazia.")

        if "docker" in normalized_request:
            return self._create_docker_plan()

        raise ValueError("Ainda não sei criar um plano para essa solicitação.")

    def _create_docker_plan(self) -> Plan:
        plan = Plan(
            goal="Instalar e configurar o Docker",
            estimated_seconds=240,
            risk=RiskLevel.HIGH,
        )

        plan.add_step(
            PlanStep(
                title="Atualizar repositórios",
                description="Atualiza os índices de pacotes do Ubuntu.",
                command=["sudo", "apt", "update"],
            )
        )

        plan.add_step(
            PlanStep(
                title="Instalar Docker",
                description="Instala o pacote Docker disponível nos repositórios do Ubuntu.",
                command=["sudo", "apt", "install", "-y", "docker.io"],
            )
        )

        plan.add_step(
            PlanStep(
                title="Habilitar o serviço",
                description="Habilita e inicia o Docker imediatamente.",
                command=[
                    "sudo",
                    "systemctl",
                    "enable",
                    "--now",
                    "docker",
                ],
            )
        )

        plan.add_step(
            PlanStep(
                title="Verificar instalação",
                description="Confirma que o Docker foi instalado corretamente.",
                command=["docker", "--version"],
            )
        )

        return plan
