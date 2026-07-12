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

## Sprint 8 — Concluída

Implementado e validado:

- CoreEngine
- detecção de intenção
- integração com Planner
- integração com Explainer
- testes do CoreEngine
- 12 testes passando
- Ruff sem erros

## Próxima Sprint

Sprint 9 — Executor

## Sprint 9.1 — Concluída

Implementado:

- Executor básico
- Execução sequencial das etapas do plano
- Teste inicial do Executor
- 13 testes passando
- Ruff sem erros

## Próxima etapa

Sprint 9.2 — Tool Registry
---

# Engineering Checkpoint

## Sprint 9.4 — Concluída

### Estado do projeto

- Ruff: All checks passed
- Pytest: 22 passed

### Funcionalidades implementadas

- CLI
- Doctor
- Core Engine
- Intent Analyzer
- Planner
- Explainer
- ShellService
- Tool Registry
- ShellTool
- Executor integrado ao Tool Registry

### Arquitetura

Usuário

↓

CLI

↓

Core Engine

↓

Planner

↓

Executor

↓

Tool Registry

↓

Shell Tool

↓

Shell Service

↓

Ubuntu

### Próxima Sprint

Sprint 10

Dry Run

Execution Preview

Execution Report

---

# Engineering Checkpoint 2

## Milestone

Execution

## Estado atual

### Qualidade

- Ruff: All checks passed
- Pytest: 27 passed

### Componentes implementados

- Core Engine
- Planner
- Explainer
- Executor
- Tool Registry
- Shell Tool
- Preview Builder
- Preview Renderer

### Próxima Sprint

Sprint 10.4

Execution Pipeline