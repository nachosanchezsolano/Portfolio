from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from application.chat_controller import ChatFlowController
from application.ports.observability import Logger, NoopLogger
from application.use_cases.detect_intent import DetectIntent
from application.use_cases.rag_query import RagQuery
from application.use_cases.response_chat import ResponseChat
from application.use_cases.sanitize_message import SanitizeMessage
from entities.chat import DomainValidationError
from application.ports.security_ports import RequestSecurity
from frameworks_and_drivers.in_memory_session_repository import InMemorySessionRepository
from frameworks_and_drivers.in_memory_observation_repository import InMemoryObservationRepository
from frameworks_and_drivers.providers.local.models import LocalIntentResolver, LocalLanguageModel
from frameworks_and_drivers.local_semantic_sanitizer import LocalSemanticSanitizer
from frameworks_and_drivers.providers.local.retrieval import MemoryRetriever
from frameworks_and_drivers.settings import Settings, get_settings
from interface_adapters.controllers import ChatController
from interface_adapters.security.request_security_controller import RequestSecurityController
from interface_adapters.schemas import ChatInput, ChatOutput, MessageTraceOutput, ObservationOutput, SessionTraceOutput

def create_app(
    controller: ChatController,
    security: RequestSecurity,
    settings: Settings | None = None,
    logger: Logger | None = None,
    observations=None,
    traces=None,
) -> FastAPI:
    runtime_settings = settings or get_settings()
    runtime_logger = logger or NoopLogger()
    observation_repository = observations or InMemoryObservationRepository()
    from frameworks_and_drivers.in_memory_chat_trace_repository import InMemoryChatTraceRepository
    trace_repository = traces or InMemoryChatTraceRepository()
    application = FastAPI(title="Portfolio Assistant API", version="0.1.0")
    security_controller = RequestSecurityController(security)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=runtime_settings.origins,
        allow_methods=["POST", "GET"],
        allow_headers=["*"],
    )

    @application.middleware("http")
    async def security_headers(request: Request, call_next):
        try:
            response = await call_next(request)
        except Exception as error:
            runtime_logger.error(
                "http_request_failed",
                method=request.method,
                path=request.url.path,
                error_type=type(error).__name__,
            )
            raise
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        runtime_logger.info(
            "http_request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        )
        return response

    @application.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.post("/v1/chat", response_model=ChatOutput, dependencies=[Depends(security_controller.protect)])
    async def chat(request: ChatInput) -> ChatOutput:
        try:
            return await controller.ask(request)
        except DomainValidationError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    def require_admin_key(value: str | None) -> None:
        if not runtime_settings.admin_api_key or value != runtime_settings.admin_api_key:
            raise HTTPException(status_code=401, detail="invalid admin credentials")

    @application.get("/v1/admin/chat-observations", response_model=list[ObservationOutput])
    async def list_chat_observations(
        limit: int = Query(default=100, ge=1, le=500),
        admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
    ) -> list[ObservationOutput]:
        require_admin_key(admin_key)
        rows = await observation_repository.list_recent(limit)
        return [
            ObservationOutput(
                observation_id=row.observation_id,
                visitor_id=row.visitor_id,
                session_id=row.session_id,
                question=row.question,
                answer=row.answer,
                sources=list(row.sources),
                intent=row.intent.value,
                context_count=row.context_count,
                latency_ms=row.latency_ms,
                created_at=row.created_at,
                correctness=row.correctness,
                feedback_note=row.feedback_note,
            )
            for row in rows
        ]

    @application.post("/v1/admin/chat-observations/{observation_id}/feedback")
    async def add_observation_feedback(
        observation_id: str,
        correctness: str,
        note: str | None = None,
        admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
    ) -> dict[str, str]:
        require_admin_key(admin_key)
        if correctness not in {"correct", "incorrect", "needs_review"}:
            raise HTTPException(status_code=422, detail="invalid correctness value")
        await observation_repository.add_feedback(observation_id, correctness, note)
        return {"status": "ok"}

    @application.get("/v1/admin/chat-sessions", response_model=list[SessionTraceOutput])
    async def list_chat_sessions(
        limit: int = Query(default=100, ge=1, le=500),
        admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
    ) -> list[SessionTraceOutput]:
        require_admin_key(admin_key)
        rows = await trace_repository.list_sessions(limit)
        return [
            SessionTraceOutput(
                session_id=row.session_id,
                visitor_id=row.visitor_id,
                started_at=row.started_at,
                last_seen_at=row.last_seen_at,
                message_count=row.message_count,
                last_intent=row.last_intent.value if row.last_intent else None,
            )
            for row in rows
        ]

    @application.get("/v1/admin/chat-sessions/{session_id}/messages", response_model=list[MessageTraceOutput])
    async def list_chat_messages(
        session_id: str,
        limit: int = Query(default=100, ge=1, le=500),
        admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
    ) -> list[MessageTraceOutput]:
        require_admin_key(admin_key)
        rows = await trace_repository.list_messages(session_id, limit)
        return [
            MessageTraceOutput(
                message_id=row.message_id,
                session_id=row.session_id,
                visitor_id=row.visitor_id,
                turn_index=row.turn_index,
                raw_question=row.raw_question,
                sanitized_question=row.sanitized_question,
                retrieval_query=row.retrieval_query,
                intent=row.intent.value,
                retrieved_context=[
                    {"source": chunk.source, "content": chunk.content, "score": chunk.score}
                    for chunk in row.retrieved_context
                ],
                response_prompt_system=row.response_prompt_system,
                response_prompt_user=row.response_prompt_user,
                final_answer=row.final_answer,
                sources=list(row.sources),
                context_count=row.context_count,
                latency_ms=row.latency_ms,
                status=row.status,
                created_at=row.created_at,
                correctness=row.correctness,
                feedback_note=row.feedback_note,
            )
            for row in rows
        ]

    @application.post("/v1/admin/chat-messages/{message_id}/feedback")
    async def add_message_feedback(
        message_id: str,
        correctness: str,
        note: str | None = None,
        admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
    ) -> dict[str, str]:
        require_admin_key(admin_key)
        if correctness not in {"correct", "incorrect", "needs_review"}:
            raise HTTPException(status_code=422, detail="invalid correctness value")
        await trace_repository.add_feedback(message_id, correctness, note)
        return {"status": "ok"}

    return application


def build_local_controller(traces=None) -> ChatController:
    flow = ChatFlowController(
        sanitizer=SanitizeMessage(LocalSemanticSanitizer()),
        intent=DetectIntent(LocalIntentResolver()),
        rag=RagQuery(MemoryRetriever()),
        response=ResponseChat(LocalLanguageModel()),
        sessions=InMemorySessionRepository(),
        traces=traces,
    )
    from frameworks_and_drivers.providers.local.security import InMemorySyntacticSanitizer

    return ChatController(flow, InMemorySyntacticSanitizer())


def build_local_security() -> RequestSecurity:
    from frameworks_and_drivers.providers.local.security import InMemoryRequestSecurity

    return InMemoryRequestSecurity(
        api_key=get_settings().api_key,
        max_requests=get_settings().rate_limit_requests,
        window_seconds=get_settings().rate_limit_window_seconds,
    )


from frameworks_and_drivers.in_memory_chat_trace_repository import InMemoryChatTraceRepository

_local_traces = InMemoryChatTraceRepository()
app = create_app(build_local_controller(_local_traces), build_local_security(), traces=_local_traces)
