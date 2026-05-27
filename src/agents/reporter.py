"""Reporter：最终回答 / 报告生成节点。"""
from typing import Any


class Reporter:
    def render(self, question: str, synthesis: str) -> str:
        return (
            f"Question: {question}\n\n"
            "Answer grounded in local evidence:\n"
            f"{synthesis}"
        )


def reporter_node(state: dict[str, Any]) -> dict[str, Any]:
    answer = Reporter().render(state["question"], state.get("synthesis", ""))
    return {**state, "answer": answer, "needs_human_review": False}
