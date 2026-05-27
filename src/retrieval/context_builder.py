"""Context Builder：把检索结果和 artifact 组织成可引用上下文。"""
import json
from pathlib import Path
from typing import Any


def _evidence_score(item: dict[str, Any]) -> float:
    for key in ("rerank_score", "rrf_score", "score"):
        if key in item and item[key] is not None:
            return float(item[key])
    return 0.0


def _dedupe_key(item: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(item.get("source", "")),
        str(item.get("page", "")),
        str(item.get("content", "")).strip(),
    )


def _citation(source: str, page: Any) -> str:
    if page is None or page == "":
        return source
    return f"{source} p.{page}"


class ContextBuilder:
    def __init__(self, max_evidence_items: int = 8, max_context_chars: int = 4000):
        self.max_evidence_items = max_evidence_items
        self.max_context_chars = max_context_chars

    def build(
        self,
        question: str,
        evidence: list[dict],
        focus_recap: str | None = None,
        artifact_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ordered_evidence = self._select_evidence(evidence)
        artifact_text = self._format_artifact_context(artifact_context)
        context = self._format_context(ordered_evidence, focus_recap, artifact_text)
        return {
            "question": question,
            "focus_recap": focus_recap,
            "artifact_context": artifact_text,
            "evidence": ordered_evidence,
            "context": context,
        }

    def _select_evidence(self, evidence: list[dict]) -> list[dict[str, Any]]:
        ranked = sorted(
            evidence,
            key=lambda item: _evidence_score(item),
            reverse=True,
        )
        selected: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str]] = set()
        for item in ranked:
            if not item.get("source"):
                raise ValueError("Context evidence must include source metadata.")
            key = _dedupe_key(item)
            if key in seen:
                continue
            seen.add(key)
            selected.append(dict(item))
            if len(selected) >= self.max_evidence_items:
                break
        return selected

    def _format_context(
        self,
        evidence: list[dict[str, Any]],
        focus_recap: str | None,
        artifact_text: str,
    ) -> str:
        lines: list[str] = []
        if focus_recap:
            lines.append(f"Focus recap: {focus_recap}")
        if artifact_text:
            lines.append("Prior artifacts:")
            lines.append(artifact_text)
        if evidence:
            lines.append("Evidence:")
        for index, item in enumerate(evidence, start=1):
            source = str(item.get("source", ""))
            page = item.get("page")
            content = str(item.get("content", "")).strip()
            prefix = f"[{index}] {_citation(source, page)}: "
            remaining = self.max_context_chars - len("\n".join(lines)) - len(prefix) - 1
            if remaining <= 0:
                break
            if len(content) > remaining:
                content = content[: max(0, remaining - 3)].rstrip() + "..."
            lines.append(prefix + content)
        context = "\n".join(lines)
        return context[: self.max_context_chars]

    @staticmethod
    def _format_artifact_context(artifact_context: dict[str, Any] | None) -> str:
        if not artifact_context:
            return ""
        parts: list[str] = []
        plan_context = str(artifact_context.get("plan_context", "")).strip()
        final_answer_context = str(artifact_context.get("final_answer_context", "")).strip()
        if plan_context:
            parts.append(f"Plan:\n{plan_context}")
        if final_answer_context:
            parts.append(f"Final answer:\n{final_answer_context}")
        return "\n\n".join(parts)


def load_artifact_context(session_dir: str | Path) -> dict[str, Any]:
    """Load Sprint 1 artifacts into context-safe material."""
    root = Path(session_dir)
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Artifact session directory does not exist: {root}")

    session = _read_json(root / "session.json", default={})
    plan_payload = _read_json(root / "plan.json", default={"plan": []})
    evidence_payload = _read_json(root / "evidence.json", default={"evidence": []})
    final_answer_path = root / "final_answer.md"
    final_answer = (
        final_answer_path.read_text(encoding="utf-8").strip()
        if final_answer_path.exists()
        else ""
    )

    plan_items = [str(item) for item in plan_payload.get("plan", [])]
    return {
        "session_id": str(session.get("session_id", root.name)),
        "question": session.get("question"),
        "plan_context": "\n".join(f"- {item}" for item in plan_items),
        "evidence": list(evidence_payload.get("evidence", [])),
        "final_answer_context": final_answer,
    }


def _read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))
