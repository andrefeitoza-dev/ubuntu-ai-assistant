# Contribuindo com o Ubuntu AI

Obrigado por contribuir com o Ubuntu AI Assistant.

## Requisitos

- Python 3.12 ou superior;
- `uv`;
- Git;
- Ollama apenas para testes de integração com IA local.

## Preparação

```bash
git clone <url-do-repositorio>
cd ubuntu-ai-assistant
uv sync --all-extras --dev
uv run pre-commit install
```

## Fluxo de desenvolvimento

```bash
git checkout -b feature/minha-feature
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest
git add .
git commit -m "feat: descreva a alteração"
```

Abra um Pull Request descrevendo objetivo, impacto e validação executada.

## Regras

- Preserve os contratos públicos existentes ou documente a mudança.
- Inclua testes para correções e funcionalidades quando aplicável.
- Não permita execução sem confirmação quando a política exigir aprovação.
- Mantenha documentação e changelog alinhados com mudanças relevantes.
- Nunca inclua segredos, tokens, bancos locais ou dados pessoais no commit.
