from pathlib import Path

from src.retrieval.artifact_store import ArtifactStore
from src.retrieval.context_builder import ContextBuilder, load_artifact_context


def test_context_builder_deduplicates_orders_budgets_and_formats_citations():
    evidence = [
        {
            "content": "Second item should be trimmed because of token budget.",
            "source": "b.md",
            "page": 4,
            "score": 0.4,
        },
        {
            "content": "Top evidence about Transformer attention.",
            "source": "a.md",
            "page": 1,
            "score": 0.9,
        },
        {
            "content": "Top evidence about Transformer attention.",
            "source": "a.md",
            "page": 1,
            "score": 0.1,
        },
    ]

    context = ContextBuilder(max_evidence_items=2, max_context_chars=220).build(
        question="How does Transformer attention work?",
        evidence=evidence,
        focus_recap="Focus on citations.",
    )

    assert context["question"] == "How does Transformer attention work?"
    assert context["focus_recap"] == "Focus on citations."
    assert len(context["evidence"]) == 2
    assert [item["source"] for item in context["evidence"]] == ["a.md", "b.md"]
    assert "[1] a.md p.1" in context["context"]
    assert "[2] b.md p.4" in context["context"]
    assert len(context["context"]) <= 220


def test_artifact_to_context_loads_sprint1_artifacts(tmp_path: Path):
    store = ArtifactStore(root_dir=tmp_path)
    session_id = store.create_session("What is Sprint 2?")
    store.save_plan(session_id, ["Retrieve sparse evidence", "Build context"])
    store.save_evidence(
        session_id,
        [{"content": "Hybrid retrieval evidence.", "source": "hybrid.md", "page": 2}],
    )
    store.save_final_answer(session_id, "Sprint 2 adds hybrid retrieval.")

    material = load_artifact_context(tmp_path / session_id)

    assert material["session_id"] == session_id
    assert "Retrieve sparse evidence" in material["plan_context"]
    assert material["evidence"][0]["source"] == "hybrid.md"
    assert material["final_answer_context"] == "Sprint 2 adds hybrid retrieval."

    context = ContextBuilder().build(
        question="Summarize previous work.",
        evidence=material["evidence"],
        artifact_context=material,
    )

    assert "Hybrid retrieval evidence." in context["context"]
    assert "Retrieve sparse evidence" in context["artifact_context"]
