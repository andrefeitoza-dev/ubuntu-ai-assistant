# ADR-002 — Ubuntu AI Framework Architecture

## Status

Accepted for v0.7.0.

## Context

Ubuntu AI evolved from a terminal assistant into a reusable local-agent runtime for Linux. The codebase now includes planning, execution, context, memory, learning, reflection, knowledge, skills, plugins, logging, configuration, benchmark, CLI and TUI components.

Without explicit boundaries, new intelligent-runtime features could create circular dependencies and make public APIs unstable.

## Decision

Ubuntu AI is defined as a framework with four architectural layers:

1. **Domain** — immutable concepts and contracts that do not depend on infrastructure.
2. **Application** — orchestration of intents, planning, reflection and execution.
3. **Infrastructure** — Ollama, SQLite, shell, filesystem and operating-system adapters.
4. **Interfaces** — SDK, CLI and TUI.

The runtime is the primary application façade. CLI and TUI are clients of the runtime, not owners of business rules.

## Target module map

```text
ubuntu_ai.domain
ubuntu_ai.intent
ubuntu_ai.context
ubuntu_ai.planner
ubuntu_ai.execution
ubuntu_ai.memory
ubuntu_ai.learning
ubuntu_ai.reflection
ubuntu_ai.knowledge
ubuntu_ai.skills
ubuntu_ai.plugins
ubuntu_ai.runtime
ubuntu_ai.sdk
ubuntu_ai.cli
ubuntu_ai.tui
```

Existing namespaces remain compatible during v0.7.0. Migration is incremental and must preserve tests and public imports.

## Consequences

- New functionality must enter through explicit contracts.
- Infrastructure implementations remain replaceable.
- CLI/TUI cannot directly embed orchestration rules.
- Refactoring is evolutionary; no big-bang namespace migration.
