# Architecture

## System boundary

The project transforms structured professional knowledge into three consumers:

```text
Markdown knowledge
        │
        ├── Portfolio pages
        ├── Hybrid search
        └── Evidence-grounded chat
```

The domain depends on a knowledge-source contract, not on Obsidian. Obsidian is one possible editor for Markdown content.

## Target system

```text
Astro web
      │
      ▼
FastAPI API ─────── PostgreSQL + pgvector + FTS
      │                         ▲
      ▼                         │
PostgreSQL indexing jobs ── Python worker
      │
      ├── Embedding provider
      └── Language model provider
```

The API must never perform a long indexing operation inside an HTTP request. It creates a job and the worker processes it asynchronously.

## Clean Architecture boundaries

### Entities

Business rules and domain objects:

```text
KnowledgeSource
Document
DocumentVersion
Chunk
IndexingJob
Conversation
Message
Citation
ModelUsage
EvaluationCase
```

Entities must not import FastAPI, SQLAlchemy, LangChain, OpenRouter, or framework-specific code.

### Application

Use cases orchestrate business actions:

```text
IngestKnowledge
DetectChanges
CreateIndexingJob
ProcessIndexingJob
RetrieveContext
AnswerPortfolioQuestion
SearchPortfolio
```

### Ports

Ports define replaceable external capabilities:

```text
KnowledgeSource
DocumentRepository
VectorStore
EmbeddingProvider
LanguageModel
JobQueue
```

### Interface adapters

Adapters translate external representations into use-case requests:

```text
FastAPI controllers
Pydantic schemas
GitHub webhook handler
Markdown DTO mappers
HTTP presenters
```

### Frameworks and drivers

Concrete implementations belong here:

```text
FastAPI
SQLAlchemy / PostgreSQL
pgvector
OpenRouter HTTP client
Markdown parser
Docker
Railway
```

## Indexing pipeline

```text
Load source
  → Validate frontmatter
  → Normalize Markdown
  → Split by semantic sections
  → Calculate stable hashes
  → Compare current index
  → Embed added/changed chunks
  → Deactivate deleted chunks
  → Commit a new index version
```

Every chunk must preserve provenance: source path, document ID, heading, visibility, content hash, embedding model, and index version.

## Retrieval pipeline

```text
Question
  → Validate request
  → Apply visibility filter
  → PostgreSQL Full Text Search
  → pgvector similarity search
  → Reciprocal Rank Fusion
  → Build cited context
  → Generate structured answer
  → Validate citations
```

Visibility filtering happens before retrieval, never after it.

## Interaction modes

V1 uses explicit modes instead of autonomous agents:

```text
GENERAL
RECRUITER
TECHNICAL
```

All modes use the same retrieval pipeline but may change the response style, top-k, and emphasis. An agent runtime may be added later behind a port if real workflows justify it.

## Current migration note

The current implementation uses Astro, a small FastAPI application, an in-memory retriever, and a local assistant. Migration will proceed in this order:

1. Preserve the running prototype.
2. Extract domain and application contracts.
3. Add persistence and migrations.
4. Add the worker and incremental indexing.
5. Replace memory retrieval with hybrid PostgreSQL retrieval.
6. Keep the web layer in Astro and connect it to the stabilized API contract.
