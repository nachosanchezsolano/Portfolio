from application.ports.retrieval_ports import KnowledgeRetriever
from entities.chat import RetrievedChunk


class MemoryRetriever(KnowledgeRetriever):
    """Temporary RAG adapter; the contract will later be backed by PostgreSQL."""

    def __init__(self) -> None:
        self._documents = [
            RetrievedChunk("profile/now.md", "Estoy construyendo un portfolio conversacional con foco en software y aprendizaje continuo."),
            RetrievedChunk("profile/principles.md", "Me interesa crear soluciones simples, seguras y fáciles de evolucionar."),
        ]

    async def retrieve(self, query: str, limit: int = 4) -> list[RetrievedChunk]:
        terms = {term.lower() for term in query.split() if len(term) > 2}
        ranked = sorted(self._documents, key=lambda item: sum(term in f"{item.source} {item.content}".lower() for term in terms), reverse=True)
        matches = [item for item in ranked if not terms or any(term in f"{item.source} {item.content}".lower() for term in terms)]
        return (matches or ranked)[:limit]
