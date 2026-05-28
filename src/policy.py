"""Policy Layer：复杂度判定、模型路由、回退策略。

这是项目从“技术 demo”升级为“生产导向系统”的关键一层。
"""
from collections.abc import Callable
from dataclasses import dataclass
import time
from typing import Any, Literal


Complexity = Literal["simple", "standard", "complex"]
ModelTier = Literal["tier0", "tier1", "tier2", "tier3"]


class ComplexityClassifier:
    """Deterministic local complexity classifier.

    The classifier intentionally uses transparent heuristics instead of LLM calls so
    Sprint 4 policy tests never require paid model access.
    """

    _SIMPLE_PROMPTS = {"hi", "hello", "hey", "你好", "谢谢", "thanks", "thank you"}
    _COMPLEX_MARKERS = {
        "analyze",
        "analysis",
        "compare",
        "tradeoff",
        "tradeoffs",
        "multiple",
        "multi",
        "across",
        "report",
        "executive",
        "strategy",
        "evaluate",
        "benchmark",
        "summarize all",
        "综合",
        "对比",
        "分析",
        "报告",
        "多文档",
    }

    def classify(self, question: str) -> Complexity:
        normalized = " ".join(question.strip().lower().split())
        if not normalized:
            return "simple"
        if normalized in self._SIMPLE_PROMPTS:
            return "simple"
        if any(marker in normalized for marker in self._COMPLEX_MARKERS):
            return "complex"
        if len(normalized) > 240 or normalized.count("?") + normalized.count("？") >= 2:
            return "complex"
        return "standard"


class ModelRouter:
    """Route local policy complexity labels to abstract model tiers."""

    _ROUTES: dict[Complexity, ModelTier] = {
        "simple": "tier1",
        "standard": "tier2",
        "complex": "tier3",
    }

    def route(self, complexity: Complexity) -> ModelTier:
        return self._ROUTES[complexity]


class FallbackPolicy:
    """Deterministic retry/fallback rules for local Sprint 4 acceptance."""

    _TRANSIENT_MARKERS = {
        "timeout",
        "timed out",
        "temporarily",
        "temporary",
        "transient",
        "connection reset",
        "connection aborted",
        "rate limit",
        "too many requests",
        "429",
        "500",
        "502",
        "503",
        "504",
        "unavailable",
    }
    _PERMANENT_MARKERS = {
        "401",
        "403",
        "unauthorized",
        "forbidden",
        "invalid api key",
        "invalid key",
        "permission denied",
        "validation",
        "permanent",
        "not found",
        "404",
    }

    def should_retry(self, error_message: str) -> bool:
        normalized = error_message.lower()
        if any(marker in normalized for marker in self._PERMANENT_MARKERS):
            return False
        return any(marker in normalized for marker in self._TRANSIENT_MARKERS)

    def fallback_tier(self, current_tier: ModelTier) -> ModelTier | None:
        fallback_map: dict[ModelTier, ModelTier | None] = {
            "tier3": "tier2",
            "tier2": "tier1",
            "tier1": None,
            "tier0": None,
        }
        return fallback_map[current_tier]


@dataclass(frozen=True)
class PolicyDecision:
    complexity: Complexity
    model_tier: ModelTier
    cache_hit: bool = False
    fallback_tier: ModelTier | None = None


class LocalResponseCache:
    """Small in-memory TTL cache used only for local deterministic behavior."""

    def __init__(
        self,
        ttl_seconds: int = 3600,
        clock: Callable[[], float] | None = None,
    ):
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive.")
        self.ttl_seconds = ttl_seconds
        self.clock = clock or time.time
        self._items: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        item = self._items.get(key)
        if item is None:
            return None
        expires_at, value = item
        if self.clock() >= expires_at:
            self._items.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._items[key] = (self.clock() + self.ttl_seconds, value)

    def clear(self) -> None:
        self._items.clear()


def decide_policy(question: str, cache_hit: bool = False) -> PolicyDecision:
    classifier = ComplexityClassifier()
    router = ModelRouter()
    complexity = classifier.classify(question)
    tier: ModelTier = "tier0" if cache_hit else router.route(complexity)
    return PolicyDecision(complexity=complexity, model_tier=tier, cache_hit=cache_hit)
