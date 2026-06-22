from scripts.evaluate_intent_qa import (
    load_cases,
    score_response,
    write_json_output,
)


def test_intent_qa_eval_scores_structured_response_success():
    case = {
        "id": "case-1",
        "question": "How many references?",
        "expected_intent": "count",
        "expected_strategy": "reference_count",
        "expected_tool_status": "ok",
        "expected_tool_result": {"count": 2},
        "expected_sources": ["paper.html"],
        "expected_answer_contains": ["2"],
    }
    body = {
        "intent": "count",
        "strategy": "reference_count",
        "tool_status": "ok",
        "tool_result": {"count": 2},
        "answer": "There are 2 references. [source: paper.html]",
        "citations": [{"source": "tmp/paper.html", "page": None}],
    }

    assert score_response(case, body) == []


def test_intent_qa_eval_reports_mismatches():
    failures = score_response(
        {
            "id": "case-1",
            "question": "What does Table 2 show?",
            "expected_intent": "table_query",
            "expected_strategy": "table_lookup",
            "expected_tool_status": "blocked",
            "expected_answer_contains": ["cannot be answered"],
        },
        {
            "intent": "unknown",
            "strategy": "hybrid_retrieval",
            "tool_status": None,
            "answer": "Table 2 shows results.",
            "citations": [],
        },
    )

    assert "intent: expected 'table_query', got 'unknown'" in failures
    assert "strategy: expected 'table_lookup', got 'hybrid_retrieval'" in failures
    assert "tool_status: expected 'blocked', got None" in failures
    assert "answer missing fragment 'cannot be answered'" in failures


def test_intent_qa_eval_loads_jsonl_and_persists_output(tmp_path):
    dataset = tmp_path / "intent.jsonl"
    dataset.write_text(
        '{"id":"case-1","question":"Q","expected_intent":"unknown","expected_strategy":"hybrid_retrieval"}\n',
        encoding="utf-8",
    )
    output = tmp_path / "results" / "intent.json"

    cases = load_cases(dataset)
    write_json_output({"status": "ok", "cases_total": len(cases)}, output)

    assert cases[0]["id"] == "case-1"
    assert output.exists()
    assert '"cases_total": 1' in output.read_text(encoding="utf-8")
