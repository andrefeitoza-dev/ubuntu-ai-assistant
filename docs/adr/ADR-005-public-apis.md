# ADR-005 — Public APIs

## Status

Accepted for v0.7.0.

## Decision

The supported public entry points are:

- `ubuntu_ai.UbuntuAI`
- the SDK façade;
- provider, repository, skill and plugin contracts explicitly exported through package `__all__`;
- stable domain request/result models.

Internal composition classes are not public merely because they are importable.

## Versioning

- backward-compatible additions: minor release;
- deprecations: documented for at least one minor release;
- breaking removals: major release;
- experimental APIs: explicitly marked and excluded from stability guarantees.

## Rule

Public APIs require documentation, typing and contract tests.
