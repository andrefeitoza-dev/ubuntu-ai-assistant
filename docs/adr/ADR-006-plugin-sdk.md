# ADR-006 — Plugin SDK

## Status

Accepted and hardened for v1.6.0.

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
- plugins are blocked by default until their complete local content is approved;
- any change to an approved plugin revokes trust automatically;
- catalog discovery inspects manifests without importing plugin code.
