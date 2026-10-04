from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4
import hashlib
import json

from application.ports.observability import Logger, NoopLogger
from application.ports.retrieval_ports import ChatRequestRepository, ChatTraceRepository, ObservationRepository, SessionRepository
from application.use_cases.detect_intent import DetectIntent
from application.use_cases.rag_query import RagQuery
from application.use_cases.response_chat import ResponseChat
from application.use_cases.sanitize_message import SanitizeMessage
from entities.chat import ChatAnswer, ChatMessageTrace, ChatObservation, ChatSession, ChatSessionTrace, MessageInput, DomainValidationError, RequestInProgressError
from frameworks_and_drivers.in_memory_observation_repository import InMemoryObservationRepository
from frameworks_and_drivers.chat_request_repository import InMemoryChatRequestRepository


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
        observations: ObservationRepository | None = None,
        traces: ChatTraceRepository | None = None,
        requests: ChatRequestRepository | None = None,
    ) -> None:
        self._sanitizer = sanitizer
        self._intent = intent
        self._rag = rag
        self._response = response
        self._sessions = sessions
        self._logger = logger or NoopLogger()
        self._observations = observations or InMemoryObservationRepository()
        self._traces = traces
        self._requests = requests or InMemoryChatRequestRepository()

    async def execute(
        self, raw_message: str, session_id: str | None, visitor_id: str | None = None,
        locale: str = 'en', page_context: str | None = None, request_id: str | None = None,
    ) -> ChatAnswer:
        if not request_id:
            return await self._execute(raw_message, session_id, visitor_id, locale, page_context)
        if not session_id:
            raise DomainValidationError('session_id is required with request_id')
        key = hashlib.sha256(f'{session_id}:{request_id}'.encode()).hexdigest()
        fingerprint = hashlib.sha256(json.dumps([raw_message, locale, page_context], ensure_ascii=False).encode()).hexdigest()
        previous = await self._requests.get(key)
        if previous:
            if previous[0] != fingerprint:
                raise DomainValidationError('request_id was used for a different question')
            if previous[1]:
                return previous[1]
        if not await self._requests.claim(key, fingerprint):
            # A competing Worker may have completed between get and claim.
            previous = await self._requests.get(key)
            if previous and previous[0] != fingerprint:
                raise DomainValidationError('request_id was used for a different question')
            if previous and previous[1]:
                return previous[1]
            raise RequestInProgressError('This question is still processing; retry shortly')
        try:
            answer = await self._execute(raw_message, session_id, visitor_id, locale, page_context, key)
            await self._requests.complete(key, fingerprint, answer)
            return answer
        except Exception:
            await self._requests.release(key, fingerprint)
            raise

    async def _execute(
        self,
        raw_message: str,
        session_id: str | None,
        visitor_id: str | None = None,
        locale: str = "en",
        page_context: str | None = None,
        observation_id: str | None = None,
    ) -> ChatAnswer:
        started = perf_counter()
        self._logger.info(
            "chat_flow_started",
            session_id_present=bool(session_id),
            input_word_count=len(raw_message.split()),
        )
        session = await self._sessions.get_or_create(session_id)
        now = datetime.now(timezone.utc).isoformat()
        if self._traces:
            try:
                await self._traces.save_session(
                    ChatSessionTrace(
                        session_id=session.session_id,
                        visitor_id=visitor_id or "anonymous",
                        started_at=now,
                        last_seen_at=now,
                        message_count=len(session.messages),
                    )
                )
            except Exception as error:
                self._logger.warning("chat_session_trace_failed", error_type=type(error).__name__)
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
        decision = await self._intent.execute(message, session.turns, page_context)
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
            retrieval_scores=[chunk.score for chunk in context if chunk.score is not None],
        )

        stage_started = perf_counter()
        prompt = self._response.build_prompt(message, decision, context, session.turns, locale, page_context)
        answer = await self._response.execute_prompt(prompt)
        self._logger.info(
            "response_generated",
            duration_ms=round((perf_counter() - stage_started) * 1000, 2),
            context_count=len(context),
            output_word_count=len(answer.message.value.split()),
            fallback=not bool(context),
        )
        observation_id = observation_id or str(uuid4())
        answer = ChatAnswer(
            answer.message,
            answer.sources,
            answer.intent,
            session.session_id,
            observation_id,
        )
        try:
            await self._observations.save(
                ChatObservation(
                    observation_id=observation_id,
                    visitor_id=visitor_id or "anonymous",
                    session_id=session.session_id,
                    question=message.value,
                    answer=answer.message.value,
                    sources=answer.sources,
                    intent=answer.intent,
                    context_count=len(context),
                    latency_ms=round((perf_counter() - started) * 1000, 2),
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
            )
        except Exception as error:
            self._logger.warning(
                "chat_observation_failed",
                error_type=type(error).__name__,
            )
        if self._traces:
            try:
                await self._traces.save_message(
                    ChatMessageTrace(
                        message_id=observation_id,
                        session_id=session.session_id,
                        visitor_id=visitor_id or "anonymous",
                        turn_index=len(session.turns),
                        raw_question=raw_message,
                        sanitized_question=message.value,
                        retrieval_query=decision.retrieval_query,
                        intent=decision.intent,
                        retrieved_context=tuple(context),
                        response_prompt_system=prompt.system,
                        response_prompt_user=prompt.user,
                        final_answer=answer.message.value,
                        sources=answer.sources,
                        context_count=len(context),
                        latency_ms=round((perf_counter() - started) * 1000, 2),
                        status="completed",
                        created_at=now,
                    )
                )
            except Exception as error:
                self._logger.warning("chat_trace_failed", error_type=type(error).__name__)
        session.add_turn(message, answer.message)
        await self._sessions.save(session)
        self._logger.info(
            "chat_flow_completed",
            duration_ms=round((perf_counter() - started) * 1000, 2),
            context_count=len(context),
        )
        return answer
