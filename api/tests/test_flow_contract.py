import asyncio

import pytest

from application.chat_controller import ChatFlowController
from application.use_cases.detect_intent import DetectIntent
from application.use_cases.rag_query import RagQuery
from application.use_cases.response_chat import ResponseChat
from application.use_cases.sanitize_message import SanitizeMessage
from entities.chat import ChatAnswer, Intent, IntentDecision, MessageInput, MessageOutput, RetrievedChunk


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

    async def answer(self, message, decision, context) -> ChatAnswer:
        self.events.append(f"response:{message.value}:{len(context)}")
        return ChatAnswer(MessageOutput("grounded answer"), (context[0].source,), decision.intent)


class FailingLanguageModel(RecordingLanguageModel):
    async def answer(self, message, decision, context) -> ChatAnswer:
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
