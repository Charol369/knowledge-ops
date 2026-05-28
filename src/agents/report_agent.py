"""Report Agent：基于检索结果生成结构化技术报告（Markdown 格式）

Sprint 3 任务。

输出格式：
  # 报告标题
  ## 1. 背景
  ## 2. 关键发现（带 [来源: X] 引用编号）
  ## 3. 结论
  ## 参考文献（编号列表）
"""
from src.agents.graph import AgentState
from src.agents.reporter import Reporter
from src.agents.synthesizer import Synthesizer
from src.guardrails.citation import extract_citations


REPORT_SYSTEM_PROMPT = """你是技术报告作者。
基于提供的材料，输出 Markdown 格式报告：
- 标题、背景、关键发现、结论、参考文献 5 节
- 每个事实必须附 [来源: 编号] 引用
- 报告全长控制在 800-1500 字
"""


def report_agent(state: AgentState) -> dict:
    """Compatibility entrypoint that renders the existing synthesis as a report."""
    evidence = state.get("evidence") or state.get("context", {}).get("evidence", [])
    synthesis = state.get("synthesis") or Synthesizer().synthesize(evidence)
    answer = Reporter().render(state.get("question", ""), synthesis)
    execution_path = [*state.get("execution_path", []), "report_agent"]
    return {
        **state,
        "synthesis": synthesis,
        "answer": answer,
        "citations": extract_citations(answer),
        "execution_path": execution_path,
    }
