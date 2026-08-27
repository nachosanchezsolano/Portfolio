import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).parents[2] / "knowledge-base" / "scripts" / "upsert_vectorize.py"
spec = importlib.util.spec_from_file_location("upsert_vectorize", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
chunk_documents = module.chunk_documents
vector_id = module.vector_id


def test_chunk_documents_keeps_headings_as_section_context() -> None:
    chunks = chunk_documents(
        [("projects/example.md", "# Project\n\nFirst paragraph.\n\n## Decisions\n\nUsed Astro.")],
        max_chars=100,
        overlap_chars=10,
    )

    assert [chunk.section for chunk in chunks] == ["Project", "Decisions"]
    assert chunks[1].content == "Used Astro."


def test_chunk_documents_splits_large_content_deterministically() -> None:
    chunks = chunk_documents(
        [("profile/now.md", "A" * 25)], max_chars=10, overlap_chars=2
    )

    assert [len(chunk.content) for chunk in chunks] == [10, 10, 9]
    assert [chunk.index for chunk in chunks] == [0, 1, 2]


def test_vector_id_reuses_legacy_id_for_first_chunk() -> None:
    chunks = chunk_documents([("profile/now.md", "A" * 25)], max_chars=10, overlap_chars=2)

    assert vector_id(chunks[0]) == module.hashlib.sha256(b"profile/now.md").hexdigest()[:32]
    assert vector_id(chunks[1]) != vector_id(chunks[0])
