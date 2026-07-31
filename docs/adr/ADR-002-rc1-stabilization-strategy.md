# ADR-002 — Estratégia de estabilização da RC1

## Status

Aceito.

## Contexto

O Ubuntu AI possui muitos subsistemas integrados e um fluxo operacional validado. Uma reorganização ampla antes da primeira release candidate aumentaria o risco sem benefício imediato para o usuário.

## Decisão

A RC1 será estabilizada de forma incremental:

- preservar APIs e imports públicos;
- corrigir problemas nas fronteiras onde surgem;
- atualizar documentação e versão;
- adicionar cenários de aceitação;
- adiar renomeações e movimentações em massa;
- extrair responsabilidades grandes apenas em mudanças pequenas e testadas.

## Consequências

### Positivas

- menor risco de regressão;
- release mais rápida;
- histórico Git mais claro;
- compatibilidade preservada.

### Negativas

- `Container` e `AgentRuntime` permanecem grandes durante a RC1;
- coexistência temporária de `execution/` e `executor/`;
- parte da dívida de nomenclatura segue documentada para a Fase 7.
