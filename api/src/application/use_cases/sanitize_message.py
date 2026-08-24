from application.ports.security_ports import SemanticSanitizer
from entities.chat import MessageInput


class SanitizeMessage:
    def __init__(self, sanitizer: SemanticSanitizer) -> None:
        self._sanitizer = sanitizer

    async def execute(self, message: MessageInput) -> MessageInput:
        return await self._sanitizer.sanitize(message)
