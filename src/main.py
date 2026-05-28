"""FastAPI 入口。

KnowledgeOps 的服务定位是：生产导向研究型 Knowledge Agent API。
启动方式：uv run uvicorn src.main:app --reload
"""
from collections import defaultdict, deque
from collections.abc import Callable
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.routes import router as api_router
from src.config import settings


class InMemoryRateLimiter:
    """Small fixed-window limiter for local Sprint 4 acceptance."""

    def __init__(
        self,
        limit: int,
        window_seconds: int,
        clock: Callable[[], float] | None = None,
    ) -> None:
        if limit <= 0:
            raise ValueError("limit must be positive.")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive.")
        self.limit = limit
        self.window_seconds = window_seconds
        self.clock = clock or time.time
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = self.clock()
        window_start = now - self.window_seconds
        entries = self._requests[key]
        while entries and entries[0] <= window_start:
            entries.popleft()
        if len(entries) >= self.limit:
            return False
        entries.append(now)
        return True

app = FastAPI(
    title="KnowledgeOps",
    description="Production-oriented research agent for enterprise knowledge work",
    version="0.0.1",
)

app.state.api_auth_enabled = settings.api_auth_enabled
app.state.api_key = settings.api_key
app.state.rate_limit_enabled = settings.rate_limit_enabled
app.state.rate_limiter = InMemoryRateLimiter(
    limit=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window_seconds,
)


def _is_protected_path(path: str) -> bool:
    return path == "/api/v1/query"


@app.middleware("http")
async def sprint4_protection_middleware(request: Request, call_next):
    if not _is_protected_path(request.url.path):
        return await call_next(request)

    api_key = request.headers.get("X-API-Key", "")
    if getattr(request.app.state, "api_auth_enabled", False):
        expected_key = getattr(request.app.state, "api_key", "")
        if not expected_key or api_key != expected_key:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing API key."},
            )

    if getattr(request.app.state, "rate_limit_enabled", False):
        limiter = getattr(request.app.state, "rate_limiter", None)
        if limiter is None:
            limiter = InMemoryRateLimiter(
                limit=settings.rate_limit_requests,
                window_seconds=settings.rate_limit_window_seconds,
            )
            request.app.state.rate_limiter = limiter
        identity = api_key or request.client.host if request.client else "anonymous"
        if not limiter.allow(identity):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded."},
            )

    return await call_next(request)


app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.0.1"}


# TODO Sprint 1: 接入最小 research pipeline
# TODO Sprint 2: 接入 context builder + hybrid retrieval
# TODO Sprint 3: 接入混合范式 agent graph + artifact store
