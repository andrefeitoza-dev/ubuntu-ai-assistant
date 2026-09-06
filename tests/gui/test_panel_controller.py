from types import SimpleNamespace

from ubuntu_ai.gui.panel_controller import PanelControllerMixin


def test_update_check_starts_shared_care_query_without_blocking(monkeypatch) -> None:
    controller = PanelControllerMixin()
    controller._backend = SimpleNamespace(is_update_query=lambda request: request == "updates")
    controller._begin_operation = lambda _label: 7
    started = []

    class Thread:
        def __init__(self, *, target, args, daemon) -> None:
            started.append((target, args, daemon))

        def start(self) -> None:
            started.append("started")

    monkeypatch.setattr("ubuntu_ai.gui.panel_controller.threading.Thread", Thread)

    assert controller._start_update_check_if_requested("other") is False
    assert controller._start_update_check_if_requested("updates") is True
    assert started[-1] == "started"
    assert started[0][1:] == ((7,), True)


def test_update_query_delivers_shared_report() -> None:
    controller = PanelControllerMixin()
    delivered = []
    controller._backend = SimpleNamespace(available_updates=lambda: "pacote → versão")
    controller._post_to_ui = lambda *args: delivered.append(args)

    controller._start_update_query(4)

    assert delivered == [(controller._deliver_update_query, 4, "pacote → versão")]


def test_update_query_finishes_operation_and_labels_care_route() -> None:
    controller = PanelControllerMixin()
    messages = []
    controller._operation_generation = 4
    controller._set_busy = lambda state: messages.append(("busy", state))
    controller._add_system_message = lambda message, color: messages.append((message, color))
    controller.request_entry = SimpleNamespace(focus_set=lambda: messages.append("focus"))

    controller._deliver_update_query(4, "duas atualizações")

    assert ("busy", False) in messages
    assert any("Rota local · Cuidados" in item[0] for item in messages if isinstance(item, tuple))
    assert "focus" in messages


def test_stale_update_query_is_ignored() -> None:
    controller = PanelControllerMixin()
    controller._operation_generation = 5

    controller._deliver_update_query(4, "resultado antigo")
