import json
from typing import Any

from entities.chat import ChatMessageTrace, ChatSessionTrace, Intent, RetrievedChunk
from frameworks_and_drivers.cloudflare_context import to_python


class CloudflareD1ChatTraceRepository:
    def __init__(self, database: Any) -> None:
        self._database = database

    async def save_session(self, session: ChatSessionTrace) -> None:
        await self._database.prepare(
            """INSERT INTO chat_sessions
            (session_id, visitor_id, started_at, last_seen_at, message_count, last_intent)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
              visitor_id = excluded.visitor_id,
              last_seen_at = excluded.last_seen_at,
              last_intent = excluded.last_intent"""
        ).bind(
            session.session_id, session.visitor_id, session.started_at,
            session.last_seen_at, session.message_count,
            session.last_intent.value if session.last_intent else None,
        ).run()

    async def save_message(self, message: ChatMessageTrace) -> None:
        context = [
            {"source": chunk.source, "content": chunk.content, "score": chunk.score}
            for chunk in message.retrieved_context
        ]
        await self._database.prepare(
            """INSERT INTO chat_messages
            (message_id, session_id, visitor_id, turn_index, raw_question,
             sanitized_question, retrieval_query, intent, retrieved_context,
             response_prompt_system, response_prompt_user, final_answer, sources,
             context_count, latency_ms, status, created_at, correctness, feedback_note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        ).bind(
            message.message_id, message.session_id, message.visitor_id, message.turn_index,
            message.raw_question, message.sanitized_question, message.retrieval_query,
            message.intent.value, json.dumps(context, ensure_ascii=False),
            message.response_prompt_system, message.response_prompt_user,
            message.final_answer, json.dumps(message.sources, ensure_ascii=False),
            message.context_count, message.latency_ms, message.status, message.created_at,
            message.correctness, message.feedback_note,
        ).run()
        await self._database.prepare(
            """UPDATE chat_sessions
               SET message_count = message_count + 1,
                   last_seen_at = ?, last_intent = ?
               WHERE session_id = ?"""
        ).bind(message.created_at, message.intent.value, message.session_id).run()

    async def list_sessions(self, limit: int = 100) -> list[ChatSessionTrace]:
        result = await self._database.prepare(
            "SELECT * FROM chat_sessions ORDER BY last_seen_at DESC LIMIT ?"
        ).bind(max(1, min(limit, 500))).all()
        rows = to_python(result).get("results", [])
        return [
            ChatSessionTrace(
                str(row["session_id"]), str(row["visitor_id"]), str(row["started_at"]),
                str(row["last_seen_at"]), int(row["message_count"]),
                Intent(str(row["last_intent"])) if row.get("last_intent") else None,
            ) for row in rows
        ]

    async def list_messages(self, session_id: str, limit: int = 100) -> list[ChatMessageTrace]:
        result = await self._database.prepare(
            "SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at DESC LIMIT ?"
        ).bind(session_id, max(1, min(limit, 500))).all()
        rows = to_python(result).get("results", [])
        return [self._message_from_row(row) for row in rows]

    async def add_feedback(self, message_id: str, correctness: str, note: str | None = None) -> None:
        await self._database.prepare(
            "UPDATE chat_messages SET correctness = ?, feedback_note = ? WHERE message_id = ?"
        ).bind(correctness, note, message_id).run()

    @staticmethod
    def _message_from_row(row: dict[str, Any]) -> ChatMessageTrace:
        context = json.loads(str(row.get("retrieved_context", "[]")))
        return ChatMessageTrace(
            message_id=str(row["message_id"]), session_id=str(row["session_id"]),
            visitor_id=str(row["visitor_id"]), turn_index=int(row["turn_index"]),
            raw_question=str(row["raw_question"]), sanitized_question=str(row["sanitized_question"]),
            retrieval_query=str(row["retrieval_query"]), intent=Intent(str(row["intent"])),
            retrieved_context=tuple(RetrievedChunk(str(item["source"]), str(item["content"]), item.get("score")) for item in context),
            response_prompt_system=str(row["response_prompt_system"]),
            response_prompt_user=str(row["response_prompt_user"]), final_answer=str(row["final_answer"]),
            sources=tuple(json.loads(str(row.get("sources", "[]")))), context_count=int(row["context_count"]),
            latency_ms=float(row["latency_ms"]), status=str(row["status"]), created_at=str(row["created_at"]),
            correctness=row.get("correctness"), feedback_note=row.get("feedback_note"),
        )
