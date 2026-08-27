"""Generate Workers AI embeddings and upsert public vault documents into Vectorize."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT / "vault"
EMBEDDING_MODEL = "@cf/baai/bge-base-en-v1.5"


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


def embed_documents(account_id: str, token: str, documents: list[tuple[str, str]]) -> list[list[float]]:
    result = api_json(
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{EMBEDDING_MODEL}",
        token,
        {"text": [content for _, content in documents]},
    )
    vectors = result.get("data")
    if not isinstance(vectors, list) or len(vectors) != len(documents):
        raise RuntimeError(f"Embedding response count mismatch: expected {len(documents)}, got {vectors}")
    return vectors


def upsert(account_id: str, token: str, index: str, documents: list[tuple[str, str]], vectors: list[list[float]]) -> None:
    records = []
    for (source, content), vector in zip(documents, vectors, strict=True):
        records.append(
            {
                "id": hashlib.sha256(source.encode("utf-8")).hexdigest()[:32],
                "values": vector,
                "metadata": {"source": source, "content": content},
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
    documents = public_documents()
    vectors = embed_documents(account_id, token, documents)
    upsert(account_id, token, args.index, documents, vectors)
    print(f"Upserted {len(documents)} public documents into {args.index}")


if __name__ == "__main__":
    main()
