"""Build a deterministic local index from public Markdown notes."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT / "vault"
OUTPUT = ROOT / ".generated" / "index.json"


def build_index() -> None:
    documents = []
    for path in sorted(VAULT.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        documents.append({"id": hashlib.sha256(str(path.relative_to(VAULT)).encode()).hexdigest()[:16], "path": str(path.relative_to(VAULT)).replace("\\", "/"), "content": content})
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"version": 1, "documents": documents}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Indexed {len(documents)} public documents -> {OUTPUT}")


if __name__ == "__main__":
    build_index()
