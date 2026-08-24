from application.ports.retrieval_ports import SessionRepository
from application.use_cases.detect_intent import DetectIntent
from application.use_cases.rag_query import RagQuery
from application.use_cases.response_chat import ResponseChat
from application.use_cases.sanitize_message import SanitizeMessage
from entities.chat import ChatAnswer, ChatSession, MessageInput


class ChatFlowController:
    """Coordinates dependent use cases without putting business logic in HTTP."""

    def __init__(
        self,
        sanitizer: SanitizeMessage,
        intent: DetectIntent,
        rag: RagQuery,
        response: ResponseChat,
        sessions: SessionRepository,
    ) -> None:
        self._sanitizer = sanitizer
        self._intent = intent
        self._rag = rag
        self._response = response
        self._sessions = sessions

    async def execute(self, raw_message: str, session_id: str | None) -> ChatAnswer:
        session = await self._sessions.get_or_create(session_id)
        message = await self._sanitizer.execute(MessageInput(raw_message))
        session.add_message(message)

        decision = await self._intent.execute(message)
        context = await self._rag.execute(decision)
        answer = await self._response.execute(message, decision, context)
        answer = ChatAnswer(answer.message, answer.sources, answer.intent, session.session_id)
        await self._sessions.save(session)
        return answer
