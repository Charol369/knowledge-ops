"""MCP Server：把 KnowledgeOps 的能力暴露为 MCP 标准协议。

MCP 在本项目里的定位是工具标准化层：
- 暴露 retrieval / summarize / artifact metadata 能力
- 供 Claude Desktop / Cursor / Cline 复用
- 不承担 A2A / ANP 级别的网络复杂度
"""
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from src.agents.orchestrator import RetrievalOrchestrator
from src.agents.reporter import Reporter
from src.agents.synthesizer import Synthesizer
from src.config import settings
from src.ingest.loaders import load_directory
from src.ingest.splitters import split_recursive
from src.retrieval.context_builder import load_artifact_context

mcp = FastMCP("knowledge-ops")


@mcp.tool()
def search_knowledge(
    query: str,
    top_k: int = 5,
    docs_dir: str = "data",
    index_dir: str = "data/faiss/sprint1",
    embedding_backend: str = "hash",
) -> str:
    """检索企业知识库，返回 Top-K 相关 evidence（Markdown 格式）。"""
    try:
        evidence = RetrievalOrchestrator(
            docs_dir=docs_dir,
            index_dir=index_dir,
            embedding_backend=embedding_backend,
            top_k=top_k,
        ).gather_evidence(query, [])
    except Exception as exc:
        return f"status=blocked\nblocked_reason=Local MCP retrieval blocked: {exc}"

    if not evidence:
        return "status=blocked\nblocked_reason=No local evidence was retrieved."

    lines = ["status=ok", f"query={query}", "evidence:"]
    for index, item in enumerate(evidence[:top_k], start=1):
        page = item.get("page")
        source = item.get("source", "")
        citation = f"{source}, page {page}" if page is not None else source
        content = str(item.get("content", "")).strip().replace("\n", " ")
        lines.append(f"{index}. {content} [source: {citation}]")
    return "\n".join(lines)


@mcp.tool()
def summarize_documents(
    query: str,
    docs_dir: str = "data",
    index_dir: str = "data/faiss/sprint1",
    embedding_backend: str = "hash",
) -> str:
    """对检索结果做结构化总结。"""
    try:
        evidence = RetrievalOrchestrator(
            docs_dir=docs_dir,
            index_dir=index_dir,
            embedding_backend=embedding_backend,
            top_k=settings.top_k_final,
        ).gather_evidence(query, [])
    except Exception as exc:
        return f"status=blocked\nblocked_reason=Local MCP summarization blocked: {exc}"

    if not evidence:
        return "status=blocked\nblocked_reason=No local evidence was retrieved."
    synthesis = Synthesizer().synthesize(evidence, question=query)
    return Reporter().render(query, synthesis)


@mcp.resource("knowledge://collections/{name}")
def get_collection_info(name: str) -> str:
    """暴露 collection 元信息作为 MCP Resource。"""
    return inspect_collection(name, docs_dir="data")


def inspect_collection(name: str, docs_dir: str = "data") -> str:
    root = Path(docs_dir)
    if not root.exists():
        return (
            f"collection={name}\n"
            "status=blocked\n"
            f"blocked_reason=Local docs directory does not exist: {root}"
        )
    try:
        docs = load_directory(root)
        chunks = split_recursive(docs)
    except Exception as exc:
        return (
            f"collection={name}\n"
            "status=blocked\n"
            f"blocked_reason=Local collection inspection blocked: {exc}"
        )
    total_bytes = _loaded_source_bytes(docs)
    return "\n".join(
        [
            f"collection={name}",
            "status=ok",
            f"docs_dir={root}",
            f"documents_loaded={len(docs)}",
            f"chunks_created={len(chunks)}",
            f"size_bytes={total_bytes}",
        ]
    )


def _loaded_source_bytes(docs: list) -> int:
    total_bytes = 0
    seen: set[str] = set()
    for doc in docs:
        source = str(doc.metadata.get("source", ""))
        if not source or source in seen:
            continue
        seen.add(source)
        path = Path(source)
        try:
            if path.is_file():
                total_bytes += path.stat().st_size
        except OSError:
            continue
    return total_bytes


@mcp.resource("knowledge://sessions/{session_id}")
def get_session_artifact(session_id: str) -> str:
    """暴露研究中间产物（plan / evidence / final report）元信息。"""
    return inspect_session_artifact(session_id, artifact_root=settings.artifact_root_dir)


def inspect_session_artifact(
    session_id: str,
    artifact_root: str = settings.artifact_root_dir,
) -> str:
    session_dir = Path(artifact_root) / session_id
    if not session_dir.exists():
        return (
            f"session_id={session_id}\n"
            "status=blocked\n"
            f"blocked_reason=Artifact session directory does not exist: {session_dir}"
        )
    try:
        material = load_artifact_context(session_dir)
    except Exception as exc:
        return (
            f"session_id={session_id}\n"
            "status=blocked\n"
            f"blocked_reason=Artifact loading blocked: {exc}"
        )
    return "\n".join(
        [
            f"session_id={session_id}",
            "status=ok",
            "artifact_context:",
            json.dumps(material, ensure_ascii=False, indent=2),
        ]
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
