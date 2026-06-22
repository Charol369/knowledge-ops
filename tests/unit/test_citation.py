from langchain_core.documents import Document
from pydantic import ValidationError
import pytest

from src.guardrails.citation import extract_citations, verify_citations
from src.guardrails.output_schema import Answer


def test_extract_citations_supports_chinese_and_source_markers():
    answer = (
        "Transformer evidence is grounded [来源: docs/attention.pdf, page 2]. "
        "A plain source also works [source: notes/context.md]."
    )

    citations = extract_citations(answer)

    assert citations == [
        {"source": "docs/attention.pdf", "page": 2, "snippet": None},
        {"source": "notes/context.md", "page": None, "snippet": None},
    ]


def test_verify_citations_matches_dicts_and_documents_and_flags_unsupported():
    chunks = [
        {"content": "attention evidence", "source": "docs/attention.pdf", "page": 2},
        Document(page_content="context evidence", metadata={"source": "notes/context.md"}),
    ]

    valid, invalid = verify_citations(
        [
            {"source": "docs/attention.pdf", "page": 2},
            {"source": "notes/context.md", "page": None},
            {"source": "missing.pdf", "page": 9},
        ],
        chunks,
    )

    assert valid is False
    assert invalid == ["missing.pdf#page=9"]


def test_extract_citations_can_attach_snippets_from_matching_evidence():
    answer = "Grounded statement [source: docs/attention.pdf, page 2]."
    citations = extract_citations(
        answer,
        evidence=[
            {
                "content": "Multi-head attention evidence.",
                "source": "docs/attention.pdf",
                "page": 2,
            }
        ],
    )

    assert citations == [
        {
            "source": "docs/attention.pdf",
            "page": 2,
            "snippet": "Multi-head attention evidence.",
        }
    ]


def test_answer_schema_rejects_invalid_confidence():
    with pytest.raises(ValidationError):
        Answer(
            answer="Unsupported answer",
            confidence=1.5,
            citations=[],
            needs_human_review=False,
        )
