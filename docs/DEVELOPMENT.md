# Development workflow

## Development order

Work vertically and keep every step runnable:

1. Domain model and validation.
2. Database schema and migrations.
3. Markdown source and chunking.
4. Incremental indexing.
5. Hybrid retrieval.
6. Grounded chat and citations.
7. Portfolio consumers.
8. Webhooks and deployment.

## Local commands

Target workflow:

```bash
cp .env.example .env
docker compose up --build
```

The current prototype can still be run using its existing commands until migration is complete.

## Rules for each change

- Start with a small use case and acceptance criterion.
- Keep domain code independent of frameworks.
- Add or update tests with behavior changes.
- Add an ADR when a decision affects the system boundary or provider choice.
- Do not add infrastructure without a demonstrated need.
- Use fictional fixtures; never use personal content in tests.
- Keep migrations forward-only and reviewable.

## Test layers

```text
unit        domain rules, parsers, chunking, ranking
integration repositories, PostgreSQL, pgvector, jobs
contract    API schemas and provider ports
evaluation  retrieval and grounded answer quality
end-to-end  complete example workflow
```
