from entities.chat import Intent, IntentDecision, MessageInput


class LocalIntentResolver:
    """Deterministic stand-in for an LLM intent classifier."""

    async def resolve(self, question: MessageInput) -> IntentDecision:
        message = question.value.lower()
        technical_terms = ("technical", "architecture", "code", "software", "rag", "ai", "stack", "técnic", "código")
        recruiter_terms = ("hire", "recruit", "career", "experience", "role", "work", "contrat", "carrera", "experiencia")
        if any(term in message for term in technical_terms):
            return IntentDecision(Intent.TECHNICAL, f"technical implementation architecture {question.value}", 4)
        if any(term in message for term in recruiter_terms):
            return IntentDecision(Intent.RECRUITER, f"professional experience career work style {question.value}", 4)
        return IntentDecision(Intent.GENERAL, question.value, 4)
