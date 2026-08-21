# ADR-004: No autonomous agents in V1

- Status: Accepted
- Date: 2026-08-21

## Decision

V1 will use one retrieval and generation pipeline with explicit interaction modes: `GENERAL`, `RECRUITER`, and `TECHNICAL`.

## Consequences

The behavior remains easier to test, evaluate, secure, and explain. An agent runtime can be added later behind an application port when a real multi-step workflow exists.
