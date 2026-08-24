from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from application.chat_controller import ChatFlowController
from application.use_cases.detect_intent import DetectIntent
from application.use_cases.rag_query import RagQuery
from application.use_cases.response_chat import ResponseChat
from application.use_cases.sanitize_message import SanitizeMessage
from entities.chat import DomainValidationError
from application.ports.security_ports import RequestSecurity
from frameworks_and_drivers.in_memory_session_repository import InMemorySessionRepository
from frameworks_and_drivers.providers.local.models import LocalIntentResolver, LocalLanguageModel
from frameworks_and_drivers.local_semantic_sanitizer import LocalSemanticSanitizer
from frameworks_and_drivers.providers.local.retrieval import MemoryRetriever
from frameworks_and_drivers.settings import get_settings
from interface_adapters.controllers import ChatController
from interface_adapters.security.request_security_controller import RequestSecurityController
from interface_adapters.schemas import ChatInput, ChatOutput

settings = get_settings()


def create_app(controller: ChatController, security: RequestSecurity) -> FastAPI:
    application = FastAPI(title="Portfolio Assistant API", version="0.1.0")
    security_controller = RequestSecurityController(security)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins,
        allow_methods=["POST", "GET"],
        allow_headers=["*"],
    )

    @application.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
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

    return application


def build_local_controller() -> ChatController:
    flow = ChatFlowController(
        sanitizer=SanitizeMessage(LocalSemanticSanitizer()),
        intent=DetectIntent(LocalIntentResolver()),
        rag=RagQuery(MemoryRetriever()),
        response=ResponseChat(LocalLanguageModel()),
        sessions=InMemorySessionRepository(),
    )
    from frameworks_and_drivers.providers.local.security import InMemorySyntacticSanitizer

    return ChatController(flow, InMemorySyntacticSanitizer())


def build_local_security() -> RequestSecurity:
    from frameworks_and_drivers.providers.local.security import InMemoryRequestSecurity

    return InMemoryRequestSecurity(
        api_key=settings.api_key,
        max_requests=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )


app = create_app(build_local_controller(), build_local_security())
