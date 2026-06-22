"""引用强制（Citation Enforcement）

防幻觉的 4 把刀之一（Day2 Anthropic Ch8）：
  要求 LLM 每个事实必须附 [来源: X]，编造的话没法贴标签。

Sprint 3 任务：实现 citation 提取 + 校验（确保每个 citation 真的指向了 context 里的某个 chunk）。
"""
import re
from typing import Any

from langchain_core.documents import Document


CITATION_PATTERN = re.compile(
    r"\[(?:来源|source):\s*([^,\]]+?)(?:,\s*(?:page|p\.?)\s*(\d+))?\]",
    re.IGNORECASE,
)


def extract_citations(answer_text: str, evidence: list[Any] | None = None) -> list[dict]:
    """从答案文本里抽取 [来源: X, page Y] 这种引用标记"""
    citations: list[dict[str, Any]] = []
    for match in CITATION_PATTERN.finditer(answer_text):
        source = match.group(1).strip()
        page = int(match.group(2)) if match.group(2) is not None else None
        citations.append({"source": source, "page": page, "snippet": None})
    if evidence is None:
        return citations
    return attach_snippets(citations, evidence)


def attach_snippets(
    citations: list[dict],
    evidence: list[Any],
    max_chars: int = 260,
) -> list[dict]:
    enriched: list[dict[str, Any]] = []
    used_evidence: set[int] = set()
    seen: set[tuple[str, Any, str | None]] = set()
    for citation in citations:
        item = dict(citation)
        item["snippet"] = _find_snippet(
            citation,
            evidence,
            max_chars=max_chars,
            used_evidence=used_evidence,
        )
        key = (_normalize_source(item.get("source", "")), item.get("page"), item.get("snippet"))
        if key in seen:
            continue
        seen.add(key)
        enriched.append(item)
    return enriched


def verify_citations(citations: list[dict], context_chunks: list) -> tuple[bool, list[str]]:
    """校验每个 citation 是否指向真实的 context chunk。返回 (all_valid, invalid_list)"""
    available = [_chunk_metadata(chunk) for chunk in context_chunks]
    invalid: list[str] = []

    for citation in citations:
        source = str(citation.get("source", "")).strip()
        page = citation.get("page")
        if not source:
            invalid.append("<missing-source>")
            continue
        if not any(_matches(source, page, metadata) for metadata in available):
            invalid.append(_citation_key(source, page))

    return not invalid, invalid


def _chunk_metadata(chunk: Any) -> dict[str, Any]:
    if isinstance(chunk, Document):
        return dict(chunk.metadata)
    if isinstance(chunk, dict):
        if "metadata" in chunk and isinstance(chunk["metadata"], dict):
            metadata = dict(chunk["metadata"])
        else:
            metadata = {}
        for key in ("source", "page"):
            if key in chunk and key not in metadata:
                metadata[key] = chunk[key]
        return metadata
    metadata = getattr(chunk, "metadata", None)
    return dict(metadata) if isinstance(metadata, dict) else {}


def _chunk_content(chunk: Any) -> str:
    if isinstance(chunk, Document):
        return chunk.page_content
    if isinstance(chunk, dict):
        return str(chunk.get("content") or chunk.get("page_content") or "")
    return str(getattr(chunk, "page_content", "") or "")


def _find_snippet(
    citation: dict,
    evidence: list[Any],
    max_chars: int,
    used_evidence: set[int] | None = None,
) -> str | None:
    source = str(citation.get("source", "")).strip()
    page = citation.get("page")
    fallback: str | None = None
    fallback_index: int | None = None
    for index, chunk in enumerate(evidence):
        metadata = _chunk_metadata(chunk)
        if _matches(source, page, metadata):
            content = " ".join(_chunk_content(chunk).split())
            if not content:
                return None
            snippet = content if len(content) <= max_chars else content[: max_chars - 3].rstrip() + "..."
            if used_evidence is None or index not in used_evidence:
                if used_evidence is not None:
                    used_evidence.add(index)
                return snippet
            if fallback is None:
                fallback = snippet
                fallback_index = index
    if fallback_index is not None and used_evidence is not None:
        used_evidence.add(fallback_index)
    return fallback


def _matches(source: str, page: Any, metadata: dict[str, Any]) -> bool:
    if _normalize_source(metadata.get("source", "")).strip() != _normalize_source(source).strip():
        return False
    if page is None:
        return True
    metadata_page = metadata.get("page")
    return metadata_page is not None and str(metadata_page) == str(page)


def _citation_key(source: str, page: Any) -> str:
    if page is None:
        return source
    return f"{source}#page={page}"


def _normalize_source(source: Any) -> str:
    return str(source).replace("\\", "/")
