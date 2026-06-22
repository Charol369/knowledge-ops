"""Reporter：最终回答 / 报告生成节点。"""
from typing import Any

from src.guardrails.citation import extract_citations


class Reporter:
    def render(self, question: str, synthesis: str) -> str:
        return (
            f"Question: {question}\n\n"
            "Answer grounded in local evidence:\n"
            f"{synthesis}"
        )


def reporter_node(state: dict[str, Any]) -> dict[str, Any]:
    answer = Reporter().render(state["question"], state.get("synthesis", ""))
    answer = _enforce_tool_answer_constraints(answer, state)
    evidence = state.get("context", {}).get("evidence", state.get("evidence", []))
    execution_path = [*state.get("execution_path", []), "reporter"]
    return {
        **state,
        "answer": answer,
        "citations": extract_citations(answer, evidence=evidence),
        "needs_human_review": False,
        "execution_path": execution_path,
    }


def _enforce_tool_answer_constraints(answer: str, state: dict[str, Any]) -> str:
    tool_result = state.get("tool_result") or {}
    if state.get("strategy") == "reference_count" and state.get("tool_status") == "ok":
        count = tool_result.get("count")
        if count is not None and str(count) not in answer:
            source = str(tool_result.get("source") or "local knowledge base").replace("\\", "/")
            page = tool_result.get("page_start")
            citation = _citation_marker(source, page)
            return Reporter().render(
                state["question"],
                (
                    f"The references section contains {count} entries according to the "
                    f"deterministic reference count tool.{citation}"
                ),
            )

    if state.get("tool_status") == "blocked" or state.get("strategy") == "blocked":
        blocked_reason = (
            state.get("fallback_reason")
            or state.get("blocked_reason")
            or tool_result.get("blocked_reason")
            or "The required evidence or document structure is unavailable."
        )
        if "cannot be answered" not in answer.lower():
            return Reporter().render(
                state["question"],
                (
                    "This question cannot be answered from the current local knowledge base. "
                    f"Reason: {blocked_reason}"
                ),
            )
    return answer


def _citation_marker(source: str, page: Any) -> str:
    if not source:
        return ""
    if page is None:
        return f" [source: {source}]"
    return f" [source: {source}, page {page}]"
