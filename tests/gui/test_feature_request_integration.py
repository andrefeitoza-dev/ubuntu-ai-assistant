from pathlib import Path

from ubuntu_ai.gui.app import UbuntuAIApp
from ubuntu_ai.gui.backend import GUIBackend


def test_backend_recognizes_gui_coordinated_requests() -> None:
    assert GUIBackend.is_remote_diagnostic_request("Diagnostique o servidor selecionado.")
    assert GUIBackend.is_cancel_selected_automation_request("Cancele a tarefa selecionada.")


def test_natural_specialist_requests_create_multi_agent_goals() -> None:
    assert UbuntuAIApp._multi_agent_request("Analise este problema de rede.") == "problema de rede"
    assert UbuntuAIApp._multi_agent_request("Diagnostique a falta de espaço.") == "falta de espaço"


def test_submit_delegates_selected_remote_and_automation_requests() -> None:
    source = Path("src/ubuntu_ai/gui/app.py").read_text(encoding="utf-8")

    assert "is_remote_diagnostic_request(request)" in source
    assert 'self._automation_action("cancel")' in source
    assert "self._start_remote_diagnostics()" in source
