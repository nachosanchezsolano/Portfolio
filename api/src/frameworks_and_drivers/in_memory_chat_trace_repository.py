from entities.chat import ChatMessageTrace, ChatSessionTrace


class InMemoryChatTraceRepository:
    def __init__(self) -> None:
        self._sessions: dict[str, ChatSessionTrace] = {}
        self._messages: dict[str, ChatMessageTrace] = {}

    async def save_session(self, session: ChatSessionTrace) -> None:
        self._sessions[session.session_id] = session

    async def save_message(self, message: ChatMessageTrace) -> None:
        self._messages[message.message_id] = message
        session = self._sessions.get(message.session_id)
        if session:
            self._sessions[session.session_id] = ChatSessionTrace(
                session.session_id, session.visitor_id, session.started_at,
                message.created_at, session.message_count + 1, message.intent,
            )

    async def list_sessions(self, limit: int = 100) -> list[ChatSessionTrace]:
        return list(self._sessions.values())[-max(1, min(limit, 500)) :][::-1]

    async def list_messages(self, session_id: str, limit: int = 100) -> list[ChatMessageTrace]:
        rows = [row for row in self._messages.values() if row.session_id == session_id]
        return rows[-max(1, min(limit, 500)) :][::-1]

    async def add_feedback(self, message_id: str, correctness: str, note: str | None = None) -> None:
        message = self._messages.get(message_id)
        if message is None:
            return
        self._messages[message_id] = ChatMessageTrace(
            **{**message.__dict__, "correctness": correctness, "feedback_note": note}
        )
