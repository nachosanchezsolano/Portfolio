import asyncio
from application.ask_portfolio import AskPortfolio
from entities.chat import ChatQuestion
from frameworks_and_drivers.local_assistant import LocalPortfolioAssistant
from frameworks_and_drivers.memory_retriever import MemoryRetriever


def test_local_assistant_answers_from_memory() -> None:
    answer = asyncio.run(AskPortfolio(LocalPortfolioAssistant(MemoryRetriever()), 1200).execute(ChatQuestion("¿Qué principios te interesan?")))
    assert "soluciones" in answer.message


def test_empty_question_is_rejected() -> None:
    try:
        asyncio.run(AskPortfolio(LocalPortfolioAssistant(MemoryRetriever()), 1200).execute(ChatQuestion("   ")))
    except ValueError as error:
        assert "empty" in str(error)
    else:
        raise AssertionError("empty question should fail")
