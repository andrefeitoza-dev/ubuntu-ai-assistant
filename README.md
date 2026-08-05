# Ubuntu AI Assistant

Framework local e extensível para construir agentes inteligentes voltados à administração segura de sistemas Linux, com foco inicial no Ubuntu.

O Ubuntu AI transforma solicitações em linguagem natural em planos auditáveis, apresenta um preview, aplica políticas de risco, solicita confirmação quando necessário e executa comandos de forma controlada.

## Recursos da v0.6.0

- planejamento determinístico e por IA local com Ollama;
- preview em modo seguro antes da execução;
- confirmação humana e políticas de execução;
- contexto do sistema, memória, conversa e aprendizado;
- conhecimento local com busca e RAG;
- skills, plugins e seleção de ferramentas;
- reflexão antes e depois da execução;
- Agent Loop com replanejamento controlado;
- TUI com Rich, spinner e resumo de benchmark;
- logging rotativo, diagnóstico de IA e benchmark;
- SDK Python para integração com outras aplicações;
- suíte com mais de 300 testes automatizados.

## Requisitos

- Ubuntu ou distribuição Linux compatível;
- Python 3.12 ou superior;
- Ollama para funcionalidades de IA local.

Para máquinas com aproximadamente 8 GB de RAM:

```bash
ollama pull qwen2.5:3b
```

## Instalação com pipx

Depois de baixar ou clonar o projeto:

```bash
pipx install .
ubuntu-ai version
ubuntu-ai doctor
```

Para desenvolvimento:

```bash
uv sync --all-extras --dev
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest
```

## Uso rápido

```bash
ubuntu-ai doctor
ubuntu-ai diagnose-ai
ubuntu-ai benchmark
ubuntu-ai plan "mostrar o diretório atual"
ubuntu-ai tui
```

Na TUI:

```text
Objetivo> mostrar o diretório atual
Confirmar este plano? y
```

## Fluxo seguro

```text
Objetivo → Contexto → Planejamento → Preview → Reflexão → Confirmação
        → Preflight → Política → Execução → Memória → Aprendizado
```

Nenhum plano ou replanejamento deve executar sem passar pelas regras de confirmação aplicáveis.

## SDK

```python
from ubuntu_ai import UbuntuAI

assistant = UbuntuAI()
result = assistant.plan("mostrar o diretório atual")
print(result.rendered_preview)
```

## Documentação

- `docs/architecture.md` — arquitetura atual;
- `docs/project-context.md` — contexto técnico do projeto;
- `docs/roadmap.md` — roadmap;
- `docs/releases/` — notas das RCs e releases;
- `docs/adr/` — decisões arquiteturais;
- `CONTRIBUTING.md` — guia para contribuições.

## Estado do projeto

A versão `0.6.0` consolida a fundação do framework. A próxima fase evoluirá o runtime inteligente, o replanejamento e as APIs públicas para agentes Linux.

## Licença

MIT.
