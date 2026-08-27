from application.chat_controller import ChatFlowController
from application.ports.security_ports import SyntacticSanitizer
from interface_adapters.schemas import ChatInput, ChatOutput


class ChatController:
    """HTTP adapter: translates request/response models and delegates the flow."""

    def __init__(self, flow: ChatFlowController, syntax_sanitizer: SyntacticSanitizer) -> None:
        self._flow = flow
        self._syntax_sanitizer = syntax_sanitizer

    async def ask(self, request: ChatInput) -> ChatOutput:
        message = self._syntax_sanitizer.sanitize(request.message)
        answer = await self._flow.execute(message, request.session_id, request.visitor_id)
        return ChatOutput(
            message=answer.message.value,
            sources=list(answer.sources),
            intent=answer.intent.value,
            session_id=answer.session_id or request.session_id or "",
            observation_id=answer.observation_id,
        )
