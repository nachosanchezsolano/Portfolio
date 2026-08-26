from typing import Any, Protocol


class Logger(Protocol):
    def info(self, event: str, **fields: Any) -> None: ...

    def warning(self, event: str, **fields: Any) -> None: ...

    def error(self, event: str, **fields: Any) -> None: ...


class NoopLogger:
    def info(self, event: str, **fields: Any) -> None:
        return None

    def warning(self, event: str, **fields: Any) -> None:
        return None

    def error(self, event: str, **fields: Any) -> None:
        return None
