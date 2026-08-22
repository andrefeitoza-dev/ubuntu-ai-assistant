from __future__ import annotations

import argparse
from time import time_ns

from ubuntu_ai.gui.backend import GUIBackend


def validate(target: str) -> None:
    backend = GUIBackend()
    host = backend.select_target(target)
    if host.name.lower() == "local":
        raise ValueError("A validação exige um destino SSH explícito.")

    goal = backend.plan_multi_agent(
        "diagnóstico completo",
        goal_id=f"release-v2-ssh-{time_ns()}",
    )
    if (
        goal.context["environment"] != "remote"
        or str(goal.context["target"]).lower() != host.name.lower()
    ):
        raise RuntimeError("O plano não preservou o destino SSH selecionado.")

    backend.register_multi_agent(goal)
    report = backend.execute_multi_agent(goal, confirmed=True)
    expected = {
        ("uptime",),
        ("ip", "route"),
        ("df", "-h"),
        ("systemctl", "--failed", "--no-legend", "--plain"),
    }
    commands = {result.command for result in report.results}
    if report.target.lower() != host.name.lower() or commands != expected or not report.successful:
        raise RuntimeError("O diagnóstico multiagente SSH não foi concluído integralmente.")

    records = backend.remote_audit_records()
    completed = {record.command for record in records if record.status == "completed"}
    if not expected <= completed:
        raise RuntimeError("A auditoria SSH não contém todos os comandos concluídos.")

    print(f"Diagnóstico multiagente SSH aprovado: {host.name}")
    for result in report.results:
        print(f"- {' '.join(result.command)}: código {result.return_code}")
    print(f"Registros de auditoria disponíveis: {len(records)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Valida o diagnóstico multiagente em um host SSH cadastrado."
    )
    parser.add_argument("target", help="Nome do destino SSH no inventário do Ubuntu AI.")
    args = parser.parse_args()
    validate(args.target)


if __name__ == "__main__":
    main()
