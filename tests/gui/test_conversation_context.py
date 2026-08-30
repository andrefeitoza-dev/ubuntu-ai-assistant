from types import SimpleNamespace

from ubuntu_ai.execution.mode import execution_mode
from ubuntu_ai.execution.permissions import capability_permissions
from ubuntu_ai.gui.backend import GUIBackend
from ubuntu_ai.gui.conversation_context import ReadOnlyConversationContext
from ubuntu_ai.interaction import InteractionDecision, InteractionRoute


def test_repeats_only_last_read_only_query_on_same_target() -> None:
    context = ReadOnlyConversationContext()
    context.remember("quanto espaço livre tenho?", target="local")

    resolution = context.resolve("Repita essa consulta.", target="local")

    assert resolution.request == "quanto espaço livre tenho?"
    assert resolution.message is None


def test_does_not_carry_context_between_computers() -> None:
    context = ReadOnlyConversationContext()
    context.remember("qual a versão do Ubuntu?", target="local")

    resolution = context.resolve("mostre novamente", target="servidor")

    assert resolution.request is None
    assert "destino mudou" in resolution.message


def test_refuses_ambiguous_action_reference() -> None:
    resolution = ReadOnlyConversationContext().resolve("Abra o primeiro.", target="local")

    assert resolution.request is None
    assert "referência ambígua" in resolution.message


def test_explains_when_there_is_no_previous_query() -> None:
    resolution = ReadOnlyConversationContext().resolve("consulte novamente", target="local")

    assert resolution.request is None
    assert "Não há uma consulta" in resolution.message


def test_backend_routes_repeated_local_query_without_turning_it_into_action() -> None:
    calls: list[str] = []
    backend = GUIBackend.__new__(GUIBackend)
    backend._selected_target = "local"
    backend._conversation_context = ReadOnlyConversationContext()
    backend._router = SimpleNamespace(
        route=lambda request: (
            calls.append(request) or InteractionDecision(InteractionRoute.LOCAL, "resposta segura")
        )
    )

    backend.route("que dia é hoje?")
    repeated = backend.route("repita essa consulta")

    assert calls == ["que dia é hoje?", "que dia é hoje?"]
    assert repeated.route is InteractionRoute.LOCAL


def test_backend_controls_and_reports_global_simulation() -> None:
    backend = GUIBackend.__new__(GUIBackend)
    backend._selected_target = "local"
    backend._conversation_context = ReadOnlyConversationContext()
    execution_mode.set_simulation(False)
    try:
        enabled = backend.route("Ative o modo de simulação.")
        status = backend.route("Mostre o modo de execução.")
        disabled = backend.route("Desative o modo de simulação.")

        assert "ativado" in enabled.response
        assert "ativado" in status.response
        assert "desativado" in disabled.response
        assert execution_mode.simulation is False
    finally:
        execution_mode.set_simulation(False)


def test_backend_manages_additional_capability_permissions() -> None:
    backend = GUIBackend.__new__(GUIBackend)
    backend._selected_target = "local"
    backend._conversation_context = ReadOnlyConversationContext()
    capability_permissions.set_allowed("desktop", allowed=True)
    try:
        blocked = backend.route("Bloqueie aplicativos.")
        status = backend.route("Mostre as permissões do assistente.")
        allowed = backend.route("Permita aplicativos.")

        assert "desativada" in blocked.response
        assert "desktop" in status.response
        assert "reativada" in allowed.response
        assert "desktop" not in capability_permissions.denied
    finally:
        capability_permissions.set_allowed("desktop", allowed=True)
