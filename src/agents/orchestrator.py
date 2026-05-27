"""Retrieval Orchestrator：编排确定性检索服务。

职责：
- 调 retrieval services，而不是自己“自由发挥”地检索
- 在必要时局部采用 ReAct：重写 query、补检索、分解子问题
- 为 synthesizer 提供干净的 evidence 集合
"""
from typing import Any

from langchain_core.documents import Document

from src.config import settings
from src.ingest.embedder import get_embedder
from src.ingest.loaders import load_directory
from src.ingest.splitters import split_recursive
from src.retrieval.context_builder import ContextBuilder
from src.retrieval.dense import build_index, load_index, search
from src.retrieval.hybrid import reciprocal_rank_fusion
from src.retrieval.sparse import BM25Retriever


def _doc_to_evidence(doc: Document) -> dict[str, Any]:
    item = {
        "content": doc.page_content,
        "source": doc.metadata.get("source", ""),
        "page": doc.metadata.get("page"),
    }
    for key in ("score", "rrf_score", "rerank_score"):
        if key in doc.metadata:
            item[key] = doc.metadata[key]
    return item

class RetrievalOrchestrator:
    def __init__(
        self,
        docs_dir: str = "data",
        index_dir: str = "data/faiss/sprint1",
        embedding_backend: str = "hash",
        top_k: int | None = None,
    ):
        self.docs_dir = docs_dir
        self.index_dir = index_dir
        self.embedding_backend = embedding_backend
        self.top_k = top_k or settings.top_k_final

    def gather_evidence(self, question: str, plan: list[str]) -> list[dict]:
        docs = load_directory(self.docs_dir)
        chunks = split_recursive(docs)
        if not chunks:
            return []

        embedder = get_embedder(backend=self.embedding_backend)
        try:
            vectorstore = load_index(self.index_dir, embedder)
        except Exception:
            vectorstore = build_index(chunks, embedder, index_dir=self.index_dir)

        dense_results = search(vectorstore, question, k=self.top_k)
        sparse_results = BM25Retriever(chunks).search(question, k=self.top_k)
        fused = reciprocal_rank_fusion(
            [dense_results, sparse_results],
            top_n=self.top_k,
        )
        return [_doc_to_evidence(doc) for doc in fused]


def retrieval_orchestrator_node(state: dict[str, Any]) -> dict[str, Any]:
    execution_path = [*state.get("execution_path", []), "retrieval_orchestrator"]

    if state.get("evidence"):
        evidence = list(state["evidence"])
        blocked_reason = None
    else:
        try:
            orchestrator = RetrievalOrchestrator(
                docs_dir=state.get("docs_dir", "data"),
                index_dir=state.get("index_dir", "data/faiss/sprint1"),
                embedding_backend=state.get("embedding_backend", "hash"),
                top_k=state.get("top_k") or settings.top_k_final,
            )
            evidence = orchestrator.gather_evidence(
                state["question"],
                state.get("plan", []),
            )
            blocked_reason = None if evidence else "No local evidence was retrieved."
        except Exception as exc:
            evidence = []
            blocked_reason = f"Local retrieval/context blocked: {exc}"

    context = ContextBuilder(max_evidence_items=state.get("top_k") or settings.top_k_final).build(
        question=state["question"],
        evidence=evidence,
        artifact_context=state.get("artifact_context"),
    )
    return {
        **state,
        "evidence": evidence,
        "context": context,
        "blocked_reason": blocked_reason,
        "execution_path": execution_path,
    }
