"""FastAPI 入口。

KnowledgeOps 的服务定位是：生产导向研究型 Knowledge Agent API。
启动方式：uv run uvicorn src.main:app --reload
"""
from fastapi import FastAPI

from src.api.routes import router as api_router

app = FastAPI(
    title="KnowledgeOps",
    description="Production-oriented research agent for enterprise knowledge work",
    version="0.0.1",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.0.1"}


# TODO Sprint 1: 接入最小 research pipeline
# TODO Sprint 2: 接入 context builder + hybrid retrieval
# TODO Sprint 3: 接入混合范式 agent graph + artifact store
# TODO Sprint 4: 加 policy layer + langfuse middleware + guardrails middleware
# TODO Sprint 5: 加 SSE 流式响应 + rate limit + auth
