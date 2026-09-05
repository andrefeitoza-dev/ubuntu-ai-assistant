import pytest

from ubuntu_ai.fast_path import AssistantIdentityResponder


@pytest.mark.parametrize(
    "phrase",
    (
        "Quem é você?",
        "Qual é o seu nome?",
        "Se apresente",
        "Fale sobre você.",
    ),
)
def test_assistant_introduces_itself_locally(phrase: str) -> None:
    response = AssistantIdentityResponder().respond(phrase)

    assert response is not None
    assert response.startswith("Eu sou o Ubuntu AI Assistant")
    assert "Ollama local" in response
    assert "o que você pode fazer?" in response


def test_unrelated_request_is_not_claimed() -> None:
    assert AssistantIdentityResponder().respond("Explique Docker") is None
