from src.agents.intent_router import classify_query_intent


def test_intent_router_classifies_definition():
    result = classify_query_intent("What is multi-head attention?")

    assert result.intent == "definition"
    assert result.strategy == "hybrid_retrieval"
    assert result.tool_name is None


def test_intent_router_classifies_reference_count():
    result = classify_query_intent("How many references are in Attention Is All You Need?")

    assert result.intent == "count"
    assert result.strategy == "reference_count"
    assert result.tool_name == "reference_count_tool"
    assert result.target == "references"


def test_intent_router_classifies_section_summary():
    result = classify_query_intent("Summarize section 3.2 in the paper.")

    assert result.intent == "section_summary"
    assert result.strategy == "section_lookup"
    assert result.tool_name == "section_lookup_tool"
    assert result.target == "3.2"


def test_intent_router_classifies_table_query():
    result = classify_query_intent("What does Table 2 show?")

    assert result.intent == "table_query"
    assert result.strategy == "table_lookup"
    assert result.tool_name == "table_lookup_tool"


def test_intent_router_classifies_no_answer_pattern():
    result = classify_query_intent("What was the author's private salary?")

    assert result.intent == "no_answer"
    assert result.strategy == "blocked"


def test_intent_router_classifies_list():
    result = classify_query_intent("List the datasets used in experiments.")

    assert result.intent == "list"
    assert result.strategy == "targeted_retrieval"
    assert result.tool_name is None


def test_intent_router_classifies_compare():
    result = classify_query_intent("Compare encoder attention versus decoder attention.")

    assert result.intent == "compare"
    assert result.strategy == "hybrid_retrieval"
    assert result.tool_name is None


def test_intent_router_classifies_unknown():
    result = classify_query_intent("Transformer training details")

    assert result.intent == "unknown"
    assert result.strategy == "hybrid_retrieval"
    assert result.tool_name is None


def test_intent_router_respects_valid_requested_intent():
    result = classify_query_intent("Explain anything", requested_intent="list")

    assert result.intent == "list"
    assert result.strategy == "targeted_retrieval"
    assert result.route_reason == "caller_requested_intent"
