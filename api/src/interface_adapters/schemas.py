from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1200)
    session_id: str | None = Field(default=None, max_length=80)


class AskResponse(BaseModel):
    message: str
    sources: list[str]
