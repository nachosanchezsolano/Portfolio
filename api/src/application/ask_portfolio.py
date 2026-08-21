from application.ports import PortfolioAssistant
from entities.chat import ChatAnswer, ChatQuestion


class AskPortfolio:
    def __init__(self, assistant: PortfolioAssistant, max_message_length: int) -> None:
        self._assistant = assistant
        self._max_message_length = max_message_length

    async def execute(self, question: ChatQuestion) -> ChatAnswer:
        question.validate(self._max_message_length)
        return await self._assistant.answer(question)
