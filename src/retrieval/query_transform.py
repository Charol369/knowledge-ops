"""查询变换：HyDE / Multi-Query / Query Decomposition."""
import re
from collections.abc import Callable
from typing import Any


def _call_llm(llm: Any, prompt: str) -> str:
    if callable(llm):
        result = llm(prompt)
    elif hasattr(llm, "invoke"):
        result = llm.invoke(prompt)
    else:
        raise TypeError("llm must be callable or expose invoke(prompt).")
    if hasattr(result, "content"):
        return str(result.content).strip()
    return str(result).strip()


def hyde_transform(query: str, llm: Callable[[str], str] | Any | None = None) -> str:
    """HyDE：让 LLM 生成一段假答案用于检索"""
    normalized = query.strip()
    if not normalized:
        return ""
    prompt = f"Write a concise hypothetical passage that would answer: {normalized}"
    if llm is not None:
        return _call_llm(llm, prompt)
    return (
        "Hypothetical answer passage for retrieval. "
        f"Question: {normalized}. "
        "Include core entities, terminology, and likely evidence phrases."
    )


def multi_query_expand(
    query: str,
    llm: Callable[[str], str] | Any | None = None,
    n: int = 3,
) -> list[str]:
    """生成 N 个查询改写"""
    normalized = query.strip()
    if n <= 0 or not normalized:
        return []
    if llm is not None:
        prompt = f"Generate {n} different search query rewrites of: {normalized}"
        raw = _call_llm(llm, prompt)
        candidates = [
            re.sub(r"^\s*[-*\d.)]+\s*", "", line).strip()
            for line in raw.splitlines()
            if line.strip()
        ]
    else:
        candidates = [
            normalized,
            f"{normalized} key concepts evidence",
            f"{normalized} definitions comparison",
            f"{normalized} implementation details",
            f"{normalized} citations sources",
        ]

    deduped: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate and candidate not in seen:
            deduped.append(candidate)
            seen.add(candidate)
        if len(deduped) == n:
            break
    while len(deduped) < n:
        deduped.append(f"{normalized} variant {len(deduped) + 1}")
    return deduped


def decompose_query(query: str) -> list[str]:
    """把多跳问题拆成可独立检索的子问题；不依赖 LangGraph。"""
    normalized = query.strip()
    if not normalized:
        return []
    parts = [
        part.strip(" .?？")
        for part in re.split(r"\bthen\b|\band\b|[;；。？?]", normalized, flags=re.IGNORECASE)
        if part.strip(" .?？")
    ]
    if len(parts) <= 1:
        return [normalized]
    return [f"{part}?" for part in parts]
