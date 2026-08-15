from typing import Any

from ubuntu_ai.domain.plan import Plan, PlanStep, RiskLevel
from ubuntu_ai.executor.executor import Executor
from ubuntu_ai.services.shell import CommandResult
from ubuntu_ai.tools.base import Tool
from ubuntu_ai.tools.registry import ToolRegistry


class FakeShellTool(Tool):
    name = "shell"
    description = "Ferramenta shell usada nos testes."

    def __init__(self, return_codes: list[int] | None = None) -> None:
        self.executed_commands: list[list[str]] = []
        self._return_codes = return_codes or [0]

    def execute(self, **kwargs: Any) -> CommandResult:
        command = kwargs["command"]
        self.executed_commands.append(command)

        index = len(self.executed_commands) - 1
        return_code = self._return_codes[min(index, len(self._return_codes) - 1)]

        return CommandResult(
            command=" ".join(command),
            return_code=return_code,
            stdout="ok" if return_code == 0 else "",
            stderr="" if return_code == 0 else "erro",
        )


def create_plan() -> Plan:
    return Plan(
        goal="Executar teste",
        risk=RiskLevel.LOW,
        estimated_seconds=5,
        steps=[
            PlanStep(
                title="Primeira etapa",
                description="Executa o primeiro comando.",
                command=["echo", "primeiro"],
            ),
            PlanStep(
                title="Segunda etapa",
                description="Executa o segundo comando.",
                command=["echo", "segundo"],
            ),
        ],
    )


def test_executor_runs_steps_in_order() -> None:
    registry = ToolRegistry()
    shell_tool = FakeShellTool()
    registry.register(shell_tool)

    executor = Executor(registry)
    results = executor.execute(create_plan())

    assert len(results) == 2
    assert shell_tool.executed_commands == [
        ["echo", "primeiro"],
        ["echo", "segundo"],
    ]
    assert all(result.success for result in results)


def test_executor_stops_after_failure() -> None:
    registry = ToolRegistry()
    shell_tool = FakeShellTool(return_codes=[1, 0])
    registry.register(shell_tool)

    executor = Executor(registry)
    results = executor.execute(create_plan())

    assert len(results) == 1
    assert not results[0].success
    assert shell_tool.executed_commands == [["echo", "primeiro"]]


def test_executor_requires_registered_shell_tool() -> None:
    registry = ToolRegistry()
    executor = Executor(registry)

    try:
        executor.execute(create_plan())
    except KeyError as exc:
        assert "Ferramenta não encontrada" in str(exc)
    else:
        raise AssertionError("Era esperado KeyError")
