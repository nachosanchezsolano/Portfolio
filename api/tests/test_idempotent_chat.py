import asyncio

from frameworks_and_drivers.fastapi_app import build_local_controller
from interface_adapters.schemas import ChatInput


def test_lost_response_retry_returns_same_answer_and_consumes_one_turn():
    async def scenario():
        controller = build_local_controller()
        request = ChatInput(message='What do you build?', session_id='session-lost', request_id='logical-question-1')
        completed = await controller.ask(request)  # Server completes; caller loses this response.
        recovered = await controller.ask(request)
        assert completed.observation_id == recovered.observation_id
        session = await controller._flow._sessions.get_or_create('session-lost')
        assert len(session.messages) == 1
        assert len(session.turns) == 1
    asyncio.run(scenario())


def test_d1_request_cache_and_claim_are_shared_between_worker_instances():
    import sqlite3
    from pathlib import Path
    from entities.chat import ChatAnswer, Intent, MessageOutput
    from frameworks_and_drivers.chat_request_repository import CloudflareD1ChatRequestRepository
    connection = sqlite3.connect(':memory:')
    connection.row_factory = sqlite3.Row
    migration = Path(__file__).parents[1] / 'migrations/0004_chat_requests.sql'
    connection.executescript(migration.read_text())
    class Statement:
        def __init__(self, sql):
            self.sql, self.values = sql, ()
        def bind(self, *values):
            self.values = values
            return self
        async def first(self):
            row = connection.execute(self.sql, self.values).fetchone()
            return dict(row) if row else None
        async def run(self):
            cursor = connection.execute(self.sql, self.values)
            connection.commit()
            return {'meta': {'changes': cursor.rowcount}}
    class Database:
        def prepare(self, sql):
            return Statement(sql)
    async def scenario():
        first, retry = CloudflareD1ChatRequestRepository(Database()), CloudflareD1ChatRequestRepository(Database())
        assert await first.claim('key', 'fingerprint')
        assert not await retry.claim('key', 'fingerprint')
        answer = ChatAnswer(MessageOutput('Supported answer'), ('project.md',), Intent.TECHNICAL, 'session', 'observation')
        await first.complete('key', 'fingerprint', answer)
        assert (await retry.get('key')) == ('fingerprint', answer)
        await retry.release('key', 'fingerprint')
        assert (await first.get('key'))[1] == answer
    asyncio.run(scenario())
    connection.close()


def test_idempotency_rejects_reusing_a_key_for_another_question():
    from entities.chat import DomainValidationError
    import pytest
    async def scenario():
        controller = build_local_controller()
        await controller.ask(ChatInput(message='What do you build?', session_id='session', request_id='same-key'))
        with pytest.raises(DomainValidationError, match='different question'):
            await controller.ask(ChatInput(message='What experience do you have?', session_id='session', request_id='same-key'))
    asyncio.run(scenario())


def test_replay_at_session_limit_is_returned_without_an_extra_turn():
    async def scenario():
        controller = build_local_controller()
        for index in range(5):
            await controller.ask(ChatInput(message='What do you build?', session_id='full-session', request_id=f'question-{index}'))
        replay = await controller.ask(ChatInput(message='What do you build?', session_id='full-session', request_id='question-0'))
        assert replay.message
        assert len((await controller._flow._sessions.get_or_create('full-session')).messages) == 5
    asyncio.run(scenario())
