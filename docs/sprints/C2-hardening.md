# Sprint C2 — Hardening

## Objetivo

Tornar a fachada consolidada da versão 1.0 observável e resiliente sem
introduzir retries automáticos em operações potencialmente destrutivas.

## Entregas

- RuntimeTelemetry thread-safe.
- ApplicationHealthService com probes não destrutivos.
- RetryPolicy conservadora para operações idempotentes.
- LoggingService integrado à ApplicationRuntime.
- Métricas de `start`, `confirm`, `cancel` e `snapshot`.
- Comando `ubuntu-ai health`.
- Composição pelo Container.

## Segurança

A C2 não conecta retry automático ao AgentRuntime. Uma repetição de operação
com efeito colateral pode ser perigosa em administração de sistemas.

## Critérios de aceite

- Ruff sem erros.
- Suíte completa verde.
- `ubuntu-ai health` retorna prontidão.
- Falhas são contabilizadas e relançadas.
