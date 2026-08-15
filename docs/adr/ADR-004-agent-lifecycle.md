# ADR-004 — Agent Lifecycle

## Status

Accepted for v0.7.0.

## Lifecycle

```text
IDLE
  -> UNDERSTANDING
  -> PLANNING
  -> REVIEWING
  -> WAITING_CONFIRMATION
  -> EXECUTING
  -> VERIFYING
  -> REFLECTING
  -> COMPLETED | FAILED | CANCELLED
```

## Rules

- Every transition is explicit and observable.
- Confirmation is mandatory when policy or risk requires it.
- Execution results are immutable records.
- Reflection may recommend replanning but cannot execute commands directly.
- Cancellation clears pending execution state safely.
- A failed step does not silently become success.

## Compatibility

Existing lifecycle values remain valid. New values are added only when the implementation that uses them is introduced and covered by tests.
