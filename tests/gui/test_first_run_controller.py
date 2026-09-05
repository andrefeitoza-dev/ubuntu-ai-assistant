from __future__ import annotations

from types import SimpleNamespace

from ubuntu_ai.distribution.first_run import FirstRunStatus
from ubuntu_ai.gui.first_run_controller import FirstRunControllerMixin


def test_ready_runtime_does_not_show_setup_prompt(monkeypatch) -> None:
    prompts: list[object] = []
    monkeypatch.setattr(
        "ubuntu_ai.gui.first_run_controller.add_setup_prompt",
        lambda *args, **kwargs: prompts.append((args, kwargs)),
    )
    controller = FirstRunControllerMixin()
    controller.welcome = SimpleNamespace(winfo_exists=lambda: True)

    controller._deliver_ai_setup_status(FirstRunStatus(True, True, True))

    assert prompts == []


def test_incomplete_runtime_shows_graphical_setup_action(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def prompt(parent, **options):
        captured["parent"] = parent
        captured.update(options)
        return "prompt"

    monkeypatch.setattr("ubuntu_ai.gui.first_run_controller.add_setup_prompt", prompt)
    controller = FirstRunControllerMixin()
    controller.welcome = SimpleNamespace(winfo_exists=lambda: True)

    controller._deliver_ai_setup_status(FirstRunStatus(False, False, False))

    assert controller._setup_prompt == "prompt"
    assert captured["ollama_available"] is False
    assert captured["model"] == "qwen2.5:3b"
    assert callable(captured["on_configure"])
