from collections import defaultdict
from time import monotonic

from application.ports.security_ports import RequestSecurity, SecurityError
from entities.chat import DomainValidationError
import re


class InMemoryRequestSecurity(RequestSecurity):
    """Local policy adapter; replace with a distributed edge limiter in production."""

    def __init__(self, api_key: str, max_requests: int, window_seconds: int) -> None:
        self._api_key = api_key
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def check(self, client_id: str, credential: str | None = None) -> None:
        if self._api_key and credential != self._api_key:
            raise SecurityError("invalid api key")

        now = monotonic()
        recent = [stamp for stamp in self._requests[client_id] if now - stamp < self._window_seconds]
        if len(recent) >= self._max_requests:
            raise SecurityError("rate limit exceeded")
        recent.append(now)
        self._requests[client_id] = recent


class InMemorySyntacticSanitizer:
    """Framework-independent request syntax boundary."""

    _unsafe_patterns = (
        r"```",
        r"<\s*script",
        r"\b(?:select|insert|update|delete|drop|alter|create)\b[\s\S]{0,80}"
        r"\b(?:from|table|database|where|into)\b",
        r"\b(?:union\s+select|exec(?:ute)?|xp_cmdshell)\b",
        r"(?:--|/\*|\*/)",
    )

    def sanitize(self, value: str) -> str:
        if any(re.search(pattern, value, re.IGNORECASE) for pattern in self._unsafe_patterns):
            raise DomainValidationError("message contains unsafe syntax")
        return " ".join(value.split())
