from frameworks_and_drivers.security.in_memory import InMemoryRequestSecurity


class CloudflareRequestSecurity(InMemoryRequestSecurity):
    """Worker-safe fallback behind the RequestSecurity port.

    Cloudflare Rate Limiting can replace this adapter without touching FastAPI or
    the application layer when the production zone policy is configured.
    """
