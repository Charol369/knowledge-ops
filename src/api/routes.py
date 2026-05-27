"""API 路由层。

主入口语义已从“普通 RAG 问答”升级为“研究型 Agent 请求入口”。
即使当前仍是骨架，也要把最终的数据流设计清楚：
question -> policy -> graph -> artifacts -> response / stream
"""
from pathlib import Path

from fastapi import APIRouter, HTTPException

from src.api.schemas import IngestRequest, IngestResponse, QueryRequest, QueryResponse
from src.ingest.loaders import load_directory, load_docx, load_html, load_pdf
from src.ingest.splitters import split_recursive

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    """主入口：用户问题 -> policy layer -> agent graph -> 结构化研究结果。"""
    # TODO Sprint 1: 支持最小 CLI / API research pipeline
    # TODO Sprint 3: 接到 src.agents.graph.build_graph().invoke(...)
    # TODO Sprint 4: 接入 complexity classifier / model router / langfuse / injection 检测
    # TODO Sprint 5: 切 SSE 流式响应，返回 plan / progress / evidence / final report
    raise HTTPException(status_code=501, detail="Not implemented yet (Sprint 1-5)")


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
            build_index(chunks, get_embedder(), index_dir=target_index_dir)
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
