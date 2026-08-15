# ADR-006 — Plugin SDK

## Status

Accepted for v0.7.0.

## Decision

Plugins extend the framework only through declared capabilities.

A plugin must provide:

- stable identifier and version;
- manifest metadata;
- required framework version range;
- declared skills/capabilities;
- initialization and shutdown lifecycle;
- no import-time side effects.

## Security

- plugins are untrusted by default;
- capability admission is controlled by policy;
- shell access must be declared;
- plugin failures are isolated and reported;
- plugins cannot bypass confirmation or execution policy.
