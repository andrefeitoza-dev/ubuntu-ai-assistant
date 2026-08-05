# Ubuntu AI Assistant

Assistente local para administração segura de sistemas Ubuntu, com planejamento por linguagem natural, preview, confirmação explícita e execução controlada.

## Estado atual

O projeto está em preparação para **v0.6.0 RC1** e já oferece:

- planejamento determinístico e por IA local;
- integração com Ollama;
- TUI interativa;
- avaliação de risco, reflexão e preflight;
- seleção de ferramentas e sistema de skills;
- execução controlada com confirmação humana;
- memória, conversa, conhecimento local, RAG e aprendizado;
- Agent Loop com replanejamento seguro;
- Plugin SDK versionado;
- diagnóstico do runtime de IA;
- suíte com mais de 260 testes.

## Requisitos

- Ubuntu ou distribuição Linux compatível;
- Python 3.12 ou superior;
- `uv`;
- Ollama para planejamento por IA.

Modelo recomendado para máquinas com aproximadamente 8 GB de RAM:

```bash
ollama pull qwen2.5:3b
```

## Desenvolvimento

```bash
uv sync --extra dev
uv run ruff check src tests
uv run pytest
```

## Comandos principais

```bash
ubuntu-ai doctor
ubuntu-ai diagnose-ai
ubuntu-ai plan "mostrar o diretório atual"
ubuntu-ai tui
```

## Fluxo seguro

```text
Objetivo → Plano → Preview → Reflexão → Confirmação
        → Preflight → Política → Execução → Memória → Aprendizado
```

Nenhum plano novo ou replanejado deve executar sem confirmação quando a política exigir aprovação.

## Exemplo pela TUI

```bash
ubuntu-ai tui
```

```text
Objetivo> mostrar o diretório atual
Confirmar este plano? y
```

## Documentação

- `docs/architecture.md` — arquitetura atual;
- `docs/roadmap.md` — fases e próximas entregas;
- `docs/rc1/RC1.1-architectural-audit.md` — auditoria da RC1;
- `docs/adr/` — decisões arquiteturais.

## Licença

MIT.
