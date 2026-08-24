from typing import Protocol

from entities.chat import ChatSession, RetrievedChunk


class KnowledgeRetriever(Protocol):
    async def retrieve(self, query: str, limit: int = 4) -> list[RetrievedChunk]: ...


class SessionRepository(Protocol):
    async def get_or_create(self, session_id: str | None) -> ChatSession: ...
    async def save(self, session: ChatSession) -> None: ...
