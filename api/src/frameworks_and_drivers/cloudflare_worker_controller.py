from application.chat_controller import ChatFlowController
from application.use_cases.detect_intent import DetectIntent
from application.use_cases.rag_query import RagQuery
from application.use_cases.response_chat import ResponseChat
from application.use_cases.sanitize_message import SanitizeMessage
from frameworks_and_drivers.providers.cloudflare.ai import CloudflareIntentResolver, CloudflareLanguageModel, CloudflareVectorizeRetriever
from frameworks_and_drivers.in_memory_session_repository import InMemorySessionRepository
from frameworks_and_drivers.local_semantic_sanitizer import LocalSemanticSanitizer
from frameworks_and_drivers.providers.cloudflare.security import CloudflareRequestSecurity
from frameworks_and_drivers.settings import Settings, settings_from_worker_env
from application.ports.observability import Logger


def build_cloudflare_flow(logger: Logger | None = None) -> ChatFlowController:
    return ChatFlowController(
        sanitizer=SanitizeMessage(LocalSemanticSanitizer()),
        intent=DetectIntent(CloudflareIntentResolver()),
        rag=RagQuery(CloudflareVectorizeRetriever()),
        response=ResponseChat(CloudflareLanguageModel()),
        sessions=InMemorySessionRepository(),
        logger=logger,
    )


def build_cloudflare_security(settings: Settings) -> CloudflareRequestSecurity:
    return CloudflareRequestSecurity(
        api_key=settings.api_key,
        max_requests=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )
