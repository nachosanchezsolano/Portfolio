from typing import Protocol
from entities.chat import ChatAnswer, ChatQuestion


class PortfolioAssistant(Protocol):
    async def answer(self, question: ChatQuestion) -> ChatAnswer: ...


class KnowledgeRetriever(Protocol):
    async def retrieve(self, query: str, limit: int = 4) -> list[tuple[str, str]]: ...
