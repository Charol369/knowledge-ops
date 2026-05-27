"""Reporter：最终回答 / 报告生成节点。"""
from typing import Any


class Reporter:
    def render(self, question: str, synthesis: str) -> str:
        raise NotImplementedError


def reporter_node(state: dict[str, Any]) -> dict[str, Any]:
    # TODO Sprint 3: 输出 answer + citations + needs_human_review
    raise NotImplementedError
