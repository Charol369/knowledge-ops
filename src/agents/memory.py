"""Memory / Artifact 持久化入口。

Sprint 4 提供 PostgresSaver 的可选边界，但本地默认仍使用 MemorySaver。
缺少 DSN、可选依赖或真实数据库服务时，不阻塞本地验收。
"""
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from langgraph.checkpoint.memory import MemorySaver

from src.config import settings


@dataclass(frozen=True)
class CheckpointerStatus:
    backend: str
    configured: bool
    active: bool
    pending_reason: str | None = None
    blocked_reason: str | None = None


PostgresSaverFactory = Callable[[str], Any]


def get_checkpointer(
    postgres_saver_factory: PostgresSaverFactory | None = None,
) -> Any:
    """统一的 graph checkpointer 入口。"""
    checkpointer, _ = _resolve_checkpointer(postgres_saver_factory)
    return checkpointer


def get_checkpointer_status(
    postgres_saver_factory: PostgresSaverFactory | None = None,
) -> CheckpointerStatus:
    """Return the selected checkpoint backend without requiring external services."""
    _, status = _resolve_checkpointer(postgres_saver_factory)
    return status


def _resolve_checkpointer(
    postgres_saver_factory: PostgresSaverFactory | None,
) -> tuple[Any, CheckpointerStatus]:
    dsn = settings.postgres_saver_dsn.strip()
    if not dsn:
        return MemorySaver(), CheckpointerStatus(
            backend="memory",
            configured=False,
            active=True,
            pending_reason=(
                "PostgresSaver disabled: no postgres_saver_dsn configured; using MemorySaver."
            ),
        )

    if postgres_saver_factory is None:
        return MemorySaver(), CheckpointerStatus(
            backend="memory",
            configured=True,
            active=True,
            blocked_reason=(
                "PostgresSaver configured but no local factory/dependency is available; "
                "using MemorySaver fallback."
            ),
        )

    try:
        return postgres_saver_factory(dsn), CheckpointerStatus(
            backend="postgres",
            configured=True,
            active=True,
        )
    except Exception as exc:
        return MemorySaver(), CheckpointerStatus(
            backend="memory",
            configured=True,
            active=True,
            blocked_reason=(
                f"PostgresSaver configured but unavailable: {exc}; "
                "using MemorySaver fallback."
            ),
        )
