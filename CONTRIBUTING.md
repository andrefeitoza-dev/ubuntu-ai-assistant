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

## Validação obrigatória

```bash
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
uv run pytest -q
uv run python scripts/check_architecture.py
git diff --check
```

Alterações na integração VS Code também exigem:

```bash
cd integrations/vscode
npm test
```

## Commits e Pull Requests

- use uma branch específica, como `feature/nome` ou `fix/nome`;
- mantenha o commit focado e com mensagem descritiva;
- informe riscos, compatibilidade e evidências no Pull Request;
- não inclua wheels, ambientes virtuais, bancos ou arquivos XDG;
- mudanças públicas precisam atualizar documentação e testes.

## Regras

- Preserve os contratos públicos existentes ou documente a mudança.
- Inclua testes para correções e funcionalidades quando aplicável.
- Não permita execução sem confirmação quando a política exigir aprovação.
- Mantenha documentação e changelog alinhados com mudanças relevantes.
- Nunca inclua segredos, tokens, bancos locais ou dados pessoais no commit.
- Plugins permanecem não confiáveis até aprovação explícita.
- Integrações não podem abrir shell nem contornar o executor controlado.
