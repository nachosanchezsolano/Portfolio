from application.ports.model_ports import LanguageModel
from entities.chat import ChatAnswer, Intent, IntentDecision, MessageInput, MessageOutput, RetrievedChunk


class LocalLanguageModel(LanguageModel):
    """Grounded local generator used until a hosted model adapter is configured."""

    async def answer(self, question: MessageInput, decision: IntentDecision, context: list[RetrievedChunk]) -> ChatAnswer:
        if not context:
            return ChatAnswer(MessageOutput("Todavía no tengo evidencia suficiente para responder esa pregunta. Podés preguntarme por mi trayectoria, proyectos o forma de trabajo."), intent=decision.intent)
        excerpts = " ".join(chunk.content for chunk in context[:2])
        prefix = {
            Intent.GENERAL: "Según la información pública disponible",
            Intent.RECRUITER: "Desde una perspectiva profesional",
            Intent.TECHNICAL: "Desde una perspectiva técnica",
        }[decision.intent]
        return ChatAnswer(MessageOutput(f"{prefix}: {excerpts}"), tuple(chunk.source for chunk in context), decision.intent)
