from application.ask_portfolio import AskPortfolio
from entities.chat import ChatQuestion
from interface_adapters.schemas import AskRequest, AskResponse


class ChatController:
    def __init__(self, use_case: AskPortfolio) -> None:
        self._use_case = use_case

    async def ask(self, request: AskRequest) -> AskResponse:
        answer = await self._use_case.execute(ChatQuestion(request.message, request.session_id))
        return AskResponse(message=answer.message, sources=list(answer.sources))
