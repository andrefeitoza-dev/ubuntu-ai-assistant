# Ubuntu AI Assistant

## Project Context

### Status

Em desenvolvimento.

Arquitetura baseada em Clean Architecture e desenvolvimento incremental por Sprints.

---

# Objetivo

Desenvolver uma plataforma de administração inteligente para Ubuntu utilizando IA local (Ollama).

O sistema deverá:

- interpretar comandos em linguagem natural;
- gerar planos antes da execução;
- explicar riscos;
- solicitar confirmação;
- executar tarefas de forma segura;
- aprender o contexto do ambiente;
- futuramente administrar servidores Ubuntu remotos.

---

# Tecnologias

- Python 3.12
- Typer
- Rich
- Ollama
- Ruff
- Pytest
- uv
- Git
- GitHub

---

# Estrutura do projeto

src/ubuntu_ai/

- cli/
- core/
- domain/
- planner/
- executor/
- explainer/
- services/
- tools/
- memory/

---

# Arquitetura

CLI

↓

Core Engine

↓

Intent Analyzer

↓

Planner

↓

Risk Evaluator

↓

Explainer

↓

Executor

↓

Tool Registry

↓

Ubuntu

---

# Princípios

## CLI

Responsável apenas pela interface.

Nunca executa comandos Linux.

---

## Planner

Converte intenção em plano.

Nunca executa comandos.

---

## Executor

Executa apenas planos aprovados.

Nunca interpreta intenções.

---

## Services

Integrações reutilizáveis.

Exemplos:

- ShellService
- SystemService
- OllamaService

---

## Tools

Capacidades específicas do sistema.

Exemplos:

- AptTool
- DockerTool
- GitTool
- FilesystemTool

---

# Convenções

Sempre executar:

uv run ruff check src tests

Depois:

uv run pytest

Depois:

git add .

git commit

---

# Estado atual

Implementado:

- CLI
- Doctor
- SystemService
- OllamaService
- ShellService
- Planner inicial
- Explainer inicial
- Core Engine
- Domain Models

Todos os testes passando.

10 passed.

---

# Próxima Sprint

Integração completa do Core Engine.

Fluxo:

Usuário

↓

CLI

↓

Core Engine

↓

Planner

↓

Risk Evaluator

↓

Explainer

↓

Executor

---

# Objetivo final

Criar um assistente profissional de administração do Ubuntu semelhante ao Claude Code, porém especializado em Linux e totalmente executado localmente através do Ollama.