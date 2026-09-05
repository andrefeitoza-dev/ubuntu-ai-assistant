from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.executor.preview import PreviewBuilder
from ubuntu_ai.planner.builtin.maintenance import SafeMaintenancePlanner


def test_cleanup_uses_closed_privileged_commands_and_high_risk() -> None:
    plan = SafeMaintenancePlanner().try_create_plan("Faça uma limpeza segura de pacotes.")

    assert plan is not None
    assert plan.risk is RiskLevel.HIGH
    assert [tuple(step.command) for step in plan.steps] == [
        ("pkexec", "apt-get", "autoremove", "-y"),
        ("pkexec", "apt-get", "clean"),
    ]


def test_package_update_does_not_use_dist_upgrade() -> None:
    plan = SafeMaintenancePlanner().try_create_plan("Atualize os pacotes")

    assert plan is not None
    assert plan.risk is RiskLevel.HIGH
    commands = [tuple(step.command) for step in plan.steps]
    assert ("pkexec", "apt-get", "upgrade", "-y") in commands
    assert all("dist-upgrade" not in command for command in commands)


def test_firewall_activation_is_critical_and_warns_about_network() -> None:
    plan = SafeMaintenancePlanner().try_create_plan("Ative o firewall")

    assert plan is not None
    assert plan.risk is RiskLevel.CRITICAL
    assert tuple(plan.steps[0].command) == ("pkexec", "ufw", "enable")
    assert "conexões" in plan.steps[0].description


def test_unknown_maintenance_request_is_not_claimed() -> None:
    assert SafeMaintenancePlanner().try_create_plan("configure regras avançadas") is None


def test_all_maintenance_plans_build_execution_preview() -> None:
    planner = SafeMaintenancePlanner()

    for request in (
        "Faça uma limpeza segura de pacotes",
        "Atualize os pacotes",
        "Ative o firewall",
    ):
        plan = planner.try_create_plan(request)
        assert plan is not None
        preview = PreviewBuilder().build(plan)
        assert preview.steps
