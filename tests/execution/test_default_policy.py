from ubuntu_ai.execution import ExecutionRequest
from ubuntu_ai.execution.default_policy import DefaultExecutionPolicy


def test_policy_allows_safe_command() -> None:
    policy = DefaultExecutionPolicy()

    decision = policy.evaluate(ExecutionRequest(command="ls -la"))

    assert decision.allowed is True
    assert decision.reason == "Comando autorizado."


def test_policy_blocks_rm() -> None:
    policy = DefaultExecutionPolicy()

    decision = policy.evaluate(ExecutionRequest(command="rm -rf /"))

    assert decision.allowed is False
    assert "bloqueado" in decision.reason


def test_policy_blocks_empty_command() -> None:
    policy = DefaultExecutionPolicy()

    decision = policy.evaluate(ExecutionRequest(command=""))

    assert decision.allowed is False
    assert decision.reason == "Comando vazio."


def test_policy_blocks_shutdown() -> None:
    policy = DefaultExecutionPolicy()

    decision = policy.evaluate(ExecutionRequest(command="shutdown now"))

    assert decision.allowed is False


def test_policy_allows_trusted_desktop_application() -> None:
    decision = DefaultExecutionPolicy().evaluate(ExecutionRequest(command="gtk-launch firefox"))

    assert decision.allowed is True


def test_policy_blocks_unknown_desktop_application() -> None:
    decision = DefaultExecutionPolicy().evaluate(
        ExecutionRequest(command="gtk-launch unknown.desktop")
    )

    assert decision.allowed is False
    assert "Aplicativo bloqueado" in decision.reason


def test_policy_allows_http_site() -> None:
    decision = DefaultExecutionPolicy().evaluate(
        ExecutionRequest(command="xdg-open https://ubuntu.com")
    )

    assert decision.allowed is True


def test_policy_blocks_unsafe_uri_scheme() -> None:
    decision = DefaultExecutionPolicy().evaluate(
        ExecutionRequest(command="xdg-open javascript:alert(1)")
    )

    assert decision.allowed is False
    assert "Destino bloqueado" in decision.reason
