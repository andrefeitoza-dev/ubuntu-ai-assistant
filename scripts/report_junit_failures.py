from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


def _escape(value: str) -> str:
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def report(path: Path) -> int:
    root = ET.parse(path).getroot()
    failures = []
    for case in root.iter("testcase"):
        problem = case.find("failure")
        if problem is None:
            problem = case.find("error")
        if problem is None:
            continue
        identifier = ".".join(
            part for part in (case.get("classname", ""), case.get("name", "")) if part
        )
        details = (problem.get("message") or problem.text or "Falha sem detalhes.").strip()
        message = _escape(f"{identifier}: {details[:4000]}")
        print(f"::error title=Teste automatizado reprovado::{message}")
        failures.append(identifier)
    if not failures:
        print(
            "::error title=Suíte automatizada reprovada::O pytest falhou sem caso JUnit associado."
        )
    return 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Publica falhas JUnit como anotações do CI.")
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    raise SystemExit(report(args.report))


if __name__ == "__main__":
    main()
