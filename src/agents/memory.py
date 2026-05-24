"""Memory 管理：LangGraph Checkpointer 持久化对话状态

LangChain 1.0 重构后 Memory 完全迁到 LangGraph 体系：
  - 0.x：RunnableWithMessageHistory（已 deprecated，Day3 跑过 warning）
  - 1.0+：langgraph.checkpoint.MemorySaver / SqliteSaver

Sprint 3 用 MemorySaver（内存），Sprint 4 切 SqliteSaver / PostgresSaver 上生产持久化。
"""
from langgraph.checkpoint.memory import MemorySaver


def get_checkpointer():
    """统一的 checkpointer 入口（W1 末用 MemorySaver，生产换 Postgres）"""
    return MemorySaver()


# TODO Sprint 3: thread_id 隔离不同用户会话
# TODO Sprint 4: 切 PostgresSaver，配合 docker-compose 的 langfuse-postgres 复用
