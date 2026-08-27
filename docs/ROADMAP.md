# Roadmap

## Phase 0 — Foundation

- [x] Define product direction.
- [x] Define public engine and private content repositories.
- [x] Define V1 boundaries and principles.
- [x] Define Markdown content contract.
- [x] Create initial architecture documentation.
- [ ] Add the target repository skeleton.

## Phase 1 — Local platform

- [ ] Create `apps/api`, `apps/worker`, and `apps/web` boundaries.
- [ ] Add PostgreSQL and pgvector to Docker Compose.
- [ ] Add environment validation and health checks.
- [ ] Add SQLAlchemy and Alembic.

## Phase 2 — Knowledge pipeline

- [ ] Implement Markdown source adapter.
- [ ] Validate YAML frontmatter.
- [x] Implement semantic section chunking for the Cloudflare Vectorize ingestion.
- [ ] Add content hashes and change detection.
- [ ] Add PostgreSQL-backed indexing jobs.
- [ ] Add the worker.

## Phase 3 — Retrieval and chat

- [ ] Add embedding provider port.
- [ ] Add OpenRouter embedding adapter.
- [ ] Add pgvector retrieval and PostgreSQL FTS.
- [ ] Add Reciprocal Rank Fusion.
- [ ] Add OpenRouter language model adapter.
- [ ] Add structured answers and citations.

## Phase 4 — Portfolio

- [ ] Build profile, project, experience, and skills APIs.
- [x] Establish the Astro frontend in `apps/web`.
- [ ] Connect pages and chat to the same knowledge source.

## Phase 5 — Automation and quality

- [ ] Add GitHub webhook ingestion.
- [ ] Add idempotency and delivery tracking.
- [ ] Create the golden evaluation dataset.
- [ ] Add retrieval and groundedness metrics.
- [ ] Add structured logs, usage tracking, and Sentry.
- [ ] Add security tests.

## Phase 6 — Release

- [ ] Add Railway deployment configuration.
- [ ] Add contributor guide and license.
- [ ] Add public example vault.
- [ ] Publish the first Open Source release.

## Later extensions

- Additional knowledge sources.
- Reranking.
- Redis or a dedicated queue.
- LangGraph workflows.
- Agents.
- Multi-tenant support.
- Administration UI.
