"""LangGraph 主图：编排 QA / Summary / Report 三 Agent（Supervisor 模式）

架构（详见 docs/architecture.md）：

  START → supervisor → (intent=qa)      → qa_agent      → END
                    → (intent=summary)  → summary_agent → END
                    → (intent=report)   → report_agent  → END

Sprint 3 任务。Day5 03_supervisor.py 已经做过简化版（math/story），这里是扩展版。
"""
from typing import TypedDict, Literal


class AgentState(TypedDict):
    """图的共享内存"""
    question: str            # 用户原始问题
    intent: str              # supervisor 决定的路由（qa / summary / report）
    context: list[str]       # 检索到的 chunks
    answer: str              # 最终答案
    citations: list[dict]    # 引用来源 [{source, page, snippet}]


def build_graph():
    """构建并编译 LangGraph"""
    # TODO Sprint 3:
    #   from langgraph.graph import StateGraph, START, END
    #   graph = StateGraph(AgentState)
    #   graph.add_node("supervisor", supervisor)
    #   graph.add_node("qa_agent", qa_agent)
    #   ...
    #   graph.add_conditional_edges("supervisor", route)
    #   return graph.compile(checkpointer=MemorySaver())  # 加 checkpointer 支持 HITL
    raise NotImplementedError


def route(state: AgentState) -> Literal["qa_agent", "summary_agent", "report_agent"]:
    """根据 supervisor 决定的 intent 选下一个节点"""
    return f"{state['intent']}_agent"  # type: ignore
