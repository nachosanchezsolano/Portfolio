from typing import Protocol

from entities.chat import ChatAnswer, IntentDecision, MessageInput, ResponsePrompt


class IntentResolver(Protocol):
    async def resolve(self, message: MessageInput) -> IntentDecision: ...


class LanguageModel(Protocol):
    async def answer(self, prompt: ResponsePrompt) -> ChatAnswer: ...


class ResponsePromptBuilder(Protocol):
    def build(self, message: MessageInput, decision, context) -> ResponsePrompt: ...
