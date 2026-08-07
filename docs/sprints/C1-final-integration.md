# Sprint C1 — Consolidação do Fluxo

## Objetivo

Definir uma porta de entrada canônica para a versão 1.0 sem reescrever os
componentes que já estão estabilizados e cobertos por testes.

## Decisão arquitetural

O `AgentRuntime` + `AgentLoopController` permanece como fluxo principal de
interação local porque já integra:

1. contexto e discovery;
2. conversation;
3. intent;
4. planner, knowledge, learning e RAG;
5. preview e confirmação;
6. execution intelligence;
7. execução controlada;
8. reflection;
9. memory e learning pós-execução.

A Sprint C1 introduz `ApplicationRuntime` como fachada canônica. Ela expõe o
fluxo principal e, na mesma composição, disponibiliza as capacidades
especializadas já construídas:

- `MultiAgentRuntime`;
- `AutonomousRuntime`;
- `RemoteExecutionEngine`.

Isso elimina a necessidade de escolher entre runtimes concorrentes na camada
de interface e preserva compatibilidade com o código legado.

## Fluxo canônico 1.0

```text
CLI / SDK / TUI
      |
ApplicationRuntime
      |
AgentLoopController
      |
AgentRuntime
      |
Context -> Intent -> Memory/Knowledge/Learning -> Planner
      |
Preview -> Confirmation -> Execution Intelligence
      |
Controlled Execution -> Reflection -> Memory/Learning
```

## Nova interface CLI

```bash
ubuntu-ai run "instale nginx"
ubuntu-ai run --dry-run "instale nginx"
ubuntu-ai run --yes "mostre o status do sistema"
```

`--yes` não remove os guardrails internos. Ele apenas confirma os pontos de
confirmação produzidos pelo AgentLoop; políticas, preflight, reflection e
limites de iteração continuam ativos.

## Compatibilidade

Nenhum dos runtimes existentes foi removido nesta sprint. A consolidação define
qual deles é a fachada pública da aplicação e mantém os demais como capacidades
especializadas para evitar regressões durante a preparação da versão 1.0.
