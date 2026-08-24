import asyncio

import pytest

from application.chat_controller import ChatFlowController
from application.use_cases.detect_intent import DetectIntent
from application.use_cases.rag_query import RagQuery
from application.use_cases.response_chat import ResponseChat
from application.use_cases.sanitize_message import SanitizeMessage
from entities.chat import DomainValidationError, Intent
from frameworks_and_drivers.in_memory_session_repository import InMemorySessionRepository
from frameworks_and_drivers.local_intent_resolver import LocalIntentResolver
from frameworks_and_drivers.local_language_model import LocalLanguageModel
from frameworks_and_drivers.local_semantic_sanitizer import LocalSemanticSanitizer
from frameworks_and_drivers.security.in_memory import InMemorySyntacticSanitizer
from frameworks_and_drivers.memory_retriever import MemoryRetriever


def build_flow() -> ChatFlowController:
    flow = ChatFlowController(
        SanitizeMessage(LocalSemanticSanitizer()),
        DetectIntent(LocalIntentResolver()),
        RagQuery(MemoryRetriever()),
        ResponseChat(LocalLanguageModel()),
        InMemorySessionRepository(),
    )
    return flow


def test_technical_question_resolves_intent_retrieves_context_and_answers() -> None:
    answer = asyncio.run(build_flow().execute("¿Qué arquitectura técnica estás construyendo?", None))
    assert answer.intent is Intent.TECHNICAL
    assert "perspectiva técnica" in answer.message.value
    assert "profile/" in answer.sources[0]
    assert answer.session_id


def test_message_input_rejects_empty_and_more_than_500_words() -> None:
    flow = build_flow()
    with pytest.raises(DomainValidationError):
        asyncio.run(flow.execute("   ", None))
    with pytest.raises(DomainValidationError):
        asyncio.run(flow.execute("word " * 501, None))


def test_semantic_sanitizer_rejects_sql_and_code_prompts() -> None:
    flow = build_flow()
    with pytest.raises(DomainValidationError):
        asyncio.run(flow.execute("select password from users", None))
    with pytest.raises(DomainValidationError):
        asyncio.run(flow.execute("```python\nimport os\n```", None))


def test_session_rejects_the_sixth_message() -> None:
    flow = build_flow()
    session_id = "session-test"
    for index in range(5):
        asyncio.run(flow.execute(f"Pregunta número {index}", session_id))
    with pytest.raises(DomainValidationError):
        asyncio.run(flow.execute("Pregunta número seis", session_id))
