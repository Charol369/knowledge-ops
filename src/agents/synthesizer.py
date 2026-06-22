"""Synthesizer：证据整合节点。

职责：
- 对每个子任务返回的 evidence 做归纳
- 形成中间结论，而不是直接输出华丽答案
- 将结构化 synthesis 交给 reporter
"""
import re
from typing import Any

from src.agents.llm_synthesizer import LLMSynthesizer
from src.config import settings
from src.retrieval.sparse import tokenize_query


EXPLANATORY_CUES = {
    "allows",
    "attention",
    "concatenated",
    "consists",
    "different",
    "heads",
    "jointly",
    "keys",
    "parallel",
    "projected",
    "queries",
    "values",
}


class Synthesizer:
    def synthesize(self, evidence: list[dict], question: str = "") -> str:
        if not evidence:
            return "No local evidence was retrieved, so no grounded synthesis is available."
        lines = []
        for index, item in enumerate(self._select_evidence(evidence, question), start=1):
            source = item.get("source", "unknown source")
            page = item.get("page")
            content = self._best_segment(
                str(item.get("content", "")).strip(),
                question=question,
            )
            citation = f"{source}, page {page}" if page is not None else source
            lines.append(f"{index}. {content} [source: {citation}]")
        return "\n".join(lines)

    def _select_evidence(self, evidence: list[dict], question: str) -> list[dict]:
        terms = set(tokenize_query(question))
        if not terms:
            return evidence[:3]

        def score(item: dict) -> tuple[float, float]:
            content = _clean_text(str(item.get("content", ""))).lower()
            lexical_score = float(item.get("lexical_score") or 0.0)
            overlap = sum(1 for term in terms if term in content)
            cue_score = sum(0.25 for cue in EXPLANATORY_CUES if cue in content)
            return lexical_score + overlap + cue_score, float(item.get("rrf_score") or 0.0)

        ranked = sorted(evidence, key=score, reverse=True)
        selected: list[dict] = []
        seen: set[tuple[str, str, str]] = set()
        for item in ranked:
            content = _clean_text(str(item.get("content", "")))
            key = (
                str(item.get("source", "")).replace("\\", "/"),
                str(item.get("page", "")),
                content[:160],
            )
            if key in seen:
                continue
            seen.add(key)
            selected.append(item)
            if len(selected) >= 3:
                break
        return selected or evidence[:3]

    def _best_segment(self, content: str, question: str) -> str:
        cleaned = _clean_text(content)
        if not cleaned:
            return "Retrieved evidence is empty."
        terms = set(tokenize_query(question))
        segments = _candidate_segments(cleaned)
        if not segments:
            return _trim(cleaned)

        def score(segment: str) -> tuple[float, int]:
            lowered = segment.lower()
            overlap = sum(1 for term in terms if term in lowered)
            cues = sum(1 for cue in EXPLANATORY_CUES if cue in lowered)
            noise_penalty = 2 if "<eos>" in lowered or "<pad>" in lowered else 0
            return float(overlap + cues - noise_penalty), -len(segment)

        best = max(segments, key=score)
        return _trim(best)


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _candidate_segments(text: str) -> list[str]:
    normalized = _clean_text(text)
    rough_segments = re.split(r"(?<=[.!?])\s+|(?<=:)\s+", normalized)
    segments: list[str] = []
    for segment in rough_segments:
        stripped = segment.strip()
        if len(stripped) < 24:
            continue
        if len(stripped) <= 360:
            segments.append(stripped)
            continue
        for start in range(0, len(stripped), 260):
            window = stripped[start : start + 360].strip()
            if len(window) >= 24:
                segments.append(window)
    return segments


def _trim(text: str, limit: int = 320) -> str:
    normalized = _clean_text(text)
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def synthesizer_node(state: dict[str, Any]) -> dict[str, Any]:
    evidence = state.get("context", {}).get("evidence") or state.get("evidence", [])
    tool_synthesis = _synthesize_tool_or_blocked_state(state)
    if tool_synthesis is not None:
        execution_path = [*state.get("execution_path", []), "synthesizer"]
        return {
            **state,
            **tool_synthesis,
            "execution_path": execution_path,
        }

    llm_result = LLMSynthesizer().synthesize(
        question=state.get("question", ""),
        evidence=evidence,
        model_tier=state.get("model_tier"),
    )
    if llm_result.status == "ok":
        synthesis = llm_result.answer
        synthesis_mode = "llm"
    elif settings.llm_synthesis_fallback_enabled:
        synthesis = Synthesizer().synthesize(
            evidence,
            question=state.get("question", ""),
        )
        synthesis_mode = "deterministic_fallback"
    else:
        synthesis = (
            "No production LLM answer is available. "
            f"Blocked reason: {llm_result.blocked_reason or llm_result.status}"
        )
        synthesis_mode = "blocked"

    execution_path = [*state.get("execution_path", []), "synthesizer"]
    return {
        **state,
        "synthesis": synthesis,
        "synthesis_mode": synthesis_mode,
        "synthesis_status": llm_result.status,
        "synthesis_model": llm_result.model,
        "synthesis_blocked_reason": llm_result.blocked_reason,
        "synthesis_usage": llm_result.usage,
        "execution_path": execution_path,
    }


def _synthesize_tool_or_blocked_state(state: dict[str, Any]) -> dict[str, Any] | None:
    strategy = state.get("strategy")
    tool_status = state.get("tool_status")
    tool_result = state.get("tool_result") or {}
    blocked_reason = (
        state.get("fallback_reason")
        or state.get("blocked_reason")
        or tool_result.get("blocked_reason")
    )

    if strategy == "reference_count" and tool_status == "ok":
        count = tool_result.get("count")
        if count is None:
            return None
        source = str(tool_result.get("source") or "local knowledge base").replace("\\", "/")
        page = tool_result.get("page_start")
        citation = _citation_marker(source, page)
        return {
            "synthesis": (
                f"The references section contains {count} entries according to the "
                f"deterministic reference count tool.{citation}"
            ),
            "synthesis_mode": "deterministic_tool",
            "synthesis_status": "ok",
            "synthesis_model": None,
            "synthesis_blocked_reason": None,
            "synthesis_usage": None,
        }

    if tool_status == "blocked" or strategy == "blocked":
        reason = blocked_reason or "The required evidence or document structure is unavailable."
        return {
            "synthesis": (
                "This question cannot be answered from the current local knowledge base. "
                f"Reason: {reason}"
            ),
            "synthesis_mode": "blocked",
            "synthesis_status": "blocked",
            "synthesis_model": None,
            "synthesis_blocked_reason": reason,
            "synthesis_usage": None,
        }

    return None


def _citation_marker(source: str, page: Any) -> str:
    if not source:
        return ""
    if page is None:
        return f" [source: {source}]"
    return f" [source: {source}, page {page}]"
