import re

from entities.chat import DomainValidationError, MessageInput


class LocalSemanticSanitizer:
    """Deterministic safety boundary until an AI guardrail is configured."""

    _blocked_patterns = (
        r"```",
        r"<\s*script",
        r"\b(?:select|insert|update|delete|drop|alter|create)\b[\s\S]{0,80}\b(?:from|table|database|where|into)\b",
        r"\b(?:union\s+select|exec(?:ute)?|xp_cmdshell|information_schema)\b",
        r"\b(?:import\s+os|subprocess|eval\s*\(|__import__\s*\()",
        r"(?:--|/\*|\*/|;\s*(?:select|insert|update|delete|drop|alter|create))",
        r"\b(?:ignore|disregard|forget)\s+(?:all\s+)?(?:the\s+)?(?:previous|prior|system|developer)\s+(?:instructions|messages)",
        r"\b(?:reveal|show|print)\s+(?:the\s+)?(?:system|developer)\s+(?:prompt|instructions|message)",
        r"\b(?:jailbreak|dan|developer\s+mode)\b",
    )

    async def sanitize(self, message: MessageInput) -> MessageInput:
        value = message.value
        if any(re.search(pattern, value, re.IGNORECASE) for pattern in self._blocked_patterns):
            raise DomainValidationError("message contains an unsupported or unsafe instruction")
        return MessageInput(" ".join(value.split()))
