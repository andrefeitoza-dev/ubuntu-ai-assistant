# ADR-007 — Memory Architecture

## Status

Accepted for v0.7.0.

## Decision

Memory is separated into four concerns:

1. **Session memory** — recent interaction state.
2. **Execution memory** — requests, commands and outcomes.
3. **Semantic memory** — retrievable contextual knowledge.
4. **Learning evidence** — observations derived from successful or failed executions.

Memory stores evidence; it does not decide actions. Planning and reflection consume memory through query services.

## Requirements

- repository contracts are backend-independent;
- sensitive values must not be persisted by default;
- records have timestamps and provenance;
- retrieval is bounded and relevance-ranked;
- deletion and retention policies are supported.
