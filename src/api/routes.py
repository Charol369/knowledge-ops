"""API 路由层

W1 末骨架：声明路由 + 接到 Agent graph。Sprint 1+ 逐步填充。
"""
from fastapi import APIRouter, HTTPException
from src.api.schemas import QueryRequest, QueryResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    """主入口：用户问题 → Agent graph → 结构化答案"""
    # TODO Sprint 3: 接到 src.agents.graph.build_graph().invoke({"question": req.question})
    # TODO Sprint 4: 加 Langfuse callback + injection 检测
    # TODO Sprint 5: 切 SSE 流式响应（StreamingResponse）
    raise HTTPException(status_code=501, detail="Not implemented yet (Sprint 3)")


@router.post("/ingest")
async def ingest():
    """批量入库接口（admin 用）"""
    # TODO Sprint 1: 接到 src.ingest pipeline + 鉴权
    raise HTTPException(status_code=501, detail="Not implemented yet (Sprint 1)")
