# Guia do Desenvolvedor

## Estrutura

- application
- agent_loop
- planner
- execution_intelligence
- reflection
- learning
- hardening
- tui
- distribution
- plugins
- agents
- integrations/vscode

## Convenções

- Ruff
- Pytest
- Dependency Injection
- Clean Architecture

## Verificação

```bash
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
uv run pytest -q
uv run python scripts/check_architecture.py
uv build
uv run python scripts/release_artifacts.py validate dist
uv run python scripts/release_artifacts.py checksums dist
```

Consulte o [processo de release](release-process.md) para auditoria, checksums,
proveniência e publicação dos artefatos.

## Integrações

Integrações externas devem depender apenas de entry points e APIs públicas.
Não devem importar o container, duplicar políticas, abrir shell ou confirmar
ações em nome do usuário.

## Plugins

Consulte [compatibilidade de plugins](plugin-compatibility.md). Mudanças
incompatíveis exigem nova versão da API e orientação de migração.
