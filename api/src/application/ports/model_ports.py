from typing import Protocol

from entities.chat import ChatAnswer, ConversationTurn, IntentDecision, MessageInput, ResponsePrompt, RetrievedChunk


class IntentResolver(Protocol):
    async def resolve(self, message: MessageInput) -> IntentDecision: ...


class LanguageModel(Protocol):
    async def answer(self, prompt: ResponsePrompt) -> ChatAnswer: ...


class ResponsePromptBuilder(Protocol):
    def build(
        self,
        message: MessageInput,
        decision: IntentDecision,
        context: list[RetrievedChunk],
        conversation: list[ConversationTurn] | None = None,
    ) -> ResponsePrompt: ...
