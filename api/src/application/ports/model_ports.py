from typing import Protocol

from entities.chat import ChatAnswer, IntentDecision, MessageInput, RetrievedChunk


class IntentResolver(Protocol):
    async def resolve(self, message: MessageInput) -> IntentDecision: ...


class LanguageModel(Protocol):
    async def answer(
        self,
        message: MessageInput,
        decision: IntentDecision,
        context: list[RetrievedChunk],
    ) -> ChatAnswer: ...
