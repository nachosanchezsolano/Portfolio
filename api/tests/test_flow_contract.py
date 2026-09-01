import asyncio

import pytest

from application.chat_controller import ChatFlowController
from application.use_cases.detect_intent import DetectIntent
from application.use_cases.rag_query import RagQuery
from application.use_cases.response_chat import ResponseChat
from application.use_cases.build_response_prompt import BuildResponsePrompt
from application.use_cases.sanitize_message import SanitizeMessage
from entities.chat import ChatAnswer, Intent, IntentDecision, MessageInput, MessageOutput, ResponsePrompt, RetrievedChunk


class RecordingSanitizer:
    def __init__(self, events: list[str]) -> None:
        self.events = events

    async def sanitize(self, message: MessageInput) -> MessageInput:
        self.events.append("sanitize")
        return MessageInput("normalized question")


class RecordingIntentResolver:
    def __init__(self, events: list[str]) -> None:
        self.events = events

    async def resolve(self, message: MessageInput) -> IntentDecision:
        self.events.append(f"intent:{message.value}")
        return IntentDecision(Intent.TECHNICAL, "normalized retrieval query", 2)


class RecordingRetriever:
    def __init__(self, events: list[str]) -> None:
        self.events = events

    async def retrieve(self, query: str, limit: int) -> list[RetrievedChunk]:
        self.events.append(f"rag:{query}:{limit}")
        return [RetrievedChunk("profile/test.md", "evidence")]


class RecordingLanguageModel:
    def __init__(self, events: list[str]) -> None:
        self.events = events

    async def answer(self, prompt: ResponsePrompt) -> ChatAnswer:
        self.events.append(f"response:{prompt.user}:{len(prompt.context)}")
        return ChatAnswer(MessageOutput("grounded answer"), (prompt.context[0].source,), prompt.intent)


class FailingLanguageModel(RecordingLanguageModel):
    async def answer(self, prompt: ResponsePrompt) -> ChatAnswer:
        self.events.append("response:failed")
        raise RuntimeError("model unavailable")


class RecordingSessionRepository:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.saved = None

    async def get_or_create(self, session_id: str | None):
        self.events.append(f"session:get:{session_id}")
        from entities.chat import ChatSession

        return ChatSession(session_id or "generated")

    async def save(self, session) -> None:
        self.events.append("session:save")
        self.saved = session


def test_flow_sanitizes_before_intent_rag_and_response() -> None:
    events: list[str] = []
    flow = ChatFlowController(
        SanitizeMessage(RecordingSanitizer(events)),
        DetectIntent(RecordingIntentResolver(events)),
        RagQuery(RecordingRetriever(events)),
        ResponseChat(RecordingLanguageModel(events)),
        RecordingSessionRepository(events),
    )

    answer = asyncio.run(flow.execute("raw user input", "session-1"))

    assert events == [
        "session:get:session-1",
        "sanitize",
        "intent:normalized question",
        "rag:normalized retrieval query:2",
        "response:normalized question:1",
        "session:save",
    ]
    assert answer.message.value == "grounded answer"
    assert answer.intent is Intent.TECHNICAL
    assert answer.sources == ("profile/test.md",)
    assert answer.session_id == "session-1"


def test_flow_builds_main_prompt_with_rag_context_before_response() -> None:
    events: list[str] = []
    flow = ChatFlowController(
        SanitizeMessage(RecordingSanitizer(events)),
        DetectIntent(RecordingIntentResolver(events)),
        RagQuery(RecordingRetriever(events)),
        ResponseChat(RecordingLanguageModel(events)),
        RecordingSessionRepository(events),
    )

    asyncio.run(flow.execute("raw user input", "session-1"))

    assert events[-2:] == ["response:normalized question:1", "session:save"]


def test_flow_does_not_commit_session_when_response_generation_fails() -> None:
    events: list[str] = []
    flow = ChatFlowController(
        SanitizeMessage(RecordingSanitizer(events)),
        DetectIntent(RecordingIntentResolver(events)),
        RagQuery(RecordingRetriever(events)),
        ResponseChat(FailingLanguageModel(events)),
        RecordingSessionRepository(events),
    )

    with pytest.raises(RuntimeError, match="model unavailable"):
        asyncio.run(flow.execute("raw user input", "session-1"))

    assert "session:save" not in events


def test_prompt_includes_locale_and_page_context_without_treating_it_as_evidence() -> None:
    prompt = BuildResponsePrompt().build(
        MessageInput("¿Por qué usaste RAG?"),
        IntentDecision(Intent.TECHNICAL, "RAG architecture"),
        [RetrievedChunk("projects/assistant.md", "RAG evidence")],
        locale="es",
        page_context="AI Portfolio Assistant",
    )

    assert "Idioma preferido de la interfaz: es" in prompt.system
    assert "AI Portfolio Assistant" in prompt.system
    assert "no lo trates como evidencia" in prompt.system
    assert prompt.locale == "es"
    assert prompt.page_context == "AI Portfolio Assistant"
