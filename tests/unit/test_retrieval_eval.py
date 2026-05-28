from langchain_core.documents import Document

from scripts.evaluate_retrieval import is_relevant, score_case, summarize_mode


def test_retrieval_eval_matches_expected_source_and_page():
    case = {
        "id": "case-1",
        "question": "Where is attention defined?",
        "expected_sources": ["data\\attention.pdf"],
        "expected_pages": [3],
    }
    matching = Document(
        page_content="Scaled dot-product attention.",
        metadata={"source": "data/attention.pdf", "page": 3},
    )
    wrong_page = Document(
        page_content="Different page.",
        metadata={"source": "data/attention.pdf", "page": 4},
    )

    assert is_relevant(matching, case)
    assert not is_relevant(wrong_page, case)


def test_retrieval_eval_scores_hit_rank_and_summary_metrics():
    case = {
        "id": "case-1",
        "question": "Where is attention defined?",
        "expected_sources": ["paper.md"],
        "expected_pages": [2],
    }
    results = [
        Document(page_content="No match.", metadata={"source": "other.md", "page": 1}),
        Document(page_content="Attention match.", metadata={"source": "paper.md", "page": 2}),
    ]

    scored = score_case(case, results)
    summary = summarize_mode([scored], top_k=2, started=0.0)

    assert scored["hit"] is True
    assert scored["first_hit_rank"] == 2
    assert summary["hit_at_k"] == 1.0
    assert summary["question_recall_at_k"] == 1.0
    assert summary["mrr_at_k"] == 0.5
