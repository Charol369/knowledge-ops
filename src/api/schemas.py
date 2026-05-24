"""API 请求/响应 Pydantic 模型"""
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    intent: str | None = Field(default=None, description="可选：qa/summary/report，不传则 supervisor 自动判断")
    thread_id: str | None = Field(default=None, description="可选：会话 ID 用于多轮记忆")


class Citation(BaseModel):
    source: str
    page: int | None = None
    snippet: str | None = None


class QueryResponse(BaseModel):
    answer: str
    confidence: float
    citations: list[Citation] = []
    trace_id: str | None = None  # Langfuse trace id，便于前端展示"看追踪"按钮
