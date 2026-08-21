from application.ports import KnowledgeRetriever, PortfolioAssistant
from entities.chat import ChatAnswer, ChatQuestion


class LocalPortfolioAssistant(PortfolioAssistant):
    """Adapter offline seguro; luego se reemplaza por LangChain/LangGraph."""
    def __init__(self, retriever: KnowledgeRetriever) -> None:
        self._retriever = retriever

    async def answer(self, question: ChatQuestion) -> ChatAnswer:
        matches = await self._retriever.retrieve(question.message)
        if not matches:
            return ChatAnswer("Todavía estoy construyendo mi base de conocimiento. Podés preguntarme por mi trayectoria, proyectos o forma de trabajo.")
        excerpts = " ".join(content for _, content in matches[:2])
        return ChatAnswer(f"Según mi información disponible: {excerpts}", tuple(source for source, _ in matches))
