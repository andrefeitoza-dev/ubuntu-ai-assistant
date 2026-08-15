# Ubuntu AI Framework — Architecture v0.7

## Purpose

Ubuntu AI is an open-source Python framework for building local intelligent agents that operate Linux safely through planning, policy, confirmation and controlled execution.

## Request flow

```text
User / SDK client
       |
       v
Intent understanding
       |
       v
Context enrichment <---- Knowledge / Memory / Learning
       |
       v
Planning
       |
       v
Reflection and risk review
       |
       v
Confirmation policy
       |
       v
Execution intelligence
       |
       v
Skills / Plugins / Linux adapters
       |
       v
Verification, persistence and feedback
```

## Architectural principles

- safety before autonomy;
- intent-first evolution;
- explicit state transitions;
- dependency inversion;
- replaceable infrastructure;
- observable operations;
- compatibility through incremental migration;
- tests as release gates.

## v0.7 delivery sequence

1. Epic 0 — architecture freeze.
2. Epic 1 — intent intelligence.
3. Epic 2 — context intelligence.
4. Epic 3 — memory evolution.
5. Epic 4 — reflection and replanning.
6. Epic 5 — adaptive runtime.
7. Epic 6 — multiple AI providers.
