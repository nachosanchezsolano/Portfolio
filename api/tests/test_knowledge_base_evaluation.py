import json
from pathlib import Path


ROOT = Path(__file__).parents[2]
QUESTIONS = ROOT / "knowledge-base" / "evaluation" / "questions.json"
VAULT = ROOT / "knowledge-base" / "vault"


def test_rag_evaluation_dataset_is_grounded_in_public_sources() -> None:
    questions = json.loads(QUESTIONS.read_text(encoding="utf-8"))

    assert len(questions) >= 5
    assert len({item["id"] for item in questions}) == len(questions)
    for item in questions:
        assert item["question"]
        assert item["expected"]
        assert item["relevant_sources"]
        for source in item["relevant_sources"]:
            assert (VAULT / source).exists()
