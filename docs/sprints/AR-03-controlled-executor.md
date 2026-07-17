# AR-03 — Controlled Executor

## Status

Em desenvolvimento.

---

# Objetivo

Implementar o primeiro executor controlado do UbuntuAI, responsável por executar ações somente após validação, confirmação do usuário e aplicação das políticas de segurança.

Esta Sprint marca a transição do projeto de um sistema que apenas planeja ações para um agente capaz de executá-las de forma segura.

---

# Motivação

Até a AR-2, o UbuntuAI era capaz de:

- interpretar solicitações;
- gerar planos;
- construir previews;
- manter contexto;
- organizar sessões;
- orquestrar o fluxo através do AgentRuntime.

Entretanto, ainda não existia um mecanismo responsável por controlar a execução real das ações.

A AR-3 introduz esse componente.

---

# Escopo

A Sprint será dividida em seis pacotes.

## Pacote 1

Execution Contracts

Definição dos contratos que representam uma execução autorizada.

---

## Pacote 2

Security Policy

Implementação das políticas de segurança.

Responsabilidades:

- validar comandos;
- bloquear comandos proibidos;
- validar argumentos;
- impedir ações destrutivas.

---

## Pacote 3

Controlled Executor

Executor responsável por:

- receber ações aprovadas;
- aplicar políticas;
- executar ferramentas autorizadas;
- registrar resultados.

---

## Pacote 4

Integração

Integração completa com:

- AgentRuntime
- ExecutionPipeline
- ToolRegistry

---

## Pacote 5

Testes automatizados.

Cobertura de:

- execução autorizada;
- execução bloqueada;
- políticas;
- integração.

---

## Pacote 6

Atualização da documentação.

---

# Arquitetura

```text
Usuário
    │
    ▼
AgentRuntime
    │
    ▼
ExecutionPipeline
    │
    ▼
Execution Preview
    │
    ▼
Confirmação
    │
    ▼
Controlled Executor
    │
    ▼
Tool Registry
    │
    ▼
Ubuntu
```

---

# Requisitos Funcionais

RF-01

Executar apenas comandos previamente aprovados.

RF-02

Aplicar políticas de segurança antes da execução.

RF-03

Registrar o resultado de cada ação.

RF-04

Interromper imediatamente em caso de violação de política.

---

# Requisitos Não Funcionais

- Alta coesão.
- Baixo acoplamento.
- Compatível com Clean Architecture.
- Compatível com Dependency Injection.
- Compatível com testes unitários.

---

# Critérios de Aceite

- Todos os testes aprovados.
- Ruff sem erros.
- Integração com AgentRuntime concluída.
- Fluxo completo funcional.
- Documentação atualizada.

---

# Resultado Esperado

Ao término da AR-3, o UbuntuAI deverá ser capaz de executar comandos de forma controlada, segura e auditável, preservando a arquitetura definida para o projeto.