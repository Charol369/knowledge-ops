"""Retrieval Orchestrator：编排确定性检索服务。

职责：
- 调 retrieval services，而不是自己“自由发挥”地检索
- 在必要时局部采用 ReAct：重写 query、补检索、分解子问题
- 为 synthesizer 提供干净的 evidence 集合
"""
from typing import Any


class RetrievalOrchestrator:
    def gather_evidence(self, question: str, plan: list[str]) -> list[dict]:
        raise NotImplementedError


def retrieval_orchestrator_node(state: dict[str, Any]) -> dict[str, Any]:
    # TODO Sprint 3: 接 query_transform + dense/sparse/hybrid/rerank + context_builder
    raise NotImplementedError
