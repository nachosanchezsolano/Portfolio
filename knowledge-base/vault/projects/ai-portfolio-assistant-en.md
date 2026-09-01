---
id: project-ai-portfolio-assistant-en
type: project
title: AI Portfolio Assistant
visibility: public
status: published
technologies:
  - Astro
  - Python
  - FastAPI
  - Cloudflare Workers AI
  - Vectorize
  - Markdown
  - TypeScript
skills:
  - Full Stack Development
  - AI Engineering
  - RAG
  - API Design
  - Security
  - Observability
evidence:
  github: https://github.com/nachosanchezsolano/Portfolio
  demo: https://nachosanchez.com.ar
---

# Summary

An evidence-grounded conversational portfolio that lets visitors explore professional work through normal portfolio pages or natural-language questions.

# Problem

Professional information is usually scattered across a CV, project descriptions, notes and profiles. A static portfolio can show selected work, but it does not explain the decisions and context behind it very well.

# Context

This project is both a professional portfolio and a public demonstration of full-stack AI product engineering. The same Markdown knowledge source powers the portfolio content and the assistant's retrieval context.

# My role

I designed and implemented the product direction, Astro frontend, FastAPI application flow, knowledge model, Cloudflare adapters, security controls, observability events and deployment documentation.

# Architecture

The deployed flow is:

Browser → Astro static assets → FastAPI Worker → intent detection → Vectorize retrieval → grounded response → cited answer.

The canonical source is bilingual Markdown with YAML frontmatter. Public documents are chunked deterministically before embeddings and metadata are uploaded to the `portfolio-knowledge` Vectorize index.

# Engineering decisions

## Markdown as the source of truth

Markdown keeps professional content portable, reviewable and independent of the editor. The same content can later feed pages, search and chat without duplicating claims across systems.

## Retrieval instead of unsupported generation

The assistant retrieves public evidence before generating an answer. When the retrieved context is insufficient, it returns a safe no-evidence response instead of presenting an unverified claim as fact.

## Provider boundaries

AI and infrastructure providers are behind application ports and adapters. This keeps the use cases testable and avoids coupling the domain to a single vendor implementation.

## Cloudflare for the public product

The current deployment uses Cloudflare Workers, Workers AI and Vectorize to keep the public portfolio close to its visitors and to avoid exposing API credentials in the browser.

# AI pipeline

Documents → public visibility filter → semantic section chunking → embeddings → Vectorize → retrieved context → response prompt → grounded answer with sources.

The current Vectorize contract uses 768 dimensions, cosine similarity and metadata for source, content, section and chunk index.

# Security and reliability

- CORS allows only the configured portfolio domains.
- Requests pass validation and syntactic and semantic sanitization.
- Rate limiting and session state are protected at the API layer.
- The browser never receives the API key.
- Logs exclude prompts, full responses, secrets, IP addresses and automatic PII.
- Prompt injection, private-content exposure and no-evidence behavior are covered by security and domain tests.

# Observability

The API emits structured events including request start, sanitization, intent detection, retrieval completion, response generation and flow completion. Retrieval debugging includes the `context_count` field so a no-evidence answer can be distinguished from a generation failure.

# Evaluation status

The repository includes offline API tests and a knowledge-base evaluation foundation. A larger golden set for retrieval precision, answer faithfulness, latency and cost is the next quality milestone. No production accuracy percentage is claimed until that dataset is complete.

# What I would improve

- Add a visible project-context handoff from each case study to the assistant.
- Complete the bilingual route structure and reciprocal metadata.
- Add retrieval and groundedness regression gates to CI.
- Add distributed session and rate-limit storage if public traffic requires it.

# What I learned

An AI feature becomes more trustworthy when it is treated as a normal product surface: clear source boundaries, explicit failure states, observable behavior and a useful non-AI fallback.
