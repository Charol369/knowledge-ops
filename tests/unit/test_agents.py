from pathlib import Path

from src.agents.graph import run_research_graph
from src.agents import orchestrator as orchestrator_module
from src.agents.orchestrator import RetrievalOrchestrator


def test_run_research_graph_executes_plan_retrieve_synthesize_report_verify(tmp_path: Path):
    evidence = [
        {
            "content": "KnowledgeOps uses cited local evidence in Sprint 3.",
            "source": "fixture.md",
            "page": 1,
            "score": 0.9,
        }
    ]

    result = run_research_graph(
        question="How does Sprint 3 ground answers?",
        thread_id="test-thread",
        evidence=evidence,
        artifact_root=tmp_path,
    )

    assert result["execution_path"] == [
        "intent_router",
        "planner",
        "retrieval_orchestrator",
        "synthesizer",
        "reporter",
        "verifier",
    ]
    assert 2 <= len(result["plan"]) <= 4
    assert result["evidence"][0]["source"] == "fixture.md"
    assert result["context"]["evidence"][0]["source"] == "fixture.md"
    assert "fixture.md" in result["answer"]
    assert result["citations"] == [
        {
            "source": "fixture.md",
            "page": 1,
            "snippet": "KnowledgeOps uses cited local evidence in Sprint 3.",
        }
    ]
    assert result["verification"]["status"] == "ok"
    assert result["intent"] == "unknown"
    assert result["strategy"] == "hybrid_retrieval"
    assert result["structured_answer"]["confidence"] > 0
    assert result["artifact_session_id"]
    assert (tmp_path / result["artifact_session_id"] / "plan.json").exists()
    assert (tmp_path / result["artifact_session_id"] / "evidence.json").exists()
    assert (tmp_path / result["artifact_session_id"] / "final_answer.md").exists()


def test_run_research_graph_uses_local_docs_and_context_builder(tmp_path: Path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "sample.html").write_text(
        "<body><main><p>Graph retrieval evidence about local context.</p></main></body>",
        encoding="utf-8",
    )

    result = run_research_graph(
        question="What evidence mentions local context?",
        thread_id="docs-thread",
        docs_dir=docs_dir,
        index_dir=tmp_path / "index",
        artifact_root=tmp_path / "artifacts",
    )

    assert result["verification"]["status"] == "ok"
    assert result["context"]["context"].startswith("Evidence:")
    assert len(result["evidence"]) >= 1
    assert all(item["source"] for item in result["evidence"])


def test_run_research_graph_routes_reference_count_tool(tmp_path: Path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "paper.html").write_text(
        """
        <body>
          <h2>References</h2>
          <p>[1] Alpha reference.</p>
          <p>[2] Beta reference.</p>
        </body>
        """,
        encoding="utf-8",
    )

    result = run_research_graph(
        question="How many references are in the paper?",
        docs_dir=docs_dir,
        index_dir=tmp_path / "index",
        artifact_root=tmp_path / "artifacts",
    )

    assert result["intent"] == "count"
    assert result["strategy"] == "reference_count"
    assert result["tool_name"] == "reference_count_tool"
    assert result["tool_status"] == "ok"
    assert result["tool_result"]["count"] == 2
    assert result["evidence"][0]["reference_count"] == 2


def test_retrieval_orchestrator_optional_transform_and_rerank_fallback(tmp_path: Path, monkeypatch):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "sample.html").write_text(
        "<body><p>Alpha evidence for optional query transform.</p>"
        "<p>Beta evidence for a transformed query.</p></body>",
        encoding="utf-8",
    )
    calls = {}

    def fake_multi_query_expand(query, llm=None, n=3):
        calls["query"] = query
        calls["n"] = n
        return [query, "beta evidence"]

    monkeypatch.setattr(orchestrator_module.settings, "query_transform_enabled", True)
    monkeypatch.setattr(orchestrator_module.settings, "query_transform_count", 2)
    monkeypatch.setattr(orchestrator_module.settings, "rerank_enabled", True)
    monkeypatch.setattr(orchestrator_module.settings, "rerank_model_name", "local/missing-reranker")
    monkeypatch.setattr(orchestrator_module, "multi_query_expand", fake_multi_query_expand)

    evidence = RetrievalOrchestrator(
        docs_dir=str(docs_dir),
        index_dir=str(tmp_path / "index"),
        embedding_backend="hash",
        top_k=2,
    ).gather_evidence("alpha evidence", [])

    assert calls == {"query": "alpha evidence", "n": 2}
    assert evidence
    assert all(item["source"] for item in evidence)
