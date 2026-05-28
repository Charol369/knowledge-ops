"""Langfuse 初始化（LLMOps 追踪支柱）。

本模块必须 dry-run safe：缺少显式本地配置时不构造真实 Handler，不触发认证
或网络相关错误。真实 Langfuse 只作为可选配置路径。
"""
from collections.abc import Callable
import os
from typing import Any

from src.config import settings


def get_langfuse_handler(
    handler_factory: Callable[[], Any] | None = None,
) -> Any | None:
    """Return a Langfuse callback handler only when explicitly configured."""
    if not settings.langfuse_enabled:
        return None
    if not (settings.langfuse_public_key and settings.langfuse_secret_key):
        return None

    try:
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key
        os.environ["LANGFUSE_HOST"] = settings.langfuse_host
        if handler_factory is not None:
            return handler_factory()
        from langfuse.langchain import CallbackHandler

        return CallbackHandler()
    except Exception:
        return None


def record_langfuse_score(
    *,
    trace_id: str,
    score: float,
    name: str = "user_feedback",
    comment: str | None = None,
    client_factory: Callable[[], Any] | None = None,
) -> dict[str, str | None]:
    """Submit a Langfuse-compatible score only when safely configured."""
    if not settings.langfuse_enabled:
        return {"status": "disabled", "blocked_reason": None}
    if not (settings.langfuse_public_key and settings.langfuse_secret_key):
        return {
            "status": "config_error",
            "blocked_reason": "Langfuse feedback is enabled but public/secret keys are incomplete.",
        }

    try:
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key
        os.environ["LANGFUSE_HOST"] = settings.langfuse_host
        if client_factory is not None:
            client = client_factory()
        else:
            from langfuse import Langfuse

            client = Langfuse(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                host=settings.langfuse_host,
            )
        score_kwargs: dict[str, Any] = {
            "trace_id": trace_id,
            "name": name,
            "value": float(score),
        }
        if comment:
            score_kwargs["comment"] = comment
        client.create_score(**score_kwargs)
        flush = getattr(client, "flush", None)
        if callable(flush):
            flush()
        return {"status": "recorded", "blocked_reason": None}
    except Exception as exc:
        return {
            "status": "error",
            "blocked_reason": f"Langfuse feedback score failed locally: {exc}",
        }
