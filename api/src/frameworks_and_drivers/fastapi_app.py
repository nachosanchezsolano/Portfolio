from collections import defaultdict
from time import monotonic
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from application.ask_portfolio import AskPortfolio
from frameworks_and_drivers.local_assistant import LocalPortfolioAssistant
from frameworks_and_drivers.memory_retriever import MemoryRetriever
from frameworks_and_drivers.settings import get_settings
from interface_adapters.controllers import ChatController
from interface_adapters.schemas import AskRequest, AskResponse

settings = get_settings()
controller = ChatController(AskPortfolio(LocalPortfolioAssistant(MemoryRetriever()), settings.max_message_length))
app = FastAPI(title="Portfolio Assistant API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_methods=["POST", "GET"], allow_headers=["*"])
requests_by_client: dict[str, list[float]] = defaultdict(list)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


async def protect(request: Request, x_api_key: str | None = Header(default=None)) -> None:
    now = monotonic()
    client = request.client.host if request.client else "unknown"
    recent = [stamp for stamp in requests_by_client[client] if now - stamp < settings.rate_limit_window_seconds]
    if len(recent) >= settings.rate_limit_requests:
        raise HTTPException(status_code=429, detail="rate limit exceeded")
    recent.append(now)
    requests_by_client[client] = recent
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="invalid api key")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/chat", response_model=AskResponse, dependencies=[Depends(protect)])
async def chat(request: AskRequest) -> AskResponse:
    try:
        return await controller.ask(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
