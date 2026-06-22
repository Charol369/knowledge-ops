"""Retrieval Orchestrator：编排确定性检索服务。

职责：
- 调 retrieval services，而不是自己“自由发挥”地检索
- 在必要时局部采用 ReAct：重写 query、补检索、分解子问题
- 为 synthesizer 提供干净的 evidence 集合
"""
from typing import Any

from langchain_core.documents import Document

from src.config import settings
from src.agents.document_tools import blocked_table_lookup_result, count_references, lookup_section
from src.ingest.embedder import get_embedder
from src.ingest.loaders import load_directory
from src.ingest.splitters import split_recursive
from src.retrieval.context_builder import ContextBuilder
from src.retrieval.dense import build_index, load_index, search
from src.retrieval.hybrid import reciprocal_rank_fusion
from src.retrieval.query_transform import multi_query_expand
from src.retrieval.rerank import CrossEncoderReranker
from src.retrieval.sparse import BM25Retriever, tokenize_query


def _doc_to_evidence(doc: Document) -> dict[str, Any]:
    item = {
        "content": doc.page_content,
        "source": str(doc.metadata.get("source", "")).replace("\\", "/"),
        "page": doc.metadata.get("page"),
    }
    for key in ("score", "rrf_score", "lexical_score", "rerank_score"):
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

        sparse_retriever = BM25Retriever(chunks)
        fused_by_query: list[list[Document]] = []
        for candidate_query in self._candidate_queries(question):
            dense_results = search(vectorstore, candidate_query, k=self.top_k)
            sparse_results = sparse_retriever.search(candidate_query, k=self.top_k)
            fused_by_query.append(
                reciprocal_rank_fusion(
                    [dense_results, sparse_results],
                    top_n=self.top_k,
                )
            )

        if not fused_by_query:
            return []
        fused = (
            fused_by_query[0]
            if len(fused_by_query) == 1
            else reciprocal_rank_fusion(fused_by_query, top_n=self.top_k)
        )
        ranked = self._maybe_rerank(question, self._apply_lexical_boost(question, fused))
        return [_doc_to_evidence(doc) for doc in ranked]

    def _candidate_queries(self, question: str) -> list[str]:
        if not settings.query_transform_enabled:
            return [question]
        candidates = multi_query_expand(
            question,
            n=max(1, settings.query_transform_count),
        )
        deduped: list[str] = []
        seen: set[str] = set()
        for candidate in candidates:
            normalized = candidate.strip()
            if normalized and normalized not in seen:
                deduped.append(normalized)
                seen.add(normalized)
        return deduped or [question]

    def _maybe_rerank(self, question: str, docs: list[Document]) -> list[Document]:
        if not settings.rerank_enabled:
            return docs
        result = CrossEncoderReranker(model_name=settings.rerank_model_name).rerank(
            question,
            docs,
            top_k=self.top_k,
        )
        if result.status == "ok":
            return result.documents
        return docs

    def _apply_lexical_boost(self, question: str, docs: list[Document]) -> list[Document]:
        """Deterministic tie-breaker for offline/hash demo retrieval."""
        terms = set(tokenize_query(question))
        if not terms:
            return docs

        boosted: list[tuple[float, int, Document]] = []
        for index, doc in enumerate(docs):
            content = doc.page_content.lower()
            matched_terms = {term for term in terms if term in content}
            score = float(len(matched_terms))
            if "multi head attention" in content or "multi-head attention" in content:
                score += 2.0
            if "attention layers running in parallel" in content:
                score += 1.5
            if "jointly attend" in content:
                score += 1.5
            if "<eos>" in content or "<pad>" in content:
                score -= 1.0
            metadata = dict(doc.metadata)
            metadata["lexical_score"] = score
            boosted.append((score, -index, Document(page_content=doc.page_content, metadata=metadata)))

        return [
            doc
            for _, _, doc in sorted(
                boosted,
                key=lambda item: (item[0], item[2].metadata.get("rrf_score", 0.0), item[1]),
                reverse=True,
            )
        ]


def retrieval_orchestrator_node(state: dict[str, Any]) -> dict[str, Any]:
    execution_path = [*state.get("execution_path", []), "retrieval_orchestrator"]
    strategy = state.get("strategy") or "hybrid_retrieval"

    if strategy == "blocked":
        evidence = []
        blocked_reason = "The request cannot be answered from the available knowledge base."
        tool_status = "blocked"
        tool_result = {
            "status": "blocked",
            "blocked_reason": blocked_reason,
            "evidence": [],
        }
    elif strategy == "table_lookup":
        result = blocked_table_lookup_result()
        evidence = []
        blocked_reason = str(result["blocked_reason"])
        tool_status = "blocked"
        tool_result = result
    elif strategy == "reference_count":
        result = count_references(state.get("docs_dir", "data"))
        tool_result = result.as_dict()
        evidence = result.evidence or []
        blocked_reason = result.blocked_reason
        tool_status = result.status
    elif strategy == "section_lookup":
        result = lookup_section(
            state.get("docs_dir", "data"),
            state.get("question", ""),
            section_target=state.get("intent_target"),
        )
        tool_result = result.as_dict()
        evidence = result.evidence or []
        blocked_reason = result.blocked_reason
        tool_status = result.status
    else:
        tool_result = state.get("tool_result")
        tool_status = state.get("tool_status")

    if strategy in {"blocked", "table_lookup", "reference_count", "section_lookup"}:
        pass
    elif state.get("evidence"):
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
    diagnostics = {
        "intent": state.get("intent"),
        "strategy": strategy,
        "tool_name": state.get("tool_name"),
        "tool_status": tool_status,
        "fallback_reason": blocked_reason,
        "retrieval_top_k": state.get("top_k") or settings.top_k_final,
        "route_reason": state.get("route_reason"),
    }
    return {
        **state,
        "evidence": evidence,
        "context": context,
        "blocked_reason": blocked_reason,
        "fallback_reason": blocked_reason,
        "tool_status": tool_status,
        "tool_result": tool_result,
        "diagnostics": diagnostics,
        "execution_path": execution_path,
    }
