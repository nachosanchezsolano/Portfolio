from dataclasses import dataclass


@dataclass(frozen=True)
class ChatQuestion:
    message: str
    session_id: str | None = None

    def validate(self, max_length: int) -> None:
        if not self.message.strip():
            raise ValueError("message must not be empty")
        if len(self.message.strip()) > max_length:
            raise ValueError(f"message exceeds the {max_length} character limit")


@dataclass(frozen=True)
class ChatAnswer:
    message: str
    sources: tuple[str, ...] = ()
