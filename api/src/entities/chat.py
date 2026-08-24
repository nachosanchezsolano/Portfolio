from dataclasses import dataclass, field
from enum import StrEnum

MAX_SESSION_MESSAGES = 5
MAX_MESSAGE_WORDS = 500


class DomainValidationError(ValueError):
    """A business rule rejected a domain value."""


def count_words(value: str) -> int:
    return len(value.split())


class Intent(StrEnum):
    GENERAL = "general"
    RECRUITER = "recruiter"
    TECHNICAL = "technical"


@dataclass(frozen=True)
class MessageInput:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip() if isinstance(self.value, str) else ""
        object.__setattr__(self, "value", normalized)
        if not normalized:
            raise DomainValidationError("message must not be null or empty")
        if count_words(normalized) > MAX_MESSAGE_WORDS:
            raise DomainValidationError(f"message cannot exceed {MAX_MESSAGE_WORDS} words")


@dataclass(frozen=True)
class MessageOutput:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip() if isinstance(self.value, str) else ""
        object.__setattr__(self, "value", normalized)
        if not normalized:
            raise DomainValidationError("response must not be empty")
        if count_words(normalized) > MAX_MESSAGE_WORDS:
            raise DomainValidationError(f"response cannot exceed {MAX_MESSAGE_WORDS} words")


@dataclass
class ChatSession:
    session_id: str
    messages: list[MessageInput] = field(default_factory=list)

    def ensure_can_receive(self) -> None:
        if len(self.messages) >= MAX_SESSION_MESSAGES:
            raise DomainValidationError(
                f"chat session cannot contain more than {MAX_SESSION_MESSAGES} messages"
            )

    def add_message(self, message: MessageInput) -> None:
        self.ensure_can_receive()
        self.messages.append(message)


@dataclass(frozen=True)
class IntentDecision:
    intent: Intent
    retrieval_query: str
    retrieval_limit: int = 4


@dataclass(frozen=True)
class RetrievedChunk:
    source: str
    content: str


@dataclass(frozen=True)
class ChatAnswer:
    message: MessageOutput
    sources: tuple[str, ...] = ()
    intent: Intent = Intent.GENERAL
    session_id: str | None = None


# Compatibility alias for adapters that still use the old name.
ChatQuestion = MessageInput
