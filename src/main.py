"""FastAPI 入口

启动方式：
  uv run uvicorn src.main:app --reload

W1 末骨架版：只挂 /health 和 /api/v1 路由，主业务由 Sprint 1+ 填充。
"""
from fastapi import FastAPI
from src.api.routes import router as api_router

app = FastAPI(
    title="KnowledgeOps",
    description="Enterprise RAG + Multi-Agent Knowledge Base Platform",
    version="0.0.1",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.0.1"}


# TODO Sprint 1: 接入 Ingest pipeline
# TODO Sprint 2: 接入 Hybrid retrieval
# TODO Sprint 3: 接入 Multi-Agent graph
# TODO Sprint 4: 加 Langfuse middleware + Guardrails middleware
# TODO Sprint 5: 加 SSE 流式响应 + Rate limit
