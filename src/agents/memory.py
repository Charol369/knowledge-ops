"""Memory / Artifact 持久化入口。

旧骨架只强调对话级 checkpointer；
新架构要求同时支持：
- LangGraph 会话状态持久化
- 研究中间产物（plan / evidence / report）持久化
"""
from langgraph.checkpoint.memory import MemorySaver


def get_checkpointer():
    """统一的 graph checkpointer 入口。"""
    return MemorySaver()


# TODO Sprint 3: thread_id 隔离不同用户会话
# TODO Sprint 4: 切 PostgresSaver，配合 docker-compose 的 postgres 复用
# TODO Sprint 1-3: 将 artifact store 与 checkpointer 解耦，不把中间产物都塞进 graph state
