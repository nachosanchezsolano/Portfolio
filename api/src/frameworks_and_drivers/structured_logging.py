import json
from datetime import datetime, timezone
from typing import Any


class StructuredLogger:
    """Emits compact JSON logs compatible with Cloudflare Observability."""

    def __init__(self, **base_fields: Any) -> None:
        self._base_fields = base_fields

    def _write(self, level: str, event: str, fields: dict[str, Any]) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "service": "portfolio-api",
            "event": event,
            **self._base_fields,
            **fields,
        }
        print(json.dumps(entry, ensure_ascii=False, separators=(",", ":")))

    def info(self, event: str, **fields: Any) -> None:
        self._write("info", event, fields)

    def warning(self, event: str, **fields: Any) -> None:
        self._write("warning", event, fields)

    def error(self, event: str, **fields: Any) -> None:
        self._write("error", event, fields)
