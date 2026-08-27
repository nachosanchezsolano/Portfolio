from typing import Any

from entities.chat import ChatObservation, Intent
from frameworks_and_drivers.cloudflare_context import to_python


class CloudflareD1ObservationRepository:
    """D1-backed conversation observations exposed through the Worker DB binding."""

    def __init__(self, database: Any) -> None:
        self._database = database

    async def save(self, observation: ChatObservation) -> None:
        await self._database.prepare(
            """INSERT INTO chat_observations
            (observation_id, visitor_id, session_id, question, answer, sources,
             intent, context_count, latency_ms, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        ).bind(
            observation.observation_id,
            observation.visitor_id,
            observation.session_id,
            observation.question,
            observation.answer,
            "\n".join(observation.sources),
            observation.intent.value,
            observation.context_count,
            observation.latency_ms,
            observation.created_at,
        ).run()

    async def list_recent(self, limit: int = 100) -> list[ChatObservation]:
        result = await self._database.prepare(
            "SELECT * FROM chat_observations ORDER BY created_at DESC LIMIT ?"
        ).bind(max(1, min(limit, 500))).all()
        rows = to_python(result).get("results", [])
        return [
            ChatObservation(
                observation_id=str(row["observation_id"]),
                visitor_id=str(row["visitor_id"]),
                session_id=str(row["session_id"]),
                question=str(row["question"]),
                answer=str(row["answer"]),
                sources=tuple(filter(None, str(row.get("sources", "")).split("\n"))),
                intent=Intent(str(row["intent"])),
                context_count=int(row["context_count"]),
                latency_ms=float(row["latency_ms"]),
                created_at=str(row["created_at"]),
                correctness=row.get("correctness"),
                feedback_note=row.get("feedback_note"),
            )
            for row in rows
        ]

    async def add_feedback(self, observation_id: str, correctness: str, note: str | None = None) -> None:
        await self._database.prepare(
            "UPDATE chat_observations SET correctness = ?, feedback_note = ? WHERE observation_id = ?"
        ).bind(correctness, note, observation_id).run()
