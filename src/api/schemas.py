"""API 请求/响应 Pydantic 模型。"""
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    intent: str | None = Field(default=None, description="可选：lookup/research/report，不传则由 policy layer 判定")
    thread_id: str | None = Field(default=None, description="可选：会话 ID，用于隔离 graph checkpointer 与 artifact session")


class ResearchStep(BaseModel):
    step_id: str
    description: str
    status: str = Field(default="pending", description="pending/running/completed/failed")


class Citation(BaseModel):
    source: str
    page: int | None = None
    snippet: str | None = None


class QueryResponse(BaseModel):
    answer: str
    confidence: float
    plan: list[ResearchStep] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    model_tier_used: str | None = None
    artifact_session_id: str | None = None
    trace_id: str | None = None
    needs_human_review: bool = False
