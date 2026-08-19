from importlib import import_module
from types import SimpleNamespace

from typer.testing import CliRunner

from ubuntu_ai.cli.app import app
from ubuntu_ai.interaction import InteractionRoute

runner = CliRunner()
module = import_module("ubuntu_ai.cli.benchmark_routes")


class FakeRouter:
    def route(self, request: str):
        route = InteractionRoute.LOCAL if "dia" in request else InteractionRoute.ACTION
        if "Linux" in request:
            route = InteractionRoute.CHAT
        return SimpleNamespace(route=route, duration=0.0004)


class FakeChat:
    def ask(self, request: str):
        return SimpleNamespace(content="ok", duration=1.25, model="fake:1b")


def test_benchmark_routes_without_chat(monkeypatch) -> None:
    monkeypatch.setattr(module.container, "interaction_router", FakeRouter)

    result = runner.invoke(app, ["benchmark-routes"])

    assert result.exit_code == 0
    assert "Local" in result.stdout
    assert "Ação segura" in result.stdout
    assert "400 µs" in result.stdout


def test_benchmark_routes_can_measure_chat(monkeypatch) -> None:
    monkeypatch.setattr(module.container, "interaction_router", FakeRouter)
    monkeypatch.setattr(module.container, "chat_service", FakeChat)

    result = runner.invoke(app, ["benchmark-routes", "--include-chat"])

    assert result.exit_code == 0
    assert "primeira medição" in result.stdout
    assert "modelo aquecido" in result.stdout
    assert "1.25 s" in result.stdout
