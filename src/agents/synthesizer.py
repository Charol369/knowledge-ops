"""Synthesizer：证据整合节点。

职责：
- 对每个子任务返回的 evidence 做归纳
- 形成中间结论，而不是直接输出华丽答案
- 将结构化 synthesis 交给 reporter
"""
from typing import Any


class Synthesizer:
    def synthesize(self, evidence: list[dict]) -> str:
        raise NotImplementedError


def synthesizer_node(state: dict[str, Any]) -> dict[str, Any]:
    # TODO Sprint 3: 按子任务聚合 evidence -> synthesis
    raise NotImplementedError
