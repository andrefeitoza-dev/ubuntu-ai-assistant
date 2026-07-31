from io import StringIO

from rich.console import Console

from ubuntu_ai.agent_loop.models import LoopSnapshot, LoopState
from ubuntu_ai.tui.app import TerminalApp


class FakeController:
    def snapshot(self) -> LoopSnapshot:
        return LoopSnapshot(
            goal="",
            state=LoopState.IDLE,
            iteration=0,
            pending_plan=None,
            records=(),
            events=(),
        )


class FakeMemoryService:
    def __init__(self) -> None:
        self.limit: int | None = None

    def recent_executions(self, *, limit: int) -> tuple[object, ...]:
        self.limit = limit
        return ()


class FakePluginRegistry:
    def all(self) -> tuple[object, ...]:
        return ()


def test_terminal_commands_render_without_starting_goal() -> None:
    answers = iter((":status", ":history", ":plugins", ":help", ":quit"))
    output = StringIO()
    memory = FakeMemoryService()
    app = TerminalApp(
        controller=FakeController(),  # type: ignore[arg-type]
        memory_service=memory,  # type: ignore[arg-type]
        plugin_registry=FakePluginRegistry(),  # type: ignore[arg-type]
        console=Console(file=output, force_terminal=False, width=100),
        input_reader=lambda _: next(answers),
    )

    app.run()

    rendered = output.getvalue()
    assert "Estado do Agent Loop" in rendered
    assert "Nenhuma execução persistida" in rendered
    assert "Nenhum plugin carregado" in rendered
    assert memory.limit == 10
