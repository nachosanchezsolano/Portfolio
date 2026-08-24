from application.ports.retrieval_ports import KnowledgeRetriever
from entities.chat import IntentDecision, RetrievedChunk


class RagQuery:
    def __init__(self, retriever: KnowledgeRetriever) -> None:
        self._retriever = retriever

    async def execute(self, decision: IntentDecision) -> list[RetrievedChunk]:
        return await self._retriever.retrieve(decision.retrieval_query, decision.retrieval_limit)
