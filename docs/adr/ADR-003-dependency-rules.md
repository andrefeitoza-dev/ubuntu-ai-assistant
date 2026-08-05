# ADR-003 — Dependency Rules

## Status

Accepted for v0.7.0.

## Decision

Dependencies must point inward:

```text
interfaces -> application -> domain
infrastructure -> application/domain contracts
```

## Allowed rules

- `domain` imports only Python standard library and other domain modules.
- application services may import domain contracts and abstract repositories/providers.
- infrastructure modules implement contracts owned by inner layers.
- CLI and TUI may call SDK/runtime/application façades.
- the dependency-injection container may compose all layers.

## Forbidden rules

- domain importing CLI, TUI, SQLite, requests or shell implementations;
- planner importing concrete persistence backends;
- repository contracts importing repository implementations;
- plugins mutating global registries outside their declared lifecycle;
- circular imports hidden through package `__init__.py` files.

## Enforcement

`scripts/check_architecture.py` performs a lightweight import-boundary check. It supplements, but does not replace, unit and integration tests.
