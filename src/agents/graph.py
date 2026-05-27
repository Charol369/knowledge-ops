"""LangGraph 主图：生产导向研究型 Knowledge Agent 骨架。

这份骨架明确贯彻新的项目原则：
1. 认知链路 Agent 化：planner / retrieval_orchestrator / synthesizer / reporter / verifier
2. 执行链路服务化：ingest / retrieval / rerank / citation / eval 不塞进 Agent 自由推理
3. 成本策略前置：state 中显式追踪 complexity / model_tier / requires_reflection

当前阶段先把图结构和状态模式固定下来，具体业务逻辑按 Sprint 1-4 逐步填充。
"""
from typing import Literal, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.agents.orchestrator import retrieval_orchestrator_node
from src.agents.planner import planner_node
from src.agents.reporter import reporter_node
from src.agents.synthesizer import synthesizer_node
from src.agents.verifier import verifier_node


class AgentState(TypedDict):
    question: str
    intent: str | None
    complexity: str | None
    model_tier: str | None
    plan: list[str]
    context: list[str]
    evidence: list[dict]
    synthesis: str
    answer: str
    citations: list[dict]
    artifact_session_id: str | None
    trace_id: str | None
    requires_reflection: bool
    needs_human_review: bool


def route_after_reporter(state: AgentState) -> Literal["verifier", "finish"]:
    if state["requires_reflection"]:
        return "verifier"
    return "finish"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("retrieval_orchestrator", retrieval_orchestrator_node)
    graph.add_node("synthesizer", synthesizer_node)
    graph.add_node("reporter", reporter_node)
    graph.add_node("verifier", verifier_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "retrieval_orchestrator")
    graph.add_edge("retrieval_orchestrator", "synthesizer")
    graph.add_edge("synthesizer", "reporter")
    graph.add_conditional_edges(
        "reporter",
        route_after_reporter,
        {
            "verifier": "verifier",
            "finish": END,
        },
    )
    graph.add_edge("verifier", END)

    return graph.compile(checkpointer=MemorySaver())
