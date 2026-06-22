"""Deterministic document tools for intent-aware QA routing."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from langchain_core.documents import Document

from src.ingest.loaders import load_directory


ToolStatus = Literal["ok", "blocked"]


@dataclass(frozen=True)
class ReferenceCountResult:
    status: ToolStatus
    count: int | None = None
    source: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    evidence: list[dict[str, Any]] | None = None
    blocked_reason: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SectionLookupResult:
    status: ToolStatus
    section_id: str | None = None
    section_title: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    evidence: list[dict[str, Any]] | None = None
    blocked_reason: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def count_references(docs_dir: str | Path) -> ReferenceCountResult:
    docs = _safe_load_documents(docs_dir)
    if not docs:
        return ReferenceCountResult(
            status="blocked",
            evidence=[],
            blocked_reason="No supported local document text was loaded.",
        )

    section = _find_references_section(docs)
    if section is None:
        return ReferenceCountResult(
            status="blocked",
            evidence=[],
            blocked_reason="No references section was located.",
        )

    entries = _count_reference_entries(section["text"])
    if entries <= 0:
        return ReferenceCountResult(
            status="blocked",
            source=section["source"],
            page_start=section["page_start"],
            page_end=section["page_end"],
            evidence=[],
            blocked_reason="References section was located, but entries could not be counted deterministically.",
        )

    evidence = [
        {
            "content": (
                f"Deterministic reference count: {entries}. "
                f"The references section was located in {section['source']}."
            ),
            "source": section["source"],
            "page": section["page_start"],
            "tool": "reference_count_tool",
            "reference_count": entries,
        }
    ]
    return ReferenceCountResult(
        status="ok",
        count=entries,
        source=section["source"],
        page_start=section["page_start"],
        page_end=section["page_end"],
        evidence=evidence,
    )


def lookup_section(docs_dir: str | Path, question: str, section_target: str | None = None) -> SectionLookupResult:
    docs = _safe_load_documents(docs_dir)
    if not docs:
        return SectionLookupResult(
            status="blocked",
            evidence=[],
            blocked_reason="No supported local document text was loaded.",
        )

    target = section_target or _extract_section_target(question)
    if not target:
        return SectionLookupResult(
            status="blocked",
            evidence=[],
            blocked_reason="No section target was found in the question.",
        )

    lines = _document_lines(docs)
    heading_index = _find_section_heading(lines, target)
    if heading_index is None:
        return SectionLookupResult(
            status="blocked",
            evidence=[],
            blocked_reason=f"Section {target} was not located in the local documents.",
        )

    heading = lines[heading_index]
    section_lines = _collect_section_lines(lines, heading_index, target)
    section_text = _clean_text(" ".join(item["text"] for item in section_lines))
    if not section_text:
        return SectionLookupResult(
            status="blocked",
            section_id=target,
            section_title=heading["text"],
            page_start=heading["page"],
            page_end=heading["page"],
            evidence=[],
            blocked_reason=f"Section {target} was located but contained no extractable text.",
        )

    page_values = [item["page"] for item in section_lines if item["page"] is not None]
    page_start = min(page_values) if page_values else heading["page"]
    page_end = max(page_values) if page_values else heading["page"]
    evidence = [
        {
            "content": section_text[:1800],
            "source": heading["source"],
            "page": page_start,
            "section_id": target,
            "section_title": heading["text"],
            "tool": "section_lookup_tool",
        }
    ]
    return SectionLookupResult(
        status="ok",
        section_id=target,
        section_title=heading["text"],
        page_start=page_start,
        page_end=page_end,
        evidence=evidence,
    )


def blocked_table_lookup_result() -> dict[str, Any]:
    return {
        "status": "blocked",
        "blocked_reason": "Table parsing/indexing is not available in the current P0 local index.",
        "evidence": [],
    }


def _safe_load_documents(docs_dir: str | Path) -> list[Document]:
    try:
        return load_directory(docs_dir)
    except Exception:
        return []


def _find_references_section(docs: list[Document]) -> dict[str, Any] | None:
    lines = _document_lines(docs)
    heading_index: int | None = None
    for index, item in enumerate(lines):
        text = item["text"].strip()
        if re.fullmatch(r"(?i)(references|bibliography|works cited)", text):
            heading_index = index
            break
    if heading_index is None:
        return None

    section_lines = []
    for item in lines[heading_index + 1 :]:
        text = item["text"].strip()
        if re.fullmatch(r"(?i)(appendix|acknowledg(e)?ments?)", text):
            break
        section_lines.append(item)

    if not section_lines:
        return None
    pages = [item["page"] for item in section_lines if item["page"] is not None]
    return {
        "text": "\n".join(item["text"] for item in section_lines),
        "source": lines[heading_index]["source"],
        "page_start": min(pages) if pages else lines[heading_index]["page"],
        "page_end": max(pages) if pages else lines[heading_index]["page"],
    }


def _count_reference_entries(text: str) -> int:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    bracketed = [
        line for line in lines if re.match(r"^\[\d+\]\s+\S", line)
    ]
    if bracketed:
        return len(bracketed)

    dotted = [
        line for line in lines if re.match(r"^\d+\.\s+\S", line)
    ]
    if dotted:
        return len(dotted)

    compact_matches = re.findall(r"(?m)(?:^|\n)\s*\[(\d+)\]\s+", text)
    if compact_matches:
        return len(set(compact_matches))
    return 0


def _document_lines(docs: list[Document]) -> list[dict[str, Any]]:
    lines: list[dict[str, Any]] = []
    for doc in docs:
        source = str(doc.metadata.get("source", "")).replace("\\", "/")
        page = doc.metadata.get("page")
        for raw_line in str(doc.page_content).splitlines():
            text = raw_line.strip()
            if not text:
                continue
            lines.append({"text": text, "source": source, "page": page})
    return lines


def _extract_section_target(question: str) -> str | None:
    normalized = question.strip().lower()
    match = re.search(r"\bsection\s+(\d+(?:\.\d+)*)\b", normalized)
    if match:
        return match.group(1)
    match = re.search(r"\b(?:summarize|summary of)\s+(\d+(?:\.\d+)*)\b", normalized)
    return match.group(1) if match else None


def _find_section_heading(lines: list[dict[str, Any]], target: str) -> int | None:
    pattern = re.compile(rf"^{re.escape(target)}(?:\s+|\.?\s*$)", re.IGNORECASE)
    for index, item in enumerate(lines):
        if pattern.match(item["text"].strip()):
            return index
    return None


def _collect_section_lines(
    lines: list[dict[str, Any]],
    heading_index: int,
    target: str,
) -> list[dict[str, Any]]:
    result = [lines[heading_index]]
    target_depth = len(target.split("."))
    for item in lines[heading_index + 1 :]:
        heading = _parse_numbered_heading(item["text"])
        if heading is not None:
            heading_number = heading
            same_or_higher_level = len(heading_number.split(".")) <= target_depth
            if same_or_higher_level and not heading_number.startswith(f"{target}."):
                break
        result.append(item)
    return result


def _parse_numbered_heading(text: str) -> str | None:
    match = re.match(r"^(\d+(?:\.\d+)*)\s+\S", text.strip())
    return match.group(1) if match else None


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

