"""Idempotency for logical chat questions, including retries across Worker instances."""
import json
from time import time
from typing import Any

from entities.chat import ChatAnswer, Intent, MessageOutput
from frameworks_and_drivers.cloudflare_context import to_python

LEASE_SECONDS = 120


class InMemoryChatRequestRepository:
    def __init__(self):
        self._records: dict[str, tuple[str, ChatAnswer | None, float]] = {}

    async def get(self, key):
        record = self._records.get(key)
        return (record[0], record[1]) if record else None

    async def claim(self, key, fingerprint):
        record = self._records.get(key)
        if record and (record[1] is not None or record[2] > time() or record[0] != fingerprint):
            return False
        self._records[key] = (fingerprint, None, time() + LEASE_SECONDS)
        return True

    async def complete(self, key, fingerprint, answer):
        self._records[key] = (fingerprint, answer, time() + LEASE_SECONDS)

    async def release(self, key, fingerprint):
        record = self._records.get(key)
        if record and record[0] == fingerprint and record[1] is None:
            del self._records[key]


class CloudflareD1ChatRequestRepository:
    def __init__(self, database: Any):
        self._database = database

    async def get(self, key):
        row = to_python(await self._database.prepare('SELECT fingerprint, answer FROM chat_requests WHERE request_key = ?').bind(key).first())
        if not row:
            return None
        data = json.loads(row['answer']) if row.get('answer') else None
        answer = ChatAnswer(MessageOutput(data['message']), tuple(data['sources']), Intent(data['intent']), data['session_id'], data['observation_id']) if data else None
        return str(row['fingerprint']), answer

    async def claim(self, key, fingerprint):
        now = int(time())
        result = to_python(await self._database.prepare('''INSERT INTO chat_requests
            (request_key, fingerprint, expires_at) VALUES (?, ?, ?)
            ON CONFLICT(request_key) DO UPDATE SET expires_at = excluded.expires_at
            WHERE chat_requests.answer IS NULL AND chat_requests.fingerprint = excluded.fingerprint
              AND chat_requests.expires_at <= ?''').bind(key, fingerprint, now + LEASE_SECONDS, now).run())
        return result.get('meta', {}).get('changes', 0) == 1

    async def complete(self, key, fingerprint, answer):
        data = json.dumps({'message': answer.message.value, 'sources': answer.sources, 'intent': answer.intent.value,
                           'session_id': answer.session_id, 'observation_id': answer.observation_id}, ensure_ascii=False)
        await self._database.prepare('UPDATE chat_requests SET answer = ? WHERE request_key = ? AND fingerprint = ?').bind(data, key, fingerprint).run()

    async def release(self, key, fingerprint):
        await self._database.prepare('DELETE FROM chat_requests WHERE request_key = ? AND fingerprint = ? AND answer IS NULL').bind(key, fingerprint).run()
