# ADR-008 — Execution Architecture

## Status

Accepted for v0.7.0.

## Decision

Execution follows a guarded pipeline:

```text
PlanStep
 -> skill preparation
 -> capability resolution
 -> preflight
 -> policy evaluation
 -> confirmation
 -> controlled execution
 -> verification
 -> persistence
 -> reflection
```

## Invariants

- generated text never executes directly;
- commands are represented structurally before shell rendering;
- policy is evaluated before execution;
- blocked commands produce explicit results;
- stdout, stderr, return code and duration are captured;
- verification is distinct from command completion;
- reflection cannot bypass policy.
