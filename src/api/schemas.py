"""API 请求/响应 Pydantic 模型。"""
from typing import Literal

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    intent: str | None = Field(default=None, description="可选：lookup/research/report，不传则由 policy layer 判定")
    thread_id: str | None = Field(default=None, description="可选：会话 ID，用于隔离 graph checkpointer 与 artifact session")
    docs_dir: str = Field(default="data", description="Sprint 3 local documents directory.")
    index_dir: str = Field(default="data/faiss/sprint1", description="Sprint 3 local FAISS index directory.")
    artifact_root: str | None = Field(default=None, description="Optional Sprint 3 artifact root directory.")
    embedding_backend: Literal["hash", "local", "fake", "huggingface"] = Field(
        default="hash",
        description="Embedding backend for local graph retrieval; hash is the offline Sprint 3 default.",
    )


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
    synthesis_mode: str | None = None
    synthesis_status: str | None = None
    synthesis_model: str | None = None
    synthesis_blocked_reason: str | None = None
    artifact_session_id: str | None = None
    trace_id: str | None = None
    needs_human_review: bool = False


class FeedbackRequest(BaseModel):
    trace_id: str = Field(min_length=1, max_length=256)
    score: float = Field(ge=-1, le=1)
    comment: str | None = Field(default=None, max_length=2000)
    source: str | None = Field(default=None, max_length=128)
    name: str = Field(default="user_feedback", min_length=1, max_length=128)


class FeedbackResponse(BaseModel):
    status: str
    trace_id: str
    score: float
    storage: str
    langfuse_status: str
    blocked_reason: str | None = None


class IngestRequest(BaseModel):
    path: str = Field(min_length=1, description="Local file or directory path to ingest.")
    glob: str = Field(default="**/*", min_length=1)
    build_index: bool = Field(default=False, description="Build a local FAISS index after loading.")
    index_dir: str | None = Field(default=None, description="Optional local FAISS index directory.")
    embedding_backend: Literal["hash", "local", "fake", "huggingface"] = Field(
        default="hash",
        description="Embedding backend for local ingest; hash is the offline Sprint 1 default.",
    )


class IngestResponse(BaseModel):
    status: str
    path: str
    documents_loaded: int = 0
    chunks_created: int = 0
    index_dir: str | None = None
    blocked_reason: str | None = None
