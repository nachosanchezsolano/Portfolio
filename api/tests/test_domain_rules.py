import pytest

from entities.chat import (
    MAX_MESSAGE_WORDS,
    MAX_SESSION_MESSAGES,
    ChatSession,
    DomainValidationError,
    MessageInput,
    MessageOutput,
)


def test_message_input_rejects_none_empty_and_over_limit() -> None:
    for value in (None, "", "   "):
        with pytest.raises(DomainValidationError):
            MessageInput(value)  # type: ignore[arg-type]

    MessageInput("word " * MAX_MESSAGE_WORDS)
    with pytest.raises(DomainValidationError, match="500 words"):
        MessageInput("word " * (MAX_MESSAGE_WORDS + 1))


def test_message_output_enforces_the_same_word_limit() -> None:
    MessageOutput("respuesta " * MAX_MESSAGE_WORDS)
    with pytest.raises(DomainValidationError, match="500 words"):
        MessageOutput("respuesta " * (MAX_MESSAGE_WORDS + 1))


def test_chat_session_rejects_the_sixth_message() -> None:
    session = ChatSession("test-session")
    for index in range(MAX_SESSION_MESSAGES):
        session.add_message(MessageInput(f"message {index}"))

    assert len(session.messages) == MAX_SESSION_MESSAGES
    with pytest.raises(DomainValidationError, match="5 messages"):
        session.add_message(MessageInput("message six"))
