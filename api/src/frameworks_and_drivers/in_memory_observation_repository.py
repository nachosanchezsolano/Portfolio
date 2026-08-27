from entities.chat import ChatObservation


class InMemoryObservationRepository:
    """Local/test repository; production uses Cloudflare D1."""

    def __init__(self) -> None:
        self._observations: dict[str, ChatObservation] = {}

    async def save(self, observation: ChatObservation) -> None:
        self._observations[observation.observation_id] = observation

    async def list_recent(self, limit: int = 100) -> list[ChatObservation]:
        return list(self._observations.values())[-max(1, min(limit, 500)) :][::-1]

    async def add_feedback(self, observation_id: str, correctness: str, note: str | None = None) -> None:
        observation = self._observations.get(observation_id)
        if observation is None:
            return
        self._observations[observation_id] = ChatObservation(
            **{**observation.__dict__, "correctness": correctness, "feedback_note": note}
        )
