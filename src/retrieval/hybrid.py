"""混合检索（Hybrid）：稠密 + 稀疏融合。"""
import hashlib

from langchain_core.documents import Document


def _document_key(doc: Document) -> str:
    source = str(doc.metadata.get("source", ""))
    page = str(doc.metadata.get("page", ""))
    content_hash = hashlib.sha256(doc.page_content.encode("utf-8")).hexdigest()
    return f"{source}:{page}:{content_hash}"


def reciprocal_rank_fusion(
    rank_lists: list[list[Document]],
    k: int = 60,
    top_n: int = 10,
) -> list[Document]:
    """RRF 融合多个 retriever 的 ranking"""
    if top_n <= 0:
        return []

    scores: dict[str, float] = {}
    first_seen: dict[str, int] = {}
    documents: dict[str, Document] = {}
    seen_order = 0

    for rank_list in rank_lists:
        for rank, doc in enumerate(rank_list, start=1):
            if "source" not in doc.metadata:
                raise ValueError("Hybrid retrieval candidates must include source metadata.")
            key = _document_key(doc)
            if key not in documents:
                documents[key] = doc
                first_seen[key] = seen_order
                seen_order += 1
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)

    ranked_keys = sorted(
        scores,
        key=lambda key: (scores[key], -first_seen[key]),
        reverse=True,
    )

    fused: list[Document] = []
    for key in ranked_keys[:top_n]:
        original = documents[key]
        metadata = dict(original.metadata)
        metadata["rrf_score"] = scores[key]
        fused.append(Document(page_content=original.page_content, metadata=metadata))
    return fused
