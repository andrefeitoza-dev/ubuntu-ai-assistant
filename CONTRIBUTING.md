# Contributing

Obrigado por contribuir com o UbuntuAI.

## Requisitos

- Python 3.12
- uv
- Ruff
- Pytest

## Fluxo

git checkout -b feature/minha-feature

uv sync

uv run ruff check

uv run pytest

git commit

git push

Abra um Pull Request.

Todas as alterações devem possuir testes quando aplicável.
