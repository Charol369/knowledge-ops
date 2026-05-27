"""Synthesizer：证据整合节点。

职责：
- 对每个子任务返回的 evidence 做归纳
- 形成中间结论，而不是直接输出华丽答案
- 将结构化 synthesis 交给 reporter
"""
from typing import Any


class Synthesizer:
    def synthesize(self, evidence: list[dict]) -> str:
        if not evidence:
            return "No local evidence was retrieved, so no grounded synthesis is available."
        lines = []
        for index, item in enumerate(evidence, start=1):
            source = item.get("source", "unknown source")
            page = item.get("page")
            content = str(item.get("content", "")).strip()
            citation = f"{source}, page {page}" if page is not None else source
            lines.append(f"{index}. {content} [source: {citation}]")
        return "\n".join(lines)


def synthesizer_node(state: dict[str, Any]) -> dict[str, Any]:
    synthesis = Synthesizer().synthesize(state.get("evidence", []))
    execution_path = [*state.get("execution_path", []), "synthesizer"]
    return {**state, "synthesis": synthesis, "execution_path": execution_path}
