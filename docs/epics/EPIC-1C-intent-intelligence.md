# Epic 1C — Intent Intelligence

## Status

Implementado.

## Objetivo

Fazer Knowledge, Learning e Reflection consumirem a intenção estruturada,
mantendo compatibilidade com chamadas baseadas apenas em texto.

## Entregas

- `IntentContextBuilder` para consultas e contexto de prompt.
- Busca de conhecimento orientada por intenção.
- Recomendações de aprendizado orientadas por intenção.
- Reflexão pré e pós-execução com contexto da intenção.
- Prompt do `AIPlanner` enriquecido com categoria, objetivo, confiança e entidades.
- Métricas `knowledge`, `learning` e `reflection` no benchmark.
- Testes de integração entre os módulos.

## Compatibilidade

As APIs existentes com `str` continuam aceitas durante a migração Intent First.
Doubles antigos de `ReflectionEngine` continuam suportados pelo runtime.

## Validação

```bash
uv run ruff check src tests
uv run pytest
```
