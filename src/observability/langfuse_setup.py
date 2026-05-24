"""Langfuse 初始化（LLMOps 追踪支柱）

Day6 03_langfuse_chain.py 已验证 v4 API：from langfuse.langchain import CallbackHandler，
无参构造（自动读 LANGFUSE_* 环境变量），OpenTelemetry 风格。
"""
from langfuse.langchain import CallbackHandler
from src.config import settings


def get_langfuse_handler() -> CallbackHandler | None:
    """获取 Langfuse callback handler，未配置 key 时返回 None"""
    if not (settings.langfuse_public_key and settings.langfuse_secret_key):
        return None
    return CallbackHandler()


# TODO Sprint 4: 加 trace_id 注入 → 业务接口返回给前端，方便用户"看追踪"
# TODO Sprint 4: 在请求结束时显式 flush（v4 异步上报）
