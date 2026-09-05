import inspect

from ubuntu_ai.distribution.first_run import FirstRunStatus
from ubuntu_ai.gui import setup
from ubuntu_ai.gui.setup import setup_message


def test_setup_guides_missing_ollama_to_official_installation() -> None:
    title, detail = setup_message(FirstRunStatus(False, False, False))

    assert "Instale o Ollama" in title
    assert "instruções oficiais" in detail


def test_setup_warns_before_large_model_download() -> None:
    title, detail = setup_message(FirstRunStatus(True, True, False))

    assert "Baixe o modelo" in title
    assert "alguns gigabytes" in detail
    assert "autorizar" in detail


def test_setup_reports_ready_runtime() -> None:
    title, detail = setup_message(FirstRunStatus(True, True, True))

    assert title == "Configuração concluída"
    assert "está pronto" in detail


def test_graphical_setup_includes_authorized_voice_model_download() -> None:
    source = inspect.getsource(setup.SetupApp)

    assert "Baixar modelo de voz (31 MB)" in source
    assert "VoiceModelSetup" in source
    assert "validando a integridade" in source
    assert 'self.root.geometry("640x650")' in source
