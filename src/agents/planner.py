"""Planner：研究型 Agent 的第一认知节点。

职责：
- 判断问题是否需要 research
- 生成 2-5 个可执行子任务
- 预估复杂度，供后续 model router 使用
"""
from typing import Any


class ResearchPlanner:
    def plan(self, question: str) -> list[str]:
        raise NotImplementedError


def planner_node(state: dict[str, Any]) -> dict[str, Any]:
    # TODO Sprint 1: 最小 planner
    # TODO Sprint 3: 升级为 Plan-and-Solve 主线节点
    raise NotImplementedError
