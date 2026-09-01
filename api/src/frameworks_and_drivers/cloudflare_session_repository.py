from typing import Any
from uuid import uuid4

from entities.chat import ChatSession, ConversationTurn, MessageInput, MessageOutput
from frameworks_and_drivers.cloudflare_context import to_python


class CloudflareD1SessionRepository:
    """Rebuilds the model context from the durable chat_messages table."""

    def __init__(self, database: Any) -> None:
        self._database = database

    async def get_or_create(self, session_id: str | None) -> ChatSession:
        resolved_id = session_id or str(uuid4())
        result = await self._database.prepare(
            """SELECT sanitized_question, final_answer
               FROM chat_messages WHERE session_id = ? ORDER BY turn_index ASC"""
        ).bind(resolved_id).all()
        rows = to_python(result).get("results", [])
        session = ChatSession(resolved_id)
        for row in rows:
            question = MessageInput(str(row["sanitized_question"]))
            answer = MessageOutput(str(row["final_answer"]))
            session.messages.append(question)
            session.turns.append(ConversationTurn(question.value, answer.value))
        return session

    async def save(self, session: ChatSession) -> None:
        # The trace repository writes the session and message atomically enough
        # for the Worker flow; message rows are the source of truth for context.
        return None
