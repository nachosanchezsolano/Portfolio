import asyncio

from application.chat_controller import ChatFlowController
from application.use_cases.detect_intent import DetectIntent
from application.use_cases.rag_query import RagQuery
from application.use_cases.response_chat import ResponseChat
from application.use_cases.sanitize_message import SanitizeMessage
from entities.chat import Intent
from frameworks_and_drivers.in_memory_observation_repository import InMemoryObservationRepository
from frameworks_and_drivers.in_memory_chat_trace_repository import InMemoryChatTraceRepository
from frameworks_and_drivers.in_memory_session_repository import InMemorySessionRepository
from frameworks_and_drivers.local_intent_resolver import LocalIntentResolver
from frameworks_and_drivers.local_language_model import LocalLanguageModel
from frameworks_and_drivers.local_semantic_sanitizer import LocalSemanticSanitizer
from frameworks_and_drivers.memory_retriever import MemoryRetriever


def test_chat_flow_persists_anonymous_observation_for_review() -> None:
    observations = InMemoryObservationRepository()
    flow = ChatFlowController(
        SanitizeMessage(LocalSemanticSanitizer()),
        DetectIntent(LocalIntentResolver()),
        RagQuery(MemoryRetriever()),
        ResponseChat(LocalLanguageModel()),
        InMemorySessionRepository(),
        observations=observations,
    )

    answer = asyncio.run(flow.execute("¿Qué estás construyendo?", "session-1", "visitor-1"))
    rows = asyncio.run(observations.list_recent())

    assert answer.observation_id == rows[0].observation_id
    assert rows[0].visitor_id == "visitor-1"
    assert rows[0].question == "¿Qué estás construyendo?"
    assert rows[0].answer == answer.message.value
    assert rows[0].intent is Intent.GENERAL
    assert rows[0].context_count > 0


def test_observation_feedback_can_mark_a_response_for_review() -> None:
    observations = InMemoryObservationRepository()
    flow = ChatFlowController(
        SanitizeMessage(LocalSemanticSanitizer()),
        DetectIntent(LocalIntentResolver()),
        RagQuery(MemoryRetriever()),
        ResponseChat(LocalLanguageModel()),
        InMemorySessionRepository(),
        observations=observations,
    )

    answer = asyncio.run(flow.execute("¿Qué hacés?", "session-1", "visitor-1"))
    asyncio.run(observations.add_feedback(answer.observation_id or "", "needs_review", "revisar fuente"))
    row = asyncio.run(observations.list_recent())[0]

    assert row.correctness == "needs_review"
    assert row.feedback_note == "revisar fuente"


def test_chat_flow_persists_session_and_full_message_trace() -> None:
    traces = InMemoryChatTraceRepository()
    flow = ChatFlowController(
        SanitizeMessage(LocalSemanticSanitizer()),
        DetectIntent(LocalIntentResolver()),
        RagQuery(MemoryRetriever()),
        ResponseChat(LocalLanguageModel()),
        InMemorySessionRepository(),
        traces=traces,
    )

    answer = asyncio.run(flow.execute("¿Qué estás construyendo?", "session-trace", "visitor-trace"))
    sessions = asyncio.run(traces.list_sessions())
    messages = asyncio.run(traces.list_messages("session-trace"))

    assert sessions[0].session_id == "session-trace"
    assert sessions[0].message_count == 1
    assert messages[0].message_id == answer.observation_id
    assert messages[0].raw_question == "¿Qué estás construyendo?"
    assert messages[0].retrieval_query
    assert messages[0].retrieved_context
    assert messages[0].response_prompt_system
    assert messages[0].final_answer == answer.message.value
