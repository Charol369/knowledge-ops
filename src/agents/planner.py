"""Planner：研究型 Agent 的第一认知节点。

职责：
- 判断问题是否需要 research
- 生成 2-4 个可执行子任务
- 预估复杂度，供后续 model router 使用
"""
from typing import Any


class ResearchPlanner:
    def needs_research(self, question: str) -> bool:
        normalized = question.strip().lower()
        if not normalized:
            return False
        simple_prompts = {"hi", "hello", "你好", "thanks", "谢谢"}
        return normalized not in simple_prompts

    def plan(self, question: str) -> list[str]:
        if not self.needs_research(question):
            return [
                "Clarify the user request.",
                "Provide a concise answer without external research.",
            ]
        return [
            f"Identify local evidence relevant to: {question}",
            "Retrieve the top local evidence chunks with source metadata.",
            "Synthesize an answer grounded only in retrieved evidence.",
        ]


def planner_node(state: dict[str, Any]) -> dict[str, Any]:
    planner = ResearchPlanner()
    question = state["question"]
    plan = planner.plan(question)
    return {
        **state,
        "plan": plan,
        "requires_research": planner.needs_research(question),
        "complexity": "standard" if planner.needs_research(question) else "simple",
    }
