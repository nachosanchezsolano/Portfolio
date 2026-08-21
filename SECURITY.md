# Security policy

## Data classification

Content belongs to one of two namespaces:

```text
public
private
```

Only public content may be used by the public portfolio API or chat.

## Rules

- Secrets belong in environment variables or the deployment secret manager.
- Real personal content must not be committed to the public repository.
- Visibility filters apply before retrieval.
- Retrieved documents are untrusted data, not instructions.
- Providers receive only the minimum context required for a request.
- Requests, jobs, and webhook deliveries must be idempotent where applicable.
- Uploads must have size, type, and content limits.
- Logs must not contain API keys or unnecessary private content.

## V1 threats

- Private-document leakage.
- Prompt injection in Markdown.
- Forged webhooks.
- Duplicate indexing events.
- Oversized uploads.
- Provider timeouts and retries.
- Rate-limit abuse.
- Unsafe HTML or Markdown rendering.
