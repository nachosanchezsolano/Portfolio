import asyncio

from entities.chat import Intent, IntentDecision, MessageInput
from frameworks_and_drivers.cloudflare_ai import (
    CloudflareIntentResolver,
    CloudflareLanguageModel,
    CloudflareVectorizeRetriever,
)
from frameworks_and_drivers.cloudflare_context import reset_worker_env, set_worker_env


class FakeAI:
    def __init__(self, responses: list[dict]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, dict]] = []

    async def run(self, model: str, payload: dict) -> dict:
        self.calls.append((model, payload))
        return self.responses.pop(0)


class FakeVectorize:
    def __init__(self) -> None:
        self.calls: list[tuple[list[float], dict]] = []

    async def query(self, vector, options) -> dict:
        self.calls.append((vector, options))
        return {
            "matches": [
                {
                    "id": "chunk-1",
                    "metadata": {
                        "source": "profile/now.md",
                        "content": "Portfolio evidence",
                    },
                }
            ]
        }


class FakeEnv:
    def __init__(self, responses: list[dict]) -> None:
        self.AI = FakeAI(responses)
        self.VECTORIZE = FakeVectorize()


def test_cloudflare_intent_adapter_parses_structured_model_output() -> None:
    env = FakeEnv([{"response": '{"intent":"technical","query":"software architecture"}'}])
    token = set_worker_env(env)
    try:
        decision = asyncio.run(
            CloudflareIntentResolver().resolve(MessageInput("¿Qué arquitectura usás?"))
        )
    finally:
        reset_worker_env(token)

    assert decision.intent is Intent.TECHNICAL
    assert decision.retrieval_query == "software architecture"
    assert env.AI.calls[0][0].startswith("@cf/")


def test_cloudflare_intent_adapter_falls_back_safely_on_invalid_model_output() -> None:
    env = FakeEnv([{"response": "not valid json"}])
    token = set_worker_env(env)
    try:
        decision = asyncio.run(
            CloudflareIntentResolver().resolve(MessageInput("question"))
        )
    finally:
        reset_worker_env(token)

    assert decision.intent is Intent.GENERAL
    assert decision.retrieval_query == "question"


def test_cloudflare_retriever_embeds_query_and_reads_vector_metadata() -> None:
    env = FakeEnv([{"data": [[0.1, 0.2, 0.3]]}])
    token = set_worker_env(env)
    try:
        chunks = asyncio.run(CloudflareVectorizeRetriever().retrieve("architecture", 4))
    finally:
        reset_worker_env(token)

    assert chunks[0].source == "profile/now.md"
    assert chunks[0].content == "Portfolio evidence"
    assert env.VECTORIZE.calls == [([0.1, 0.2, 0.3], {"topK": 4, "returnMetadata": "all"})]


def test_cloudflare_language_model_is_grounded_and_returns_sources() -> None:
    env = FakeEnv([{"response": "Grounded response"}])
    token = set_worker_env(env)
    try:
        answer = asyncio.run(
            CloudflareLanguageModel().answer(
                MessageInput("What do you build?"),
                IntentDecision(Intent.GENERAL, "portfolio", 1),
                [
                    type(
                        "Chunk",
                        (),
                        {"source": "profile/now.md", "content": "Evidence"},
                    )()
                ],
            )
        )
    finally:
        reset_worker_env(token)

    assert answer.message.value == "Grounded response"
    assert answer.sources == ("profile/now.md",)
    assert "Evidence" in env.AI.calls[0][1]["messages"][0]["content"]


def test_cloudflare_language_model_returns_safe_fallback_without_context() -> None:
    env = FakeEnv([])
    token = set_worker_env(env)
    try:
        answer = asyncio.run(
            CloudflareLanguageModel().answer(
                MessageInput("What do you build?"),
                IntentDecision(Intent.GENERAL, "portfolio", 1),
                [],
            )
        )
    finally:
        reset_worker_env(token)

    assert answer.sources == ()
    assert "evidencia suficiente" in answer.message.value
    assert env.AI.calls == []
