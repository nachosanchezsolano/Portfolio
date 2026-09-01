from pydantic import BaseModel, Field, field_validator

from entities.chat import MAX_MESSAGE_WORDS, count_words


class ChatInput(BaseModel):
    message: str = Field(min_length=1)
    session_id: str | None = Field(default=None, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    visitor_id: str | None = Field(default=None, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    locale: str = Field(default="en", max_length=5, pattern=r"^(en|es)$")
    page_context: str | None = Field(default=None, max_length=240)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("message must not be null or empty")
        if count_words(value) > MAX_MESSAGE_WORDS:
            raise ValueError(f"message cannot exceed {MAX_MESSAGE_WORDS} words")
        return value


class ChatOutput(BaseModel):
    message: str = Field(min_length=1)
    sources: list[str] = Field(default_factory=list)
    intent: str
    session_id: str
    observation_id: str | None = None

    @field_validator("message")
    @classmethod
    def validate_output(cls, value: str) -> str:
        value = value.strip()
        if count_words(value) > MAX_MESSAGE_WORDS:
            raise ValueError(f"response cannot exceed {MAX_MESSAGE_WORDS} words")
        return value


class ObservationOutput(BaseModel):
    observation_id: str
    visitor_id: str
    session_id: str
    question: str
    answer: str
    sources: list[str]
    intent: str
    context_count: int
    latency_ms: float
    created_at: str
    correctness: str | None = None
    feedback_note: str | None = None


class SessionTraceOutput(BaseModel):
    session_id: str
    visitor_id: str
    started_at: str
    last_seen_at: str
    message_count: int
    last_intent: str | None = None


class MessageTraceOutput(BaseModel):
    message_id: str
    session_id: str
    visitor_id: str
    turn_index: int
    raw_question: str
    sanitized_question: str
    retrieval_query: str
    intent: str
    retrieved_context: list[dict]
    response_prompt_system: str
    response_prompt_user: str
    final_answer: str
    sources: list[str]
    context_count: int
    latency_ms: float
    status: str
    created_at: str
    correctness: str | None = None
    feedback_note: str | None = None


AskRequest = ChatInput
AskResponse = ChatOutput
