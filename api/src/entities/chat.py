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


@dataclass(frozen=True)
class ConversationTurn:
    user: str
    assistant: str


@dataclass
class ChatSession:
    session_id: str
    messages: list[MessageInput] = field(default_factory=list)
    turns: list[ConversationTurn] = field(default_factory=list)

    def ensure_can_receive(self) -> None:
        if len(self.messages) >= MAX_SESSION_MESSAGES:
            raise DomainValidationError(
                f"chat session cannot contain more than {MAX_SESSION_MESSAGES} messages"
            )

    def add_message(self, message: MessageInput) -> None:
        self.ensure_can_receive()
        self.messages.append(message)

    def add_turn(self, user: MessageInput, assistant: MessageOutput) -> None:
        self.turns.append(ConversationTurn(user.value, assistant.value))


@dataclass(frozen=True)
class IntentDecision:
    intent: Intent
    retrieval_query: str
    retrieval_limit: int = 4


@dataclass(frozen=True)
class RetrievedChunk:
    source: str
    content: str
    score: float | None = None


@dataclass(frozen=True)
class ResponsePrompt:
    system: str
    user: str
    intent: Intent
    context: tuple[RetrievedChunk, ...] = ()
    conversation_history: tuple[ConversationTurn, ...] = ()


@dataclass(frozen=True)
class ChatAnswer:
    message: MessageOutput
    sources: tuple[str, ...] = ()
    intent: Intent = Intent.GENERAL
    session_id: str | None = None
    observation_id: str | None = None


@dataclass(frozen=True)
class ChatObservation:
    observation_id: str
    visitor_id: str
    session_id: str
    question: str
    answer: str
    sources: tuple[str, ...]
    intent: Intent
    context_count: int
    latency_ms: float
    created_at: str
    correctness: str | None = None
    feedback_note: str | None = None


@dataclass(frozen=True)
class ChatMessageTrace:
    message_id: str
    session_id: str
    visitor_id: str
    turn_index: int
    raw_question: str
    sanitized_question: str
    retrieval_query: str
    intent: Intent
    retrieved_context: tuple[RetrievedChunk, ...]
    response_prompt_system: str
    response_prompt_user: str
    final_answer: str
    sources: tuple[str, ...]
    context_count: int
    latency_ms: float
    status: str
    created_at: str
    correctness: str | None = None
    feedback_note: str | None = None


@dataclass(frozen=True)
class ChatSessionTrace:
    session_id: str
    visitor_id: str
    started_at: str
    last_seen_at: str
    message_count: int
    last_intent: Intent | None = None


# Compatibility alias for adapters that still use the old name.
ChatQuestion = MessageInput
