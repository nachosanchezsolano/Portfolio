"""Generate Workers AI embeddings and upsert public vault documents into Vectorize."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT / "vault"
EMBEDDING_MODEL = "@cf/baai/bge-base-en-v1.5"
MAX_CHUNK_CHARS = 1800
CHUNK_OVERLAP_CHARS = 240


@dataclass(frozen=True)
class KnowledgeChunk:
    source: str
    content: str
    section: str
    index: int


def public_documents() -> list[tuple[str, str]]:
    documents = []
    for path in sorted(VAULT.rglob("*.md")):
        raw = path.read_text(encoding="utf-8")
        frontmatter = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw, re.DOTALL)
        if not frontmatter or not re.search(r"(?m)^visibility:\s*public\s*$", frontmatter.group(1)):
            continue
        source = path.relative_to(VAULT).as_posix()
        content = frontmatter.group(2).strip()
        documents.append((source, content))
    return documents


def chunk_documents(
    documents: list[tuple[str, str]],
    max_chars: int = MAX_CHUNK_CHARS,
    overlap_chars: int = CHUNK_OVERLAP_CHARS,
) -> list[KnowledgeChunk]:
    """Split public notes at headings/paragraphs while retaining section context."""

    if max_chars <= 0 or overlap_chars < 0 or overlap_chars >= max_chars:
        raise ValueError("chunk size must be positive and overlap must be smaller")

    chunks: list[KnowledgeChunk] = []
    for source, document in documents:
        section = "Documento"
        buffer = ""
        chunk_index = 0

        def flush() -> None:
            nonlocal buffer, chunk_index
            content = buffer.strip()
            if content:
                chunks.append(KnowledgeChunk(source, content, section, chunk_index))
                chunk_index += 1
            buffer = ""

        for raw_line in document.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("#"):
                if buffer:
                    flush()
                section = line.lstrip("# ").strip() or section
                continue

            candidate = f"{buffer}\n{line}".strip() if buffer else line
            if len(candidate) <= max_chars:
                buffer = candidate
                continue

            flush()
            if len(line) > max_chars:
                starts = range(0, max(1, len(line) - overlap_chars), max_chars - overlap_chars)
                for start in starts:
                    piece = line[start : start + max_chars].strip()
                    if piece:
                        chunks.append(KnowledgeChunk(source, piece, section, chunk_index))
                        chunk_index += 1
                buffer = ""
            else:
                buffer = line[:overlap_chars].strip()

        flush()
    return chunks


def vector_id(chunk: KnowledgeChunk) -> str:
    """Keep legacy document IDs for the first chunk to avoid stale vectors."""

    suffix = "" if chunk.index == 0 else f":{chunk.index}"
    return hashlib.sha256(f"{chunk.source}{suffix}".encode("utf-8")).hexdigest()[:32]


def api_json(url: str, token: str, payload: dict, *, content_type: str = "application/json") -> dict:
    request = Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": content_type},
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Cloudflare API request failed ({error.code}): {detail}") from error
    if not result.get("success", False):
        raise RuntimeError(f"Cloudflare API request failed: {result}")
    return result["result"]


def embed_documents(account_id: str, token: str, documents: list[KnowledgeChunk]) -> list[list[float]]:
    result = api_json(
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{EMBEDDING_MODEL}",
        token,
        {"text": [chunk.content for chunk in documents]},
    )
    vectors = result.get("data")
    if not isinstance(vectors, list) or len(vectors) != len(documents):
        raise RuntimeError(f"Embedding response count mismatch: expected {len(documents)}, got {vectors}")
    return vectors


def upsert(account_id: str, token: str, index: str, documents: list[KnowledgeChunk], vectors: list[list[float]]) -> None:
    records = []
    for chunk, vector in zip(documents, vectors, strict=True):
        records.append(
            {
                "id": vector_id(chunk),
                "values": vector,
                "metadata": {
                    "source": chunk.source,
                    "content": chunk.content,
                    "section": chunk.section,
                    "chunk_index": chunk.index,
                },
            }
        )
    boundary = f"----portfolio-{uuid.uuid4().hex}"
    ndjson = "\n".join(json.dumps(record, ensure_ascii=False) for record in records).encode("utf-8")
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="vectors"; filename="vectors.ndjson"\r\n'
        "Content-Type: application/x-ndjson\r\n\r\n"
    ).encode("utf-8") + ndjson + f"\r\n--{boundary}--\r\n".encode("utf-8")
    request = Request(
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}/vectorize/v2/indexes/{index}/upsert",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Cloudflare API request failed ({error.code}): {detail}") from error
    if not result.get("success", False):
        raise RuntimeError(f"Cloudflare API request failed: {result}")
    print(f"mutation_id={result.get('result', {}).get('mutationId', 'unknown')}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default="portfolio-knowledge")
    args = parser.parse_args()
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    if not token or not account_id:
        raise SystemExit("Set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID")
    documents = chunk_documents(public_documents())
    vectors = embed_documents(account_id, token, documents)
    upsert(account_id, token, args.index, documents, vectors)
    print(f"Upserted {len(documents)} public chunks into {args.index}")


if __name__ == "__main__":
    main()
