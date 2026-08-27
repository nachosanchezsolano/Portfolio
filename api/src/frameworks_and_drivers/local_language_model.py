from application.ports.model_ports import LanguageModel
from entities.chat import ChatAnswer, Intent, MessageOutput, ResponsePrompt


class LocalLanguageModel(LanguageModel):
    """Grounded local generator used until a hosted model adapter is configured."""

    async def answer(self, prompt: ResponsePrompt) -> ChatAnswer:
        if not prompt.context:
            return ChatAnswer(MessageOutput("Todavía no tengo evidencia suficiente para responder esa pregunta. Podés preguntarme por mi trayectoria, proyectos o forma de trabajo."), intent=prompt.intent)
        excerpts = " ".join(chunk.content for chunk in prompt.context[:2])
        prefix = {
            Intent.GENERAL: "Según la información pública disponible",
            Intent.RECRUITER: "Desde una perspectiva profesional",
            Intent.TECHNICAL: "Desde una perspectiva técnica",
        }[prompt.intent]
        return ChatAnswer(MessageOutput(f"{prefix}: {excerpts}"), tuple(chunk.source for chunk in prompt.context), prompt.intent)
