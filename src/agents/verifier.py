"""Verifier / Reflection：高价值请求的选择性校验节点。"""
from typing import Any

from pydantic import ValidationError

from src.guardrails.citation import verify_citations
from src.guardrails.output_schema import Answer
from src.observability.metrics import business_metrics


class Verifier:
    def verify(
        self,
        answer: str,
        citations: list[dict],
        evidence: list[dict] | None = None,
    ) -> dict[str, Any]:
        if not citations:
            return {
                "status": "needs_human_review",
                "confidence": 0.0,
                "invalid_citations": ["<missing-citations>"],
                "needs_human_review": True,
            }

        citations_valid, invalid = verify_citations(citations, evidence or [])
        confidence = 0.85 if citations_valid else 0.2
        try:
            structured = Answer(
                answer=answer,
                confidence=confidence,
                citations=citations,
                needs_human_review=not citations_valid,
            )
        except ValidationError as exc:
            return {
                "status": "validation_failed",
                "confidence": 0.0,
                "invalid_citations": invalid,
                "needs_human_review": True,
                "validation_error": str(exc),
            }

        return {
            "status": "ok" if citations_valid else "unsupported_citations",
            "confidence": confidence,
            "invalid_citations": invalid,
            "needs_human_review": not citations_valid,
            "structured_answer": structured.model_dump(),
        }


def verifier_node(state: dict[str, Any]) -> dict[str, Any]:
    verification = Verifier().verify(
        answer=state.get("answer", ""),
        citations=state.get("citations", []),
        evidence=state.get("context", {}).get("evidence", state.get("evidence", [])),
    )
    if state.get("tool_status") == "blocked" or state.get("strategy") == "blocked":
        verification = {
            **verification,
            "status": "blocked",
            "confidence": 0.0,
            "needs_human_review": True,
            "blocked_reason": state.get("fallback_reason") or state.get("blocked_reason"),
        }
    business_metrics.record_citation_verification(
        verified=verification.get("status") == "ok",
        needs_human_review=bool(verification.get("needs_human_review", True)),
        trace_id=state.get("trace_id"),
    )
    execution_path = [*state.get("execution_path", []), "verifier"]
    return {
        **state,
        "verification": verification,
        "confidence": verification.get("confidence", 0.0),
        "needs_human_review": verification.get("needs_human_review", True),
        "structured_answer": verification.get("structured_answer"),
        "execution_path": execution_path,
    }
