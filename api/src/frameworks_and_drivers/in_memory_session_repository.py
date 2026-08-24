from copy import deepcopy
from uuid import uuid4

from entities.chat import ChatSession


class InMemorySessionRepository:
    """Prototype repository; replace with a database-backed repository later."""

    def __init__(self) -> None:
        self._sessions: dict[str, ChatSession] = {}

    async def get_or_create(self, session_id: str | None) -> ChatSession:
        key = session_id or str(uuid4())
        if key not in self._sessions:
            self._sessions[key] = ChatSession(key)
        return deepcopy(self._sessions[key])

    async def save(self, session: ChatSession) -> None:
        self._sessions[session.session_id] = deepcopy(session)
