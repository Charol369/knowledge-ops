"""Langfuse 初始化（LLMOps 追踪支柱）。

本模块必须 dry-run safe：缺少显式本地配置时不构造真实 Handler，不触发认证
或网络相关错误。真实 Langfuse 只作为可选配置路径。
"""
from collections.abc import Callable
import hashlib
import os
import re
from typing import Any

from src.config import settings


_W3C_TRACE_ID_RE = re.compile(r"^[0-9a-f]{32}$")


def to_langfuse_trace_id(trace_id: str) -> str:
    """Map application trace IDs to Langfuse/W3C-compatible trace IDs."""
    normalized = trace_id.strip().lower()
    if _W3C_TRACE_ID_RE.fullmatch(normalized) and set(normalized) != {"0"}:
        return normalized

    try:
        from langfuse import Langfuse

        generated = str(Langfuse.create_trace_id(seed=trace_id)).strip().lower()
        if _W3C_TRACE_ID_RE.fullmatch(generated) and set(generated) != {"0"}:
            return generated
    except Exception:
        pass
    return hashlib.sha256(trace_id.encode("utf-8")).hexdigest()[:32]


def get_langfuse_handler(
    trace_id: str | None = None,
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

        if trace_id:
            return CallbackHandler(
                trace_context={"trace_id": to_langfuse_trace_id(trace_id)}
            )
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
            "trace_id": to_langfuse_trace_id(trace_id),
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
