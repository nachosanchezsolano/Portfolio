from pydantic import BaseModel, Field, field_validator

from entities.chat import MAX_MESSAGE_WORDS, count_words


class ChatInput(BaseModel):
    message: str = Field(min_length=1)
    session_id: str | None = Field(default=None, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")

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

    @field_validator("message")
    @classmethod
    def validate_output(cls, value: str) -> str:
        value = value.strip()
        if count_words(value) > MAX_MESSAGE_WORDS:
            raise ValueError(f"response cannot exceed {MAX_MESSAGE_WORDS} words")
        return value


AskRequest = ChatInput
AskResponse = ChatOutput
