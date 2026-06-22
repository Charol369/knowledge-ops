"""API 路由层。

主入口语义已从“普通 RAG 问答”升级为“研究型 Agent 请求入口”。
即使当前仍是骨架，也要把最终的数据流设计清楚：
question -> policy -> graph -> artifacts -> response / stream
"""
import json
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.agents.graph import run_research_graph
from src.api.schemas import (
    Citation,
    FeedbackRequest,
    FeedbackResponse,
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    ResearchStep,
)
from src.ingest.loaders import load_directory, load_docx, load_html, load_pdf
from src.ingest.splitters import split_recursive
from src.observability.langfuse_setup import record_langfuse_score
from src.observability.metrics import business_metrics

router = APIRouter()


def _resolve_request_trace_id(req: QueryRequest, trace_id: str | None = None) -> str | None:
    return trace_id or req.thread_id


def _run_query(req: QueryRequest, trace_id: str | None = None) -> QueryResponse:
    effective_trace_id = _resolve_request_trace_id(req, trace_id=trace_id)
    result = run_research_graph(
        question=req.question,
        intent=req.intent,
        thread_id=effective_trace_id,
        docs_dir=req.docs_dir,
        index_dir=req.index_dir,
        artifact_root=req.artifact_root,
        embedding_backend=req.embedding_backend,
    )
    response = _query_result_to_response(result)
    response.session_id = req.session_id or response.trace_id
    return response


def _query_result_to_response(result: dict) -> QueryResponse:
    verification = result.get("verification", {})
    plan = [
        ResearchStep(
            step_id=str(index),
            description=step,
            status="completed",
        )
        for index, step in enumerate(result.get("plan", []), start=1)
    ]
    citations = [
        Citation(
            source=str(item.get("source", "")),
            page=item.get("page"),
            snippet=item.get("snippet"),
        )
        for item in result.get("citations", [])
    ]
    return QueryResponse(
        answer=result.get("answer", ""),
        confidence=float(verification.get("confidence", result.get("confidence", 0.0))),
        plan=plan,
        citations=citations,
        intent=result.get("intent"),
        strategy=result.get("strategy"),
        intent_confidence=result.get("intent_confidence"),
        tool_name=result.get("tool_name"),
        tool_status=result.get("tool_status"),
        tool_result=result.get("tool_result"),
        fallback_reason=result.get("fallback_reason") or result.get("blocked_reason"),
        diagnostics=result.get("diagnostics"),
        model_tier_used=result.get("model_tier"),
        synthesis_mode=result.get("synthesis_mode"),
        synthesis_status=result.get("synthesis_status"),
        synthesis_model=result.get("synthesis_model"),
        synthesis_blocked_reason=result.get("synthesis_blocked_reason"),
        session_id=result.get("session_id") or result.get("trace_id"),
        artifact_session_id=result.get("artifact_session_id"),
        trace_id=result.get("trace_id"),
        needs_human_review=bool(result.get("needs_human_review", False)),
    )


def _sse_event(event: str, data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


@router.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    """主入口：用户问题 -> policy layer -> agent graph -> 结构化研究结果。"""
    return _run_query(req)


@router.post("/query/stream")
async def query_stream(req: QueryRequest):
    """SSE wrapper around the existing graph-backed query contract."""
    trace_id = _resolve_request_trace_id(req) or uuid4().hex

    def event_stream():
        yield _sse_event(
            "progress",
            {
                "stage": "started",
                "trace_id": trace_id,
                "message": "Query accepted.",
            },
        )
        response = _run_query(req, trace_id=trace_id)
        yield _sse_event(
            "progress",
            {
                "stage": "graph_completed",
                "trace_id": response.trace_id,
                "intent": response.intent,
                "strategy": response.strategy,
                "tool_name": response.tool_name,
                "tool_status": response.tool_status,
                "plan": [step.model_dump(mode="json") for step in response.plan],
                "citations_count": len(response.citations),
                "artifact_session_id": response.artifact_session_id,
            },
        )
        yield _sse_event("completion", response.model_dump(mode="json"))

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/feedback", response_model=FeedbackResponse)
async def feedback(req: FeedbackRequest):
    """Capture user feedback locally and optionally mirror it to Langfuse."""
    business_metrics.record_feedback(
        trace_id=req.trace_id,
        score=req.score,
        comment=req.comment,
        source=req.source,
    )
    langfuse_result = record_langfuse_score(
        trace_id=req.trace_id,
        score=req.score,
        name=req.name,
        comment=req.comment,
    )
    return FeedbackResponse(
        status="ok",
        trace_id=req.trace_id,
        score=float(req.score),
        storage="local-memory",
        langfuse_status=str(langfuse_result["status"]),
        blocked_reason=langfuse_result["blocked_reason"],
    )


@router.post("/ingest", response_model=IngestResponse)
async def ingest(req: IngestRequest):
    """批量入库接口（admin 用）。"""
    path = Path(req.path)
    if not path.exists():
        return IngestResponse(
            status="blocked",
            path=str(path),
            blocked_reason=f"Local ingest path does not exist: {path}",
        )

    try:
        if path.is_dir():
            docs = load_directory(path, glob=req.glob)
        elif path.suffix.lower() == ".pdf":
            docs = load_pdf(path)
        elif path.suffix.lower() == ".docx":
            docs = load_docx(path)
        elif path.suffix.lower() in {".html", ".htm"}:
            docs = load_html(path)
        else:
            return IngestResponse(
                status="blocked",
                path=str(path),
                blocked_reason=f"Unsupported local ingest file type: {path.suffix}",
            )
        chunks = split_recursive(docs)
    except Exception as exc:
        return IngestResponse(
            status="blocked",
            path=str(path),
            blocked_reason=f"Local ingest failed: {exc}",
        )

    if not chunks:
        return IngestResponse(
            status="blocked",
            path=str(path),
            documents_loaded=len(docs),
            chunks_created=0,
            blocked_reason="No supported local content was loaded from the requested path.",
        )

    index_dir = req.index_dir
    if req.build_index:
        try:
            from src.ingest.embedder import get_embedder
            from src.retrieval.dense import build_index

            target_index_dir = index_dir or "./data/faiss/api_ingest"
            build_index(
                chunks,
                get_embedder(backend=req.embedding_backend),
                index_dir=target_index_dir,
            )
            index_dir = target_index_dir
        except Exception as exc:
            return IngestResponse(
                status="blocked",
                path=str(path),
                documents_loaded=len(docs),
                chunks_created=len(chunks),
                blocked_reason=f"Local FAISS indexing blocked: {exc}",
            )

    return IngestResponse(
        status="ok",
        path=str(path),
        documents_loaded=len(docs),
        chunks_created=len(chunks),
        index_dir=index_dir,
    )
