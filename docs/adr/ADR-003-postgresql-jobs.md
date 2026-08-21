# ADR-003: PostgreSQL-backed jobs before Redis

- Status: Accepted
- Date: 2026-08-21

## Decision

Indexing jobs will initially be persisted in PostgreSQL and claimed transactionally by the worker.

## Consequences

The system avoids an additional service in V1. A dedicated queue can be introduced later behind the `JobQueue` port if throughput requires it.
