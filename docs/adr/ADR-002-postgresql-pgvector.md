# ADR-002: PostgreSQL and pgvector as the initial store

- Status: Accepted
- Date: 2026-08-21

## Decision

PostgreSQL will store application data, full-text indexes, vector embeddings, jobs, and evaluation records. pgvector will provide the initial vector search capability.

## Consequences

The first deployment has fewer moving parts. A dedicated vector database can be added later only if measurements show that PostgreSQL is insufficient.
