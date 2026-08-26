from time import perf_counter

from application.ports.observability import Logger, NoopLogger
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
        logger: Logger | None = None,
    ) -> None:
        self._sanitizer = sanitizer
        self._intent = intent
        self._rag = rag
        self._response = response
        self._sessions = sessions
        self._logger = logger or NoopLogger()

    async def execute(self, raw_message: str, session_id: str | None) -> ChatAnswer:
        started = perf_counter()
        self._logger.info(
            "chat_flow_started",
            session_id_present=bool(session_id),
            input_word_count=len(raw_message.split()),
        )
        session = await self._sessions.get_or_create(session_id)
        self._logger.info(
            "session_loaded",
            session_id_present=bool(session_id),
            session_message_count=len(session.messages),
        )

        stage_started = perf_counter()
        message = await self._sanitizer.execute(MessageInput(raw_message))
        self._logger.info(
            "message_sanitized",
            duration_ms=round((perf_counter() - stage_started) * 1000, 2),
            word_count=len(message.value.split()),
        )
        session.add_message(message)

        stage_started = perf_counter()
        decision = await self._intent.execute(message)
        self._logger.info(
            "intent_detected",
            duration_ms=round((perf_counter() - stage_started) * 1000, 2),
            intent=decision.intent.value,
            retrieval_query_word_count=len(decision.retrieval_query.split()),
        )

        stage_started = perf_counter()
        context = await self._rag.execute(decision)
        self._logger.info(
            "rag_completed",
            duration_ms=round((perf_counter() - stage_started) * 1000, 2),
            context_count=len(context),
        )

        stage_started = perf_counter()
        answer = await self._response.execute(message, decision, context)
        self._logger.info(
            "response_generated",
            duration_ms=round((perf_counter() - stage_started) * 1000, 2),
            context_count=len(context),
            output_word_count=len(answer.message.value.split()),
            fallback=not bool(context),
        )
        answer = ChatAnswer(answer.message, answer.sources, answer.intent, session.session_id)
        await self._sessions.save(session)
        self._logger.info(
            "chat_flow_completed",
            duration_ms=round((perf_counter() - started) * 1000, 2),
            context_count=len(context),
        )
        return answer
