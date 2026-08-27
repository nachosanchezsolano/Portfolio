import json
import re
from typing import Any

from application.ports.model_ports import IntentResolver, LanguageModel
from application.ports.retrieval_ports import KnowledgeRetriever
from entities.chat import ChatAnswer, Intent, IntentDecision, MessageInput, MessageOutput, ResponsePrompt, RetrievedChunk
from frameworks_and_drivers.cloudflare_context import get_worker_env, to_python


INTENT_MODEL = "@cf/meta/llama-3.1-8b-instruct-fp8"
EMBEDDING_MODEL = "@cf/baai/bge-base-en-v1.5"
CHAT_MODEL = "@cf/meta/llama-3.1-8b-instruct-fp8"


async def run_ai(model: str, payload: dict[str, Any]) -> Any:
    env = get_worker_env()
    result = await env.AI.run(model, payload)
    return to_python(result)


class CloudflareIntentResolver(IntentResolver):
    async def resolve(self, message: MessageInput) -> IntentDecision:
        result = await run_ai(
            INTENT_MODEL,
            {
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Classify the portfolio question. Return JSON only with keys "
                            "intent and query. intent must be one of general, recruiter, technical. "
                            "query must be a short retrieval query."
                        ),
                    },
                    {"role": "user", "content": message.value},
                ],
                "temperature": 0,
                "max_tokens": 120,
            },
        )
        raw = str(result.get("response", "")) if isinstance(result, dict) else str(result)
        match = re.search(r"\{[\s\S]*\}", raw)
        if match:
            try:
                data = json.loads(match.group(0))
                intent = Intent(str(data.get("intent", "general")).lower())
                query = str(data.get("query") or message.value).strip()
                return IntentDecision(intent, query[:500], 4)
            except (ValueError, TypeError, json.JSONDecodeError):
                pass
        return IntentDecision(Intent.GENERAL, message.value, 4)


class CloudflareVectorizeRetriever(KnowledgeRetriever):
    async def retrieve(self, query: str, limit: int = 4) -> list[RetrievedChunk]:
        embedding_result = await run_ai(EMBEDDING_MODEL, {"text": [query]})
        vector = embedding_result["data"][0] if isinstance(embedding_result, dict) else embedding_result.data[0]
        matches = await get_worker_env().VECTORIZE.query(
            vector,
            {"topK": min(limit, 20), "returnMetadata": "all"},
        )
        matches = to_python(matches)
        chunks: list[RetrievedChunk] = []
        for match in (matches.get("matches", []) if isinstance(matches, dict) else []):
            metadata = match.get("metadata", {})
            content = metadata.get("content") or metadata.get("text")
            source = metadata.get("source") or match.get("id")
            if content and source:
                chunks.append(RetrievedChunk(str(source), str(content)))
        return chunks


class CloudflareLanguageModel(LanguageModel):
    async def answer(
        self,
        prompt: ResponsePrompt,
    ) -> ChatAnswer:
        if not prompt.context:
            return ChatAnswer(
                MessageOutput("Todavía no tengo evidencia suficiente para responder esa pregunta."),
                intent=prompt.intent,
            )
        result = await run_ai(
            CHAT_MODEL,
            {
                "messages": [
                    {"role": "system", "content": prompt.system},
                    {"role": "user", "content": prompt.user},
                ],
                "temperature": 0.2,
                "max_tokens": 700,
            },
        )
        text = str(result.get("response", "")) if isinstance(result, dict) else str(result)
        text = " ".join(text.split()[:500])
        return ChatAnswer(
            MessageOutput(text),
            tuple(chunk.source for chunk in prompt.context),
            prompt.intent,
        )
