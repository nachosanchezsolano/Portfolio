from application.ports.model_ports import IntentResolver
from entities.chat import IntentDecision, MessageInput


class DetectIntent:
    def __init__(self, resolver: IntentResolver) -> None:
        self._resolver = resolver

    async def execute(self, message: MessageInput) -> IntentDecision:
        return await self._resolver.resolve(message)
