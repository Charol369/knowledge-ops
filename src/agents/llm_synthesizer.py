"""LLM-backed answer synthesis for the product query path."""
import json
import re
from dataclasses import dataclass
from typing import Any, Callable

from openai import OpenAI

from src.config import settings
from src.guardrails.citation import extract_citations, verify_citations


CompletionCreate = Callable[..., Any]


@dataclass(frozen=True)
class LLMSynthesisResult:
    status: str
    answer: str = ""
    model: str | None = None
    blocked_reason: str | None = None
    usage: dict[str, Any] | None = None


class LLMSynthesizer:
    def __init__(self, completion_create: CompletionCreate | None = None):
        self._completion_create = completion_create

    def synthesize(
        self,
        *,
        question: str,
        evidence: list[dict[str, Any]],
        model_tier: str | None,
    ) -> LLMSynthesisResult:
        if not settings.llm_synthesis_enabled:
            return LLMSynthesisResult(
                status="disabled",
                blocked_reason="LLM synthesis is disabled by configuration.",
            )
        if not evidence:
            return LLMSynthesisResult(
                status="blocked",
                blocked_reason="No evidence is available for LLM synthesis.",
            )
        if not _is_provider_configured():
            return LLMSynthesisResult(
                status="blocked",
                blocked_reason="OpenAI-compatible provider is not fully configured.",
            )

        model = _model_for_tier(model_tier)
        attempts = max(1, settings.llm_synthesis_retry_count + 1)
        previous_answer: str | None = None
        last_result: LLMSynthesisResult | None = None
        for attempt in range(attempts):
            try:
                response = self._create_completion(
                    model=model,
                    messages=_build_messages(
                        question=question,
                        evidence=evidence,
                        previous_answer=previous_answer,
                    ),
                    temperature=settings.llm_synthesis_temperature,
                    max_tokens=settings.max_tokens,
                )
            except Exception as exc:
                return LLMSynthesisResult(
                    status="failed",
                    model=model,
                    blocked_reason=f"LLM synthesis request failed: {exc}",
                )

            raw_answer = _extract_content(response).strip()
            usage = _extract_usage(response)
            if not raw_answer:
                last_result = LLMSynthesisResult(
                    status="failed",
                    model=model,
                    blocked_reason="LLM synthesis returned an empty answer.",
                    usage=usage,
                )
                previous_answer = None
                continue

            answer = _render_answer(raw_answer)
            if not answer:
                last_result = LLMSynthesisResult(
                    status="failed",
                    answer=raw_answer,
                    model=model,
                    blocked_reason="LLM synthesis returned an unparsable answer.",
                    usage=usage,
                )
                previous_answer = raw_answer
                continue

            citations = extract_citations(answer, evidence=evidence)
            if not citations:
                last_result = LLMSynthesisResult(
                    status="failed",
                    answer=answer,
                    model=model,
                    blocked_reason="LLM synthesis returned no parseable citations.",
                    usage=usage,
                )
                previous_answer = answer
                continue
            citations_valid, invalid = verify_citations(citations, evidence)
            if not citations_valid:
                last_result = LLMSynthesisResult(
                    status="failed",
                    answer=answer,
                    model=model,
                    blocked_reason=f"LLM synthesis returned unsupported citations: {invalid}",
                    usage=usage,
                )
                previous_answer = answer
                continue

            return LLMSynthesisResult(
                status="ok",
                answer=answer,
                model=model,
                usage=usage,
            )

        return last_result or LLMSynthesisResult(
            status="failed",
            model=model,
            blocked_reason="LLM synthesis failed before producing a response.",
        )

    def _create_completion(self, **kwargs: Any) -> Any:
        if self._completion_create is not None:
            return self._completion_create(**kwargs)
        client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            timeout=settings.llm_synthesis_timeout_seconds,
        )
        return client.chat.completions.create(**kwargs)


def _is_provider_configured() -> bool:
    api_key = settings.deepseek_api_key.strip()
    base_url = settings.deepseek_base_url.strip()
    if not api_key or not base_url:
        return False
    return "填入" not in api_key and not api_key.endswith("your-key")


def _model_for_tier(model_tier: str | None) -> str:
    if model_tier == "tier1":
        return settings.cheap_model or settings.deepseek_model
    if model_tier == "tier3":
        return settings.premium_model or settings.deepseek_model
    return settings.primary_model or settings.deepseek_model


