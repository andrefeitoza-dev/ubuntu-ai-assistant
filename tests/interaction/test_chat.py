from ubuntu_ai.benchmark import BenchmarkService
from ubuntu_ai.interaction import ChatService


class FakeOllamaService:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, prompt: str, model: str) -> str:
        self.prompts.append(prompt)
        assert model == "qwen2.5:3b"
        return "Resposta natural."


class FakeConversationEngine:
    def __init__(self) -> None:
        self.user: list[str] = []
        self.assistant: list[str] = []

    def history_for_prompt(self, *, session_id: str) -> tuple[str, ...]:
        assert session_id == "session-test"
        return ("user: pergunta anterior", "assistant: resposta anterior")

    def remember_user(self, *, session_id: str, content: str) -> None:
        assert session_id == "session-test"
        self.user.append(content)

    def remember_assistant(self, *, session_id: str, content: str) -> None:
        assert session_id == "session-test"
        self.assistant.append(content)


def test_chat_uses_history_and_remembers_successful_exchange() -> None:
    ollama = FakeOllamaService()
    conversation = FakeConversationEngine()
    service = ChatService(
        service=ollama,  # type: ignore[arg-type]
        model="qwen2.5:3b",
        conversation_engine=conversation,  # type: ignore[arg-type]
        session_id="session-test",
    )

    response = service.ask("O que é Linux?")

    assert response.content == "Resposta natural."
    assert response.model == "qwen2.5:3b"
    assert response.route == "chat"
    assert "pergunta anterior" in ollama.prompts[0]
    assert "O que é Linux?" in ollama.prompts[0]
    assert "não afirme que executou comandos" in ollama.prompts[0]
    assert conversation.user == ["O que é Linux?"]
    assert conversation.assistant == ["Resposta natural."]


def test_chat_without_conversation_engine() -> None:
    ollama = FakeOllamaService()
    service = ChatService(
        service=ollama,  # type: ignore[arg-type]
        model="qwen2.5:3b",
    )

    assert service.ask("Olá").content == "Resposta natural."


def test_chat_records_generation_latency() -> None:
    benchmark = BenchmarkService()
    service = ChatService(
        service=FakeOllamaService(),  # type: ignore[arg-type]
        model="qwen2.5:3b",
        benchmark_service=benchmark,
    )

    response = service.ask("Olá")

    assert response.duration >= 0
    record = benchmark.report().records[0]
    assert record.operation == "interaction.chat"
    assert record.success is True
