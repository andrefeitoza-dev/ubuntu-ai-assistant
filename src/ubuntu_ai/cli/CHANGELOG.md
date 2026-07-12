# Changelog

Todas as alterações importantes do Ubuntu AI Assistant serão documentadas aqui.

## [0.1.0] - Em desenvolvimento

### Adicionado

- Estrutura inicial do projeto
- Ambiente Python com uv
- CLI usando Typer

- Integração do Core Engine
- Testes do Core Engine
- Fluxo de planejamento e explicação validado

- Executor básico para processamento sequencial de planos
- Testes do Executor

# Changelog

## Sprint 9.4

### Adicionado

- Executor
- Tool Registry
- Shell Tool
- Integração entre Executor e Tool Registry
- 22 testes automatizados

### Qualidade

- Ruff validando todo o projeto
- Pytest: 22 testes passando

## Sprint 10.3

### Adicionado

- Execution Preview
- Preview Renderer

### Qualidade

- 27 testes automatizados
- Ruff validando todo o projeto

## Sprint 10.4

### Adicionado

- Execution Pipeline
- PipelineResult
- orquestração do fluxo de planejamento e preview
- validação de solicitações vazias

### Qualidade

- 30 testes automatizados
- Ruff sem erros