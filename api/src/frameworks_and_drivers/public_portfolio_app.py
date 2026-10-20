"""Minimal public API. No model, retriever, session or assistant SDK is initialized."""
from fastapi import FastAPI

app = FastAPI(title="Portfolio API", docs_url=None, redoc_url=None, openapi_url=None)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
