"""本地业务指标记录。

Sprint 4 只提供可测试的 dry-run 指标层，不依赖 OpenTelemetry、Redis、
Prometheus 或其他外部服务。后续生产后端可以在这个接口后面替换实现。
"""
from collections import Counter
from copy import deepcopy
from typing import Any


class BusinessMetricsRecorder:
    """In-memory metrics collector for local Sprint 4 acceptance."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._complexity_counts: Counter[str] = Counter()
        self._model_tier_counts: Counter[str] = Counter()
        self._fallback_tier_counts: Counter[str] = Counter()
        self._guardrail_level_counts: Counter[str] = Counter()
        self._policy_decisions_total = 0
        self._cache_hits_total = 0
        self._fallbacks_total = 0
        self._retryable_fallbacks_total = 0
        self._guardrail_decisions_total = 0
        self._guardrail_injections_total = 0
        self._guardrail_blocked_total = 0
        self._citation_verifications_total = 0
        self._citation_verified_total = 0
        self._human_review_total = 0
        self._trace_ids: list[str] = []
        self._events: list[dict[str, Any]] = []

    def record_policy_decision(
        self,
        *,
        complexity: str,
        model_tier: str,
        cache_hit: bool,
        trace_id: str | None = None,
    ) -> None:
        self._policy_decisions_total += 1
        self._complexity_counts[complexity] += 1
        self._model_tier_counts[model_tier] += 1
        if cache_hit:
            self._cache_hits_total += 1
        self._remember_trace_id(trace_id)
        self._events.append(
            {
                "type": "policy_decision",
                "complexity": complexity,
                "model_tier": model_tier,
                "cache_hit": cache_hit,
                "trace_id": trace_id,
            }
        )

    def record_fallback(
        self,
        *,
        current_tier: str,
        fallback_tier: str | None,
        retry: bool,
        trace_id: str | None = None,
    ) -> None:
        self._fallbacks_total += 1
        if retry:
            self._retryable_fallbacks_total += 1
        if fallback_tier is not None:
            self._fallback_tier_counts[f"{current_tier}->{fallback_tier}"] += 1
        self._remember_trace_id(trace_id)
        self._events.append(
            {
                "type": "fallback",
                "current_tier": current_tier,
                "fallback_tier": fallback_tier,
                "retry": retry,
                "trace_id": trace_id,
            }
        )

    def record_guardrail_decision(
        self,
        *,
        is_injection: bool,
        level: str,
        blocked: bool,
        trace_id: str | None = None,
    ) -> None:
        self._guardrail_decisions_total += 1
        self._guardrail_level_counts[level] += 1
        if is_injection:
            self._guardrail_injections_total += 1
        if blocked:
            self._guardrail_blocked_total += 1
        self._remember_trace_id(trace_id)
        self._events.append(
            {
                "type": "guardrail_decision",
                "is_injection": is_injection,
                "level": level,
                "blocked": blocked,
                "trace_id": trace_id,
            }
        )

    def record_citation_verification(
        self,
        *,
        verified: bool,
        needs_human_review: bool,
        trace_id: str | None = None,
    ) -> None:
        self._citation_verifications_total += 1
        if verified:
            self._citation_verified_total += 1
        if needs_human_review:
            self._human_review_total += 1
        self._remember_trace_id(trace_id)
        self._events.append(
            {
                "type": "citation_verification",
                "verified": verified,
                "needs_human_review": needs_human_review,
                "trace_id": trace_id,
            }
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "policy_decisions_total": self._policy_decisions_total,
            "complexity_counts": dict(self._complexity_counts),
            "model_tier_counts": dict(self._model_tier_counts),
            "cache_hits_total": self._cache_hits_total,
            "fallbacks_total": self._fallbacks_total,
            "retryable_fallbacks_total": self._retryable_fallbacks_total,
            "fallback_tier_counts": dict(self._fallback_tier_counts),
            "guardrail_decisions_total": self._guardrail_decisions_total,
            "guardrail_level_counts": dict(self._guardrail_level_counts),
            "guardrail_injections_total": self._guardrail_injections_total,
            "guardrail_blocked_total": self._guardrail_blocked_total,
            "citation_verifications_total": self._citation_verifications_total,
            "citation_verified_total": self._citation_verified_total,
            "human_review_total": self._human_review_total,
            "trace_ids": list(self._trace_ids),
            "events": deepcopy(self._events),
        }

    def _remember_trace_id(self, trace_id: str | None) -> None:
        if trace_id and trace_id not in self._trace_ids:
            self._trace_ids.append(trace_id)


business_metrics = BusinessMetricsRecorder()
