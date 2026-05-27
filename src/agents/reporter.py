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
    execution_path = [*state.get("execution_path", []), "reporter"]
    return {
        **state,
        "answer": answer,
        "citations": extract_citations(answer),
        "needs_human_review": False,
        "execution_path": execution_path,
    }
