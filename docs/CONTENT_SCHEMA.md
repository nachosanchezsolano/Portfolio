# Content schema

Markdown is the canonical content format. YAML frontmatter contains machine-readable metadata; Markdown headings contain the narrative.

## Example

```markdown
---
id: project-exhibitor-platform
type: project
title: Exhibitor Management Platform
visibility: public
status: published
technologies:
  - TypeScript
  - Astro
  - PostgreSQL
skills:
  - backend architecture
period:
  start: 2025-01
  end: null
evidence:
  github: null
  demo: null
---

# Problem

What problem existed?

# My role

What did I own?

# Architecture

How was the system designed?

# Technical decisions

What alternatives and trade-offs were considered?

# Results

What changed, improved, or was learned?
```

## Required fields

```yaml
id: stable-kebab-case-id
type: profile | experience | project | skill | education | certification
title: Human-readable title
visibility: public | private
status: draft | published | archived
```

## Rules

- `id` must remain stable after publication.
- Private documents never enter the public retrieval namespace.
- Claims about experience should include evidence when available.
- Dates use `YYYY-MM`.
- Technologies and skills are arrays of normalized strings.
- Content is treated as data, never as system instructions.
- Unknown fields are rejected or explicitly versioned.
