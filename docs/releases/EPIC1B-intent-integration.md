# Epic 1B — Intent Integration

## Objetivo

Integrar o domínio de intenção ao fluxo principal sem remover a compatibilidade
com solicitações textuais existentes.

## Entregas

- `Planner.create_plan()` aceita `str` ou `Intent`.
- `ExecutionPipeline` interpreta texto por meio de `IntentEngine`.
- `PipelineResult` transporta a intenção interpretada.
- `Container` compõe repositório, serviço e engine de intenção como singletons.
- `AgentRuntime.last_intent` expõe a intenção da tarefa mais recente.
- Persistência inicial em memória do histórico de intenções.
- Testes de integração entre Intent, Planner, Pipeline, Container e Runtime.

## Compatibilidade

Chamadas existentes com `str` continuam válidas. O `Intent` é um contrato
aditivo nesta fase da migração.

## Validação

```bash
uv run ruff check src tests
uv run pytest tests/intent tests/planner/test_intent_integration.py \
  tests/pipeline/test_intent_integration.py \
  tests/container/test_intent_integration.py \
  tests/agent/test_runtime_intent.py
uv run pytest
```
