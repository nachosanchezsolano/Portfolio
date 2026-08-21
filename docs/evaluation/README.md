# Evaluation

Evaluation is a product feature, not final polish.

## Golden dataset

```yaml
id: project-postgresql-experience
question: Does the candidate have PostgreSQL experience?
expected_sources:
  - project-exhibitor-platform
expected_facts:
  - PostgreSQL
forbidden_claims:
  - ten years of experience
```

Initial categories:

```text
profile, projects, experience, skills, architecture,
unsupported questions, negative questions
```

Initial metrics:

- Recall@K for retrieval.
- Citation correctness.
- Groundedness.
- Answer completeness.
- No-answer rate.
- Latency.
- Estimated cost.
