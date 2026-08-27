from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ubuntu_ai.fast_path.capabilities import CapabilityCatalog

OUTPUT = Path("docs/validation/v2.1-capability-homologation.md")
RESULTS = Path("docs/validation/v2.1-capability-results.json")
EXPECTED_TOPICS = 20
EXPECTED_CASES = 39
NEGATIVE_CASES = (
    ("N01", "Solicitação vazia"),
    ("N02", "Categoria de ajuda inexistente"),
    ("N03", "Dependência externa indisponível"),
    ("N04", "Cancelamento de operação"),
    ("N05", "Bloqueio de ação sensível sem confirmação"),
    ("N06", "Consulta remota sem destino selecionado"),
    ("N07", "Falha de conexão SSH"),
    ("N08", "Preservação do destino local após erro remoto"),
)
VALID_STATUSES = frozenset(
    {
        "PENDENTE",
        "APROVADO",
        "LIMITAÇÃO",
        "FALHOU",
    }
)


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


def expected_result_ids() -> frozenset[str]:
    announced = {f"H{number:02}" for number in range(1, EXPECTED_CASES + 1)}
    negative = {identifier for identifier, _scenario in NEGATIVE_CASES}
    return frozenset(announced | negative)


def load_results() -> dict[str, dict[str, str]]:
    if not RESULTS.is_file():
        return {}

    try:
        raw: Any = json.loads(RESULTS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Resultados de homologação inválidos: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError("Resultados de homologação devem formar um objeto JSON.")

    unknown = set(raw) - expected_result_ids()
    if unknown:
        raise ValueError(
            "Resultados possuem identificadores desconhecidos: " + ", ".join(sorted(unknown))
        )

    results: dict[str, dict[str, str]] = {}
    for identifier, payload in raw.items():
        if not isinstance(payload, dict):
            raise ValueError(f"Resultado inválido para {identifier}.")

        status = payload.get("status")
        evidence = payload.get("evidence")

        if status not in VALID_STATUSES:
            raise ValueError(f"Status inválido para {identifier}: {status}")
        if not isinstance(evidence, str) or not evidence.strip():
            raise ValueError(f"Evidência ausente para {identifier}.")

        results[identifier] = {
            "status": status,
            "evidence": evidence.strip(),
        }

    return results


def escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_matrix() -> str:
    validate_catalog()
    topics = CapabilityCatalog().topics
    results = load_results()
    counts = {status: 0 for status in VALID_STATUSES}

    def result_for(identifier: str) -> tuple[str, str]:
        payload = results.get(
            identifier,
            {"status": "PENDENTE", "evidence": "—"},
        )
        status = payload["status"]
        evidence = payload["evidence"]
        counts[status] += 1
        return status, evidence

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
            identifier = f"H{case_number:02}"
            status, evidence = result_for(identifier)
            lines.append(
                "| "
                f"{identifier} | "
                f"{topic.code}. {escape(topic.title)} | "
                f"{escape(example)} | "
                f"{escape(topic.availability)} | "
                f"{escape(topic.risk)} | "
                f"{escape(topic.confirmation)} | "
                f"{status} | {escape(evidence)} |"
            )

    lines.extend(
        (
            "",
            "## Casos complementares obrigatórios",
            "",
            "| ID | Cenário | Resultado | Evidência |",
            "|---|---|---|---|",
        )
    )

    for identifier, scenario in NEGATIVE_CASES:
        status, evidence = result_for(identifier)
        lines.append(f"| {identifier} | {escape(scenario)} | {status} | {escape(evidence)} |")

    lines.extend(
        (
            "",
            "## Resumo final",
            "",
            f"- Casos anunciados: {EXPECTED_CASES};",
            f"- casos negativos complementares: {len(NEGATIVE_CASES)};",
            f"- total previsto: {EXPECTED_CASES + len(NEGATIVE_CASES)};",
            f"- aprovados: {counts['APROVADO']};",
            f"- limitações: {counts['LIMITAÇÃO']};",
            f"- falhas: {counts['FALHOU']};",
            f"- pendentes: {counts['PENDENTE']}.",
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

    results = load_results()
    approved = sum(payload["status"] == "APROVADO" for payload in results.values())
    pending = (
        EXPECTED_CASES
        + len(NEGATIVE_CASES)
        - len(results)
        + sum(payload["status"] == "PENDENTE" for payload in results.values())
    )
    print(
        f"Matriz aprovada: {EXPECTED_TOPICS} tópicos, "
        f"{EXPECTED_CASES} casos anunciados, "
        f"{approved} resultados aprovados e {pending} pendentes."
    )


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
