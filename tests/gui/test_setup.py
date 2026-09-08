import inspect
from types import SimpleNamespace

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
    assert 'self.root.geometry("640x720")' in source
    assert "Usar este modelo" in source
    assert "self._setup.select_model(model)" in source


class FakeWidget:
    def __init__(self) -> None:
        self.options = {}

    def configure(self, **options) -> None:
        self.options.update(options)


def _setup_app(*, model_available: bool, neural_available: bool):
    app = object.__new__(setup.SetupApp)
    app._natural_voice_setup = SimpleNamespace(
        available=lambda: model_available,
        model_path=SimpleNamespace(),
    )
    app.natural_voice_detail = FakeWidget()
    app.natural_voice_button = FakeWidget()
    app._queue = SimpleNamespace(put=lambda item: None)
    return app, neural_available


def test_natural_voice_card_reports_ready_runtime(monkeypatch) -> None:
    app, neural_available = _setup_app(model_available=True, neural_available=True)
    monkeypatch.setattr(
        setup,
        "VoiceOutputService",
        lambda model_path: SimpleNamespace(neural_available=neural_available),
    )

    app._display_natural_voice_status()

    assert "instalada" in app.natural_voice_detail.options["text"]
    assert app.natural_voice_button.options["text"] == "Voz natural pronta"


def test_natural_voice_card_offers_download_when_missing(monkeypatch) -> None:
    app, neural_available = _setup_app(model_available=False, neural_available=False)
    monkeypatch.setattr(
        setup,
        "VoiceOutputService",
        lambda model_path: SimpleNamespace(neural_available=neural_available),
    )

    app._display_natural_voice_status()

    assert "Baixe" in app.natural_voice_detail.options["text"]
    assert "58 MB" in app.natural_voice_button.options["text"]


def test_natural_voice_worker_reports_success_and_failure() -> None:
    events = []
    app, _ = _setup_app(model_available=False, neural_available=False)
    app._queue = SimpleNamespace(put=events.append)
    app._natural_voice_setup = SimpleNamespace(install=lambda: None)

    app._natural_voice_download_worker()
    assert events == [("natural-voice-status", True)]

    def fail():
        raise RuntimeError("download indisponível")

    events.clear()
    app._natural_voice_setup = SimpleNamespace(install=fail)
    app._natural_voice_download_worker()
    assert events == [("natural-voice-error", "download indisponível")]
