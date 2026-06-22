"""Deterministic intent routing for product QA requests."""
from __future__ import annotations

import re
from dataclasses import dataclass


ALLOWED_INTENTS = {
    "definition",
    "section_summary",
    "count",
    "list",
    "compare",
    "table_query",
    "no_answer",
    "unknown",
}

INTENT_STRATEGY = {
    "definition": "hybrid_retrieval",
    "section_summary": "section_lookup",
    "count": "reference_count",
    "list": "targeted_retrieval",
    "compare": "hybrid_retrieval",
    "table_query": "table_lookup",
    "no_answer": "blocked",
    "unknown": "hybrid_retrieval",
}


@dataclass(frozen=True)
class QueryIntentResult:
    intent: str
    strategy: str
    confidence: float
    normalized_question: str
    tool_name: str | None = None
    route_reason: str | None = None
    target: str | None = None

    def as_state_update(self) -> dict[str, object]:
        return {
            "intent": self.intent,
            "strategy": self.strategy,
            "intent_confidence": self.confidence,
            "route_reason": self.route_reason,
            "tool_name": self.tool_name,
            "normalized_question": self.normalized_question,
        }


def classify_query_intent(
    question: str,
    requested_intent: str | None = None,
) -> QueryIntentResult:
    normalized = _normalize(question)
    requested = (requested_intent or "").strip().lower()
    if requested in ALLOWED_INTENTS:
        return _result(
            intent=requested,
            normalized_question=normalized,
            confidence=0.99,
            route_reason="caller_requested_intent",
        )

    if _matches_no_answer(normalized):
        return _result(
            intent="no_answer",
            normalized_question=normalized,
            confidence=0.86,
            route_reason="private_or_unsupported_information_pattern",
        )

    section_target = _extract_section_target(normalized)
    if section_target:
        return _result(
            intent="section_summary",
            normalized_question=normalized,
            confidence=0.9,
            route_reason="section_pattern",
            target=section_target,
        )

    if re.search(r"\btable\s+\d+[a-z]?\b", normalized) or "表 " in normalized:
        return _result(
            intent="table_query",
            normalized_question=normalized,
            confidence=0.9,
            route_reason="table_pattern",
            target=_extract_table_target(normalized),
        )

    if _matches_reference_count(normalized):
        return _result(
            intent="count",
            normalized_question=normalized,
            confidence=0.9,
            route_reason="reference_count_pattern",
            target="references",
        )

    if _starts_with_any(normalized, ("list ", "列出", "列举")) or re.search(r"\bwhich\b", normalized):
        return _result(
            intent="list",
            normalized_question=normalized,
            confidence=0.78,
            route_reason="list_pattern",
        )

    if re.search(r"\b(compare|versus|vs\.?|difference between|differences between)\b", normalized) or "比较" in normalized:
        return _result(
            intent="compare",
            normalized_question=normalized,
            confidence=0.78,
            route_reason="compare_pattern",
        )

    if _starts_with_any(normalized, ("what is", "what are", "define ", "explain ", "describe ", "什么是", "解释")):
        return _result(
            intent="definition",
            normalized_question=normalized,
            confidence=0.82,
            route_reason="definition_pattern",
        )

    return _result(
        intent="unknown",
        normalized_question=normalized,
        confidence=0.5,
        route_reason="default_unknown",
    )


def intent_router_node(state: dict) -> dict:
    result = classify_query_intent(
        str(state.get("question", "")),
        requested_intent=state.get("requested_intent") or state.get("intent"),
    )
    execution_path = [*state.get("execution_path", []), "intent_router"]
    return {
        **state,
        **result.as_state_update(),
        "intent_target": result.target,
        "execution_path": execution_path,
    }


def _result(
    *,
    intent: str,
    normalized_question: str,
    confidence: float,
    route_reason: str,
    target: str | None = None,
) -> QueryIntentResult:
    strategy = INTENT_STRATEGY[intent]
    return QueryIntentResult(
        intent=intent,
        strategy=strategy,
        confidence=confidence,
        normalized_question=normalized_question,
        tool_name=_tool_for_strategy(strategy),
        route_reason=route_reason,
        target=target,
    )


def _tool_for_strategy(strategy: str) -> str | None:
    if strategy == "reference_count":
        return "reference_count_tool"
    if strategy == "section_lookup":
        return "section_lookup_tool"
    if strategy == "table_lookup":
        return "table_lookup_tool"
    return None


def _normalize(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def _starts_with_any(text: str, prefixes: tuple[str, ...]) -> bool:
    return any(text.startswith(prefix) for prefix in prefixes)


def _matches_reference_count(text: str) -> bool:
    count_signal = re.search(r"\b(how many|number of|count)\b", text) or "多少" in text
    reference_signal = re.search(r"\b(references|reference|citations|citation|bibliography)\b", text)
    return bool(count_signal and reference_signal)


def _extract_section_target(text: str) -> str | None:
    match = re.search(r"\bsection\s+(\d+(?:\.\d+)*)\b", text)
    if match:
        return match.group(1)
    match = re.search(r"\b(?:summarize|summary of)\s+(\d+(?:\.\d+)*)\b", text)
    if match:
        return match.group(1)
    return None


def _extract_table_target(text: str) -> str | None:
    match = re.search(r"\btable\s+(\d+[a-z]?)\b", text)
    return match.group(1) if match else None


def _matches_no_answer(text: str) -> bool:
    blocked_terms = (
        "private salary",
        "personal salary",
        "password",
        "secret key",
        "api key",
        "home address",
        "social security",
    )
    return any(term in text for term in blocked_terms)

