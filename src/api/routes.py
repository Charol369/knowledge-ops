"""API 路由层。

主入口语义已从“普通 RAG 问答”升级为“研究型 Agent 请求入口”。
即使当前仍是骨架，也要把最终的数据流设计清楚：
question -> policy -> graph -> artifacts -> response / stream
"""
from fastapi import APIRouter, HTTPException

from src.api.schemas import QueryRequest, QueryResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    """主入口：用户问题 -> policy layer -> agent graph -> 结构化研究结果。"""
    # TODO Sprint 1: 支持最小 CLI / API research pipeline
    # TODO Sprint 3: 接到 src.agents.graph.build_graph().invoke(...)
    # TODO Sprint 4: 接入 complexity classifier / model router / langfuse / injection 检测
    # TODO Sprint 5: 切 SSE 流式响应，返回 plan / progress / evidence / final report
    raise HTTPException(status_code=501, detail="Not implemented yet (Sprint 1-5)")


@router.post("/ingest")
async def ingest():
    """批量入库接口（admin 用）。"""
    # TODO Sprint 1: 接到 src.ingest pipeline
    # TODO Sprint 4: 加鉴权 / 限流 / 审计日志
    raise HTTPException(status_code=501, detail="Not implemented yet (Sprint 1)")
