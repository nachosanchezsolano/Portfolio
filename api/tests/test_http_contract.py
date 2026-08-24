import asyncio

import pytest

from entities.chat import ChatAnswer, DomainValidationError, Intent, MessageOutput
from frameworks_and_drivers.security.in_memory import InMemorySyntacticSanitizer
from interface_adapters.controllers import ChatController
from interface_adapters.schemas import ChatInput, ChatOutput


class FakeFlow:
    async def execute(self, message: str, session_id: str | None):
        return ChatAnswer(
            MessageOutput("respuesta segura"),
            ("profile/test.md",),
            Intent.GENERAL,
            session_id or "generated-session",
        )


class FakeSyntaxSanitizer:
    def sanitize(self, value: str) -> str:
        return value.replace("unsafe", "safe")


def test_http_controller_sanitizes_and_maps_response() -> None:
    response = asyncio.run(
        ChatController(FakeFlow(), FakeSyntaxSanitizer()).ask(
            ChatInput(message="unsafe question", session_id="session-1")
        )
    )

    assert isinstance(response, ChatOutput)
    assert response.message == "respuesta segura"
    assert response.sources == ["profile/test.md"]
    assert response.intent == "general"
    assert response.session_id == "session-1"


def test_http_input_rejects_invalid_session_id() -> None:
    with pytest.raises(ValueError):
        ChatInput(message="valid question", session_id="invalid session")


def test_http_controller_blocks_unsafe_syntax_before_flow() -> None:
    with pytest.raises(DomainValidationError, match="unsafe syntax"):
        asyncio.run(
            ChatController(FakeFlow(), InMemorySyntacticSanitizer()).ask(
                ChatInput(message="SELECT password FROM users")
            )
        )


def test_http_input_rejects_more_than_500_words() -> None:
    with pytest.raises(ValueError):
        ChatInput(message="word " * 501)


def test_http_output_rejects_more_than_500_words() -> None:
    with pytest.raises(ValueError):
        ChatOutput(message="word " * 501, intent="general", session_id="s")
