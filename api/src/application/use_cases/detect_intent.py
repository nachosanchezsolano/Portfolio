from application.ports.model_ports import IntentResolver
from entities.chat import ConversationTurn, IntentDecision, MessageInput


class DetectIntent:
    def __init__(self, resolver: IntentResolver) -> None:
        self._resolver = resolver

    async def execute(self, message: MessageInput, conversation: list[ConversationTurn] | None = None, page_context: str | None = None) -> IntentDecision:
        # Prior questions resolve references; the current question controls topic changes.
        context = []
        if page_context:
            context.append(f"Page: {page_context[:200]}")
        for turn in reversed((conversation or [])[-2:]):
            context.append(f"Previous question: {turn.user[:400]}")
            context.append(f"Previous answer (reference only): {turn.assistant[:600]}")
        remaining = 480 - len(message.value.split())
        if not context or remaining <= 0:
            return await self._resolver.resolve(message)
        history = ' '.join(' '.join(context).split()[:min(remaining, 160)])
        contextual = MessageInput(f"Context (only for references): {history}\nCurrent question: {message.value}")
        return await self._resolver.resolve(contextual)
