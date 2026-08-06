# Epic 1 — Intent Intelligence

## Status

Concluído.

## Entregas

- Epic 1A: domínio de intenção.
- Epic 1B: integração com Planner, Pipeline, Runtime e Container.
- Epic 1C: contexto orientado por intenção para Knowledge, Learning e Reflection.
- Epic 1D: apresentação na CLI e TUI, benchmark e documentação final.

## Fluxo

```text
Texto -> Intent Engine -> Intent Context -> Planner -> Pipeline -> Runtime
```

## CLI

```bash
ubuntu-ai intent "Instale Docker"
ubuntu-ai plan "Instale Docker"
ubuntu-ai benchmark --request "Instale Docker"
```

## Critérios de aceite

- Intenção transportada pelo `PipelineResult`.
- Planner compatível com `str` e `Intent` durante a migração.
- CLI e TUI exibem categoria, objetivo, confiança e entidades.
- Benchmark mede a etapa `intent`.
- Suíte completa e Ruff verdes.
