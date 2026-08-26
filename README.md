# AI Portfolio Engine

An open-source, knowledge-driven AI portfolio engine.

Write professional knowledge once in Markdown and use it to power portfolio pages, hybrid search, and an evidence-grounded AI assistant with verifiable citations.

## Why this project exists

Professional information is usually scattered across a CV, project descriptions, notes, profiles, and conversations. This project turns that information into a structured knowledge base that can be reused by:

- A traditional portfolio.
- Project and experience pages.
- Keyword and semantic search.
- An AI assistant grounded in published evidence.
- Future integrations with other knowledge sources.

Obsidian is supported as an editing workflow, but it is not part of the domain. The engine works with Markdown files and can later accept Git repositories, Notion, PDFs, or other sources.

## Core principles

- Evidence over claims: professional answers must be traceable to sources.
- Evaluation over intuition: retrieval and generation decisions must be measured.
- Hybrid retrieval over vector-only search: exact names and semantic concepts both matter.
- Incremental indexing over full rebuilds: unchanged content should not be reprocessed.
- One pipeline over premature agents: keep V1 observable and testable.
- PostgreSQL over unnecessary infrastructure: add services only when a real need appears.
- Provider interfaces over vendor lock-in: external providers must be replaceable.
- Markdown over Obsidian dependency: the source format matters more than the editor.
- Single source of truth: pages, search, and chat use the same knowledge.
- Reproducibility over personal customization: the public repository runs with example content.

## V1 scope

V1 will provide:

1. A Markdown knowledge source with YAML frontmatter.
2. A FastAPI application following Clean Architecture.
3. A separate Python worker for indexing jobs.
4. PostgreSQL with pgvector and PostgreSQL Full Text Search.
5. Incremental indexing based on stable content hashes.
6. Hybrid retrieval using Reciprocal Rank Fusion.
7. OpenRouter behind provider interfaces for embeddings and generation.
8. Answers with citations and a safe no-evidence response.
9. An Astro portfolio consuming the same knowledge source.
10. Docker Compose for local development and Railway deployment documentation.

The first version will not include autonomous multi-agent workflows, Redis, LangGraph, or an administration dashboard. Those are extension points, not starting requirements.

## Repository model

This repository is the public engine:

```text
ai-portfolio-engine/
├── apps/
│   ├── web/       # Astro portfolio
│   ├── api/       # FastAPI HTTP API
│   └── worker/    # Asynchronous indexing worker
├── packages/
│   ├── knowledge-example/
│   └── schemas/
├── docs/
├── infra/
├── tests/
└── docker-compose.yml
```

The workspace contains the Astro/FastAPI implementation under `apps/web/`, `api/`, and `knowledge-base/`.

Personal content will live in a separate private repository:

```text
portfolio-content/
├── profile.md
├── experience/
├── projects/
├── skills/
└── education/
```

Never commit private content, credentials, personal identifiers, or real environment files to this repository.

## Local setup

The target developer experience is:

```bash
git clone <repository-url>
cd ai-portfolio-engine
cp .env.example .env
docker compose up --build
```

During the migration, the existing prototype is still started from `portfolio-platform` with:

```bash
docker compose -f docker-compose.dev.yml up
```

The target Compose setup will be updated when PostgreSQL, pgvector, and the worker are introduced.

## Documentation

- [Current project context — read this first in a new chat](docs/PROJECT_CONTEXT.md)
- [Product definition](docs/PRODUCT.md)
- [Architecture](ARCHITECTURE.md)
- [Content schema](docs/CONTENT_SCHEMA.md)
- [Development workflow](docs/DEVELOPMENT.md)
- [Cloudflare and GitHub deployment](docs/DEPLOYMENT_CLOUDFLARE_GITHUB.md)
- [Roadmap](docs/ROADMAP.md)
- [Security](SECURITY.md)
- [Evaluation](docs/evaluation/README.md)
- [Architecture decisions](docs/adr/)
- [Contributing](CONTRIBUTING.md)

## License

The license will be selected before the first public release. Until then, treat the repository as source-available development material.
