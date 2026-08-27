from __future__ import annotations

from ubuntu_ai.agent_loop.models import LoopSnapshot, LoopState


def friendly_error(message: str) -> str:
    """Transforma erros técnicos conhecidos em orientações para o usuário."""

    normalized = message.strip().lower()

    if not normalized:
        return "O backend não informou detalhes. Tente novamente."

    if "ollama" in normalized or "connection refused" in normalized:
        return "Não foi possível conectar ao Ollama. Verifique se o serviço está em execução."

    if "timeout" in normalized or "timed out" in normalized:
        return (
            "A operação excedeu o tempo esperado. "
            "Você pode tentar novamente com uma solicitação mais direta."
        )

    if "model" in normalized and ("not found" in normalized or "não encontrado" in normalized):
        return (
            "O modelo de IA configurado não foi encontrado. "
            "Confira os modelos disponíveis no Ollama."
        )

    if "permission denied" in normalized or "permissão negada" in normalized:
        return (
            "O Ubuntu negou permissão para essa operação. "
            "Revise o plano e as permissões necessárias."
        )

    return message.strip()


def format_duration(duration: float) -> str:
    """Formata latência usando a escala mais legível."""

    if duration < 0.001:
        return f"{duration * 1_000_000:.0f} µs"
    if duration < 1.0:
        return f"{duration * 1000:.1f} ms"
    return f"{duration:.2f} s"


def command_text(command: object) -> str:
    """Converte comandos estruturados em texto para apresentação."""

    if isinstance(command, (list, tuple)):
        return " ".join(str(item) for item in command)

    return str(command)


def state_message(snapshot: LoopSnapshot) -> str:
    """Retorna a mensagem pública correspondente ao estado do loop."""

    messages = {
        LoopState.COMPLETED: "✓ Operação concluída com sucesso.",
        LoopState.BLOCKED: ("A operação foi bloqueada pela política de segurança."),
        LoopState.FAILED: "Não foi possível concluir a operação.",
        LoopState.CANCELLED: "Operação cancelada.",
        LoopState.WAITING_CONFIRMATION: ("O plano aguarda sua confirmação."),
    }

    return messages.get(
        snapshot.state,
        f"Estado: {snapshot.state.value}",
    )


def risk_label(risk: str) -> str:
    """Traduz o nível de risco para um rótulo legível."""

    labels = {
        "low": "Risco baixo",
        "medium": "Risco médio",
        "high": "Risco alto",
        "critical": "Risco crítico",
    }

    return labels.get(
        risk.lower(),
        f"Risco {risk}",
    )


def risk_color(
    risk: str,
    *,
    success: str,
    warning: str,
    error: str,
) -> str:
    """Seleciona a cor do tema associada ao nível de risco."""

    normalized = risk.lower()

    if normalized == "low":
        return success

    if normalized == "medium":
        return warning

    return error
