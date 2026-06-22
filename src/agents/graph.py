"""LangGraph 主图：生产导向研究型 Knowledge Agent 骨架。

这份骨架明确贯彻新的项目原则：
1. 认知链路 Agent 化：planner / retrieval_orchestrator / synthesizer / reporter / verifier
2. 执行链路服务化：ingest / retrieval / rerank / citation / eval 不塞进 Agent 自由推理
3. 成本策略前置：state 中显式追踪 complexity / model_tier / requires_reflection

当前阶段先把图结构和状态模式固定下来，具体业务逻辑按 Sprint 1-4 逐步填充。
"""
from pathlib import Path
from typing import Any, Literal, TypedDict
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from src.agents.memory import get_checkpointer
from src.agents.orchestrator import retrieval_orchestrator_node
from src.agents.planner import planner_node
from src.agents.reporter import reporter_node
from src.agents.synthesizer import synthesizer_node
from src.agents.verifier import verifier_node
from src.config import settings
from src.observability.langfuse_setup import get_langfuse_handler
from src.retrieval.artifact_store import ArtifactStore


class AgentState(TypedDict):
    question: str
    intent: str | None
    complexity: str | None
    model_tier: str | None
    plan: list[str]
    context: dict[str, Any]
    evidence: list[dict]
    synthesis: str
    synthesis_mode: str | None
    synthesis_status: str | None
    synthesis_model: str | None
    synthesis_blocked_reason: str | None
    synthesis_usage: dict[str, Any] | None
    answer: str
    citations: list[dict]
    confidence: float
    structured_answer: dict | None
    verification: dict
    artifact_session_id: str | None
    trace_id: str | None
    requires_reflection: bool
    needs_human_review: bool
    execution_path: list[str]
    blocked_reason: str | None
    docs_dir: str
    index_dir: str
    embedding_backend: str
    top_k: int
    artifact_context: dict[str, Any] | None


def route_after_reporter(state: AgentState) -> Literal["verifier", "finish"]:
    return "verifier"


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

    return graph.compile(checkpointer=get_checkpointer())


def _graph_invoke_config(trace_id: str) -> dict[str, Any]:
    config: dict[str, Any] = {"configurable": {"thread_id": trace_id}}
    handler = get_langfuse_handler(trace_id=trace_id)
    if handler is not None:
        config["callbacks"] = [handler]
    return config


def run_research_graph(
    question: str,
    thread_id: str | None = None,
    docs_dir: str | Path = "data",
    index_dir: str | Path = "data/faiss/sprint1",
    artifact_root: str | Path | None = None,
    evidence: list[dict] | None = None,
    embedding_backend: str = "hash",
) -> dict[str, Any]:
    """Run the Sprint 3 graph locally with MemorySaver checkpointing."""
    trace_id = thread_id or uuid4().hex
    store = ArtifactStore(root_dir=artifact_root or settings.artifact_root_dir)
    session_id = store.create_session(question)
    initial_state: dict[str, Any] = {
        "question": question,
        "intent": None,
        "complexity": None,
        "model_tier": "tier2",
        "plan": [],
        "context": {},
        "evidence": list(evidence or []),
        "synthesis": "",
        "synthesis_mode": None,
        "synthesis_status": None,
        "synthesis_model": None,
        "synthesis_blocked_reason": None,
        "synthesis_usage": None,
        "answer": "",
        "citations": [],
        "confidence": 0.0,
        "structured_answer": None,
        "verification": {},
        "artifact_session_id": session_id,
        "trace_id": trace_id,
        "requires_reflection": True,
        "needs_human_review": False,
        "execution_path": [],
        "blocked_reason": None,
        "docs_dir": str(docs_dir),
        "index_dir": str(index_dir),
        "embedding_backend": embedding_backend,
        "top_k": settings.top_k_final,
        "artifact_context": None,
    }
    result = build_graph().invoke(
        initial_state,
        config=_graph_invoke_config(trace_id),
    )
    store.save_plan(session_id, result.get("plan", []))
    store.save_evidence(session_id, result.get("evidence", []))
    store.save_final_answer(session_id, result.get("answer", ""))
    result["artifact_session_id"] = session_id
    result["trace_id"] = trace_id
    return result
