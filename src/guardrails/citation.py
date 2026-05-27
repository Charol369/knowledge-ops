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


def extract_citations(answer_text: str) -> list[dict]:
    """从答案文本里抽取 [来源: X, page Y] 这种引用标记"""
    citations: list[dict[str, Any]] = []
    for match in CITATION_PATTERN.finditer(answer_text):
        source = match.group(1).strip()
        page = int(match.group(2)) if match.group(2) is not None else None
        citations.append({"source": source, "page": page, "snippet": None})
    return citations


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


def _matches(source: str, page: Any, metadata: dict[str, Any]) -> bool:
    if str(metadata.get("source", "")).strip() != source:
        return False
    if page is None:
        return True
    metadata_page = metadata.get("page")
    return metadata_page is not None and str(metadata_page) == str(page)


def _citation_key(source: str, page: Any) -> str:
    if page is None:
        return source
    return f"{source}#page={page}"
