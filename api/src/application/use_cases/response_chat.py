from application.ports.model_ports import LanguageModel
from entities.chat import ChatAnswer, IntentDecision, MessageInput, RetrievedChunk


class ResponseChat:
    def __init__(self, language_model: LanguageModel) -> None:
        self._language_model = language_model

    async def execute(
        self,
        message: MessageInput,
        decision: IntentDecision,
        context: list[RetrievedChunk],
    ) -> ChatAnswer:
        return await self._language_model.answer(message, decision, context)
