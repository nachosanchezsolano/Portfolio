# API answer flow

The chat endpoint follows one explicit orchestration path:

```text
ChatInput
  → SyntacticInputSanitizer
  → RequestSecurityController
  → SemanticSanitizer
  → IntentResolver
  → IntentDecision(intent + retrieval query)
  → KnowledgeRetriever (RAG)
  → BuildResponsePrompt (instructions + retrieved evidence)
  → LanguageModel (grounded context)
  → ChatOutput(message + sources + intent)
```

The application layer owns the orchestration in `ChatFlowController`. The application
depends only on ports, never on FastAPI, Cloudflare or a model vendor.

Ports are grouped in `api/src/application/ports/`:

- `model_ports.py`: intent resolver and language model.
- `retrieval_ports.py`: RAG retriever and session repository.
- `security_ports.py`: request security and input sanitizers.

Providers are selected only in the composition root:

- `providers/local/`: local deterministic models, memory retrieval and in-memory security.
- `providers/cloudflare/`: Workers AI, Vectorize and Cloudflare security adapters.

Replacing Cloudflare with another model or security provider does not change the
domain entities, use cases or HTTP contract.