def _build_messages(
    question: str,
    evidence: list[dict[str, Any]],
    previous_answer: str | None = None,
) -> list[dict[str, str]]:
    retry_instruction = ""
    if previous_answer:
        retry_instruction = (
            "\n\nPrevious answer that failed citation validation:\n"
            f"{previous_answer}\n\n"
            "Rewrite the answer now as valid JSON only. Use only citations copied from the "
            "evidence metadata."
        )
    return [
        {
            "role": "system",
            "content": (
                "You are an enterprise knowledge-base question-answering assistant. "
                "Answer only from the provided evidence. If the evidence is insufficient, "
                "say that the knowledge base does not contain enough information. "
                "Use natural language and be concise. Return valid JSON only, with this schema: "
                '{"paragraphs":[{"text":"...","citations":[{"source":"...","page":1}]}]}. '
                "Each paragraph must include at least one citation object. "
                "Do not invent sources, pages, numbers, or external facts. "
                "Use only citation objects whose source and page appear in the evidence metadata. "
                "Do not wrap JSON in markdown fences."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Question:\n{question.strip()}\n\n"
                "Evidence:\n"
                f"{_format_evidence(evidence)}\n\n"
                "Write the final answer in the same language as the question when possible. "
                "Return JSON only."
                f"{retry_instruction}"
            ),
        },
    ]


def _format_evidence(evidence: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    used_chars = 0
    for index, item in enumerate(evidence, start=1):
        source = str(item.get("source", "")).replace("\\", "/")
        page = item.get("page")
        content = " ".join(str(item.get("content", "")).split())
        if not content:
            continue
        remaining = settings.llm_synthesis_max_context_chars - used_chars
        if remaining <= 0:
            break
        if len(content) > remaining:
            content = content[: max(0, remaining - 3)].rstrip() + "..."
        page_text = "unknown" if page is None else str(page)
        block = f"[{index}] source: {source}, page: {page_text}\n{content}"
        lines.append(block)
        used_chars += len(block)
    return "\n\n".join(lines)


def _extract_content(response: Any) -> str:
    if isinstance(response, dict):
        return str(response["choices"][0]["message"]["content"])
    return str(response.choices[0].message.content or "")


def _render_answer(raw_answer: str) -> str:
    structured = _parse_json_answer(raw_answer)
    if structured is None:
        return raw_answer.strip()

    paragraphs = structured.get("paragraphs")
    if paragraphs is None:
        paragraphs = structured.get("answer")
    if isinstance(paragraphs, str):
        text = paragraphs.strip()
        citations = _render_citations(structured.get("citations"))
        return f"{text} {citations}".strip() if citations else text
    if not isinstance(paragraphs, list):
        return ""

    rendered: list[str] = []
    for paragraph in paragraphs:
        if isinstance(paragraph, str):
            text = paragraph.strip()
            citations = ""
        elif isinstance(paragraph, dict):
            text = str(paragraph.get("text") or paragraph.get("answer") or "").strip()
            citations = _render_citations(paragraph.get("citations"))
        else:
            continue
        if not text:
            continue
        rendered.append(f"{_strip_citation_markers(text)} {citations}".strip())
    return "\n\n".join(rendered)


def _parse_json_answer(raw_answer: str) -> dict[str, Any] | None:
    candidate = raw_answer.strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?\s*", "", candidate, flags=re.IGNORECASE)
        candidate = re.sub(r"\s*```$", "", candidate)
    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", candidate, flags=re.DOTALL)
        if not match:
            return None
        try:
            payload = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return payload if isinstance(payload, dict) else None


def _render_citations(citations: Any) -> str:
    if not isinstance(citations, list):
        return ""
    markers: list[str] = []
    seen: set[tuple[str, str]] = set()
    for citation in citations:
        if not isinstance(citation, dict):
            continue
        source = str(citation.get("source") or "").replace("\\", "/").strip()
        page = citation.get("page")
        if not source or page is None:
            continue
        page_text = str(page).strip()
        key = (source, page_text)
        if key in seen:
            continue
        seen.add(key)
        markers.append(f"[source: {source}, page {page_text}]")
    return " ".join(markers)


def _strip_citation_markers(text: str) -> str:
    return re.sub(r"\s*\[(?:来源|source):[^\]]+\]", "", text, flags=re.IGNORECASE).strip()


def _extract_usage(response: Any) -> dict[str, Any] | None:
    usage = response.get("usage") if isinstance(response, dict) else getattr(response, "usage", None)
    if usage is None:
        return None
    if isinstance(usage, dict):
        return usage
    model_dump = getattr(usage, "model_dump", None)
    if callable(model_dump):
        return model_dump(mode="json")
    return None
