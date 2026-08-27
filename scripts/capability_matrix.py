from __future__ import annotations

import argparse
from pathlib import Path

from ubuntu_ai.fast_path.capabilities import CapabilityCatalog

OUTPUT = Path("docs/validation/v2.1-capability-homologation.md")
EXPECTED_TOPICS = 20
EXPECTED_CASES = 39


def validate_catalog() -> None:
    topics = CapabilityCatalog().topics
    expected_codes = tuple(f"{number:02}" for number in range(1, 21))

    if len(topics) != EXPECTED_TOPICS:
        raise ValueError(
            f"Catálogo deve possuir {EXPECTED_TOPICS} tópicos; encontrados: {len(topics)}"
        )

    codes = tuple(topic.code for topic in topics)
    if codes != expected_codes:
        raise ValueError("Códigos do catálogo não são sequenciais: " + ", ".join(codes))

    case_count = sum(len(topic.examples) for topic in topics)
    if case_count != EXPECTED_CASES:
        raise ValueError(f"Matriz deve possuir {EXPECTED_CASES} casos; encontrados: {case_count}")

    for topic in topics:
        required = (
            topic.title,
            topic.kind,
            topic.risk,
            topic.confirmation,
            topic.availability,
        )
        if not all(value.strip() for value in required):
            raise ValueError(f"Metadados incompletos no tópico {topic.code}")
        if not topic.capabilities:
            raise ValueError(f"Tópico {topic.code} não possui capacidades")
        if not topic.examples:
            raise ValueError(f"Tópico {topic.code} não possui exemplos")


def escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_matrix() -> str:
    validate_catalog()
    topics = CapabilityCatalog().topics

    lines = [
        "# Matriz de homologação funcional — Ubuntu AI Assistant v2.1.0",
        "",
        "## Finalidade",
        "",
        "Esta matriz controla a validação dos 20 recursos anunciados no painel",
        "Recursos e ajuda. Cada pergunta deve ser executada pela interface gráfica",
        "no destino indicado, sem considerar uma resposta aprovada apenas porque",
        "o texto está presente no catálogo.",
        "",
        "## Critérios",
        "",
        "- `PENDENTE`: ainda não executado;",
        "- `APROVADO`: comportamento observado corresponde ao anunciado;",
        "- `LIMITAÇÃO`: comportamento parcial documentado;",
        "- `FALHOU`: resposta, rota, segurança ou apresentação incorreta;",
        "- ações sensíveis somente podem ser aprovadas quando a confirmação for",
        "  exigida corretamente;",
        "- testes SSH exigem um computador previamente cadastrado e autorizado.",
        "",
        "## Casos",
        "",
        (
            "| ID | Recurso | Pergunta | Disponibilidade | Risco | "
            "Confirmação | Resultado | Evidência |"
        ),
        "|---|---|---|---|---|---|---|---|",
    ]

    case_number = 0
    for topic in topics:
        for example in topic.examples:
            case_number += 1
            lines.append(
                "| "
                f"H{case_number:02} | "
                f"{topic.code}. {escape(topic.title)} | "
                f"{escape(example)} | "
                f"{escape(topic.availability)} | "
                f"{escape(topic.risk)} | "
                f"{escape(topic.confirmation)} | "
                "PENDENTE | — |"
            )

    lines.extend(
        (
            "",
            "## Casos complementares obrigatórios",
            "",
            "| ID | Cenário | Resultado | Evidência |",
            "|---|---|---|---|",
            "| N01 | Solicitação vazia | PENDENTE | — |",
            "| N02 | Categoria de ajuda inexistente | PENDENTE | — |",
            "| N03 | Dependência externa indisponível | PENDENTE | — |",
            "| N04 | Cancelamento de operação | PENDENTE | — |",
            "| N05 | Bloqueio de ação sensível sem confirmação | PENDENTE | — |",
            "| N06 | Consulta remota sem destino selecionado | PENDENTE | — |",
            "| N07 | Falha de conexão SSH | PENDENTE | — |",
            "| N08 | Preservação do destino local após erro remoto | PENDENTE | — |",
            "",
            "## Resumo final",
            "",
            "- Casos anunciados: 39;",
            "- casos negativos complementares: 8;",
            "- total previsto: 47;",
            "- aprovados: 0;",
            "- limitações: 0;",
            "- falhas: 0;",
            "- pendentes: 47.",
            "",
        )
    )

    return "\n".join(lines)


def write_matrix() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render_matrix(), encoding="utf-8")
    print(f"Matriz criada: {OUTPUT}")


def check_matrix() -> None:
    expected = render_matrix()
    if not OUTPUT.is_file():
        raise ValueError(f"Matriz ausente: {OUTPUT}")

    actual = OUTPUT.read_text(encoding="utf-8")
    if actual != expected:
        raise ValueError("Matriz de homologação está desatualizada. Execute com --write.")

    print(f"Matriz aprovada: {EXPECTED_TOPICS} tópicos, {EXPECTED_CASES} casos anunciados.")


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.write:
        write_matrix()
    else:
        check_matrix()


if __name__ == "__main__":
    main()
