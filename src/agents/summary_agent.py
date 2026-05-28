"""Summary Agent：把检索到的多个 chunks 总结成结构化摘要

Sprint 3 任务。

输入：多个 chunks（可能跨文档）
输出：结构化摘要（标题 + 3-5 个要点 + 矛盾点标注）
"""
from src.agents.graph import AgentState
from src.agents.synthesizer import Synthesizer


SUMMARY_SYSTEM_PROMPT = """你是会议纪要 / 资料整理专家。
把以下材料整理成结构化摘要：
- 标题（一句话）
- 3-5 个要点（按重要性排序）
- 矛盾或不确定的地方单独标 ⚠️
保持客观，不加未在材料中出现的信息。
"""


def summary_agent(state: AgentState) -> dict:
    """Compatibility entrypoint that reuses the deterministic synthesizer."""
    evidence = state.get("evidence") or state.get("context", {}).get("evidence", [])
    synthesis = Synthesizer().synthesize(evidence)
    execution_path = [*state.get("execution_path", []), "summary_agent"]
    return {**state, "synthesis": synthesis, "execution_path": execution_path}
