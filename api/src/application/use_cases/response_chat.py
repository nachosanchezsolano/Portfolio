from application.ports.model_ports import LanguageModel
from entities.chat import ChatAnswer, ConversationTurn, IntentDecision, MessageInput, RetrievedChunk
from application.use_cases.build_response_prompt import BuildResponsePrompt


class ResponseChat:
    def __init__(self, language_model: LanguageModel, prompt_builder=None) -> None:
        self._language_model = language_model
        self._prompt_builder = prompt_builder or BuildResponsePrompt()

    async def execute(
        self,
        message: MessageInput,
        decision: IntentDecision,
        context: list[RetrievedChunk],
        conversation: list[ConversationTurn] | None = None,
    ) -> ChatAnswer:
        prompt = self._prompt_builder.build(message, decision, context, conversation)
        return await self._language_model.answer(prompt)
