from typing import Protocol

from entities.chat import MessageInput


class SecurityError(ValueError):
    """A request failed an authentication or abuse-prevention policy."""


class RequestSecurity(Protocol):
    async def check(self, client_id: str, credential: str | None = None) -> None: ...


class SemanticSanitizer(Protocol):
    async def sanitize(self, message: MessageInput) -> MessageInput: ...


class SyntacticSanitizer(Protocol):
    def sanitize(self, value: str) -> str: ...
