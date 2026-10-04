import asyncio
from types import SimpleNamespace

from application.use_cases.detect_intent import DetectIntent
from entities.chat import ConversationTurn, Intent, IntentDecision, MessageInput, ResponsePrompt, RetrievedChunk
from frameworks_and_drivers.cloudflare_ai import CloudflareLanguageModel, CloudflareVectorizeRetriever
from frameworks_and_drivers.cloudflare_context import set_worker_env, reset_worker_env


def test_followup_retrieval_receives_recent_context_and_current_question():
    class Resolver:
        async def resolve(self, message):
            self.value = message.value
            return IntentDecision(Intent.TECHNICAL, message.value)
    resolver = Resolver()
    asyncio.run(DetectIntent(resolver).execute(MessageInput('¿Y qué CMS usaste?'), [ConversationTurn('Contame sobre Grupo Eurosa', 'Sitio comercial')], 'Grupo Eurosa'))
    assert 'Grupo Eurosa' in resolver.value
    assert '¿Y qué CMS usaste?' in resolver.value


def test_simple_question_is_not_rewritten_without_context():
    class Resolver:
        async def resolve(self, message):
            assert message.value == 'What do you build?'
            return IntentDecision(Intent.GENERAL, message.value)
    asyncio.run(DetectIntent(Resolver()).execute(MessageInput('What do you build?')))


def test_followup_can_reference_a_project_named_only_by_the_assistant():
    class Resolver:
        async def resolve(self, message):
            assert 'Grupo Eurosa' in message.value
            assert 'What would you improve in it?' in message.value
            return IntentDecision(Intent.TECHNICAL, message.value)
    history = [ConversationTurn('What project uses WordPress?', 'I integrated WordPress for Grupo Eurosa.')]
    asyncio.run(DetectIntent(Resolver()).execute(MessageInput('What would you improve in it?'), history))


def test_retrieval_filters_low_scores_and_duplicate_chunks():
    class AI:
        async def run(self, *_):
            return {'data': [[0.1]]}
    class Vectorize:
        async def query(self, *_):
            return {'matches': [
                {'score': 0.2, 'metadata': {'source': 'unrelated.md', 'content': 'unrelated'}},
                {'score': 0.9, 'metadata': {'source': 'project.md', 'content': 'evidence', 'section': 'Stack'}},
                {'score': 0.9, 'metadata': {'source': 'project.md', 'content': 'evidence', 'section': 'Stack'}},
            ]}
    token = set_worker_env(SimpleNamespace(AI=AI(), VECTORIZE=Vectorize()))
    try:
        chunks = asyncio.run(CloudflareVectorizeRetriever().retrieve('stack'))
    finally:
        reset_worker_env(token)
    assert len(chunks) == 1
    assert chunks[0].section == 'Stack'


def test_english_abstention_and_unique_sources():
    model = CloudflareLanguageModel()
    empty = ResponsePrompt('system', 'question', Intent.GENERAL, locale='en')
    answer = asyncio.run(model.answer(empty))
    assert 'evidence' in answer.message.value
    class AI:
        async def run(self, *_):
            return {'response': 'Supported answer'}
    token = set_worker_env(SimpleNamespace(AI=AI()))
    try:
        answer = asyncio.run(model.answer(ResponsePrompt('system', 'question', Intent.GENERAL, context=(RetrievedChunk('same.md', 'A'), RetrievedChunk('same.md', 'B')))))
    finally:
        reset_worker_env(token)
    assert answer.sources == ('same.md',)
