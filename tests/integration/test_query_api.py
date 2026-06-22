from pathlib import Path

from fastapi.testclient import TestClient

from src.main import app


def test_query_endpoint_invokes_sprint3_graph(tmp_path: Path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "sample.html").write_text(
        "<body><p>API graph evidence cites a local HTML document.</p></body>",
        encoding="utf-8",
    )
    client = TestClient(app)

    response = client.post(
        "/api/v1/query",
        json={
            "question": "What does the API graph evidence cite?",
            "thread_id": "api-thread",
            "docs_dir": str(docs_dir),
            "index_dir": str(tmp_path / "index"),
            "artifact_root": str(tmp_path / "artifacts"),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert body["confidence"] > 0
    assert len(body["plan"]) >= 2
    assert body["citations"][0]["source"].endswith("sample.html")
    assert body["model_tier_used"] == "tier2"
    assert body["artifact_session_id"]
    assert body["trace_id"] == "api-thread"
    assert body["intent"] == "unknown"
    assert body["strategy"] == "hybrid_retrieval"
    assert body["diagnostics"]["strategy"] == "hybrid_retrieval"
    assert body["needs_human_review"] is False


def test_query_endpoint_accepts_product_session_id(tmp_path: Path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "sample.html").write_text(
        "<body><p>Session based query evidence.</p></body>",
        encoding="utf-8",
    )
    client = TestClient(app)

    response = client.post(
        "/api/v1/query",
        json={
            "question": "What evidence is available for this session?",
            "session_id": "sess-product-test",
            "docs_dir": str(docs_dir),
            "index_dir": str(tmp_path / "index"),
            "artifact_root": str(tmp_path / "artifacts"),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == "sess-product-test"
    assert body["trace_id"]
    assert body["trace_id"] != "sess-product-test"
    assert body["artifact_session_id"]


def test_query_endpoint_auto_generates_trace_without_manual_id(tmp_path: Path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "sample.html").write_text(
        "<body><p>Automatic trace evidence.</p></body>",
        encoding="utf-8",
    )
    client = TestClient(app)

    response = client.post(
        "/api/v1/query",
        json={
            "question": "What evidence is available without a manual trace?",
            "docs_dir": str(docs_dir),
            "index_dir": str(tmp_path / "index"),
            "artifact_root": str(tmp_path / "artifacts"),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["trace_id"]
    assert body["session_id"] == body["trace_id"]
    assert body["artifact_session_id"]


def test_query_endpoint_returns_reference_count_tool_diagnostics(tmp_path: Path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "paper.html").write_text(
        """
        <body>
          <h2>References</h2>
          <p>[1] Alpha reference.</p>
          <p>[2] Beta reference.</p>
          <p>[3] Gamma reference.</p>
        </body>
        """,
        encoding="utf-8",
    )
    client = TestClient(app)

    response = client.post(
        "/api/v1/query",
        json={
            "question": "How many references are in the paper?",
            "docs_dir": str(docs_dir),
            "index_dir": str(tmp_path / "index"),
            "artifact_root": str(tmp_path / "artifacts"),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "count"
    assert body["strategy"] == "reference_count"
    assert body["tool_name"] == "reference_count_tool"
    assert body["tool_status"] == "ok"
    assert body["tool_result"]["count"] == 3
    assert body["diagnostics"]["tool_status"] == "ok"


def test_query_endpoint_blocks_table_query_without_table_index(tmp_path: Path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "paper.html").write_text(
        "<body><p>Table caption exists but no structured table index.</p></body>",
        encoding="utf-8",
    )
    client = TestClient(app)

    response = client.post(
        "/api/v1/query",
        json={
            "question": "What does Table 2 show?",
            "docs_dir": str(docs_dir),
            "index_dir": str(tmp_path / "index"),
            "artifact_root": str(tmp_path / "artifacts"),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "table_query"
    assert body["strategy"] == "table_lookup"
    assert body["tool_name"] == "table_lookup_tool"
    assert body["tool_status"] == "blocked"
    assert "Table parsing/indexing is not available" in body["fallback_reason"]
    assert body["needs_human_review"] is True


def test_query_endpoint_returns_section_lookup_tool_diagnostics(tmp_path: Path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "paper.html").write_text(
        """
        <body>
          <p>3.2 Attention</p>
          <p>Section-scoped attention evidence.</p>
          <p>3.3 Training</p>
          <p>Training details should not be included.</p>
        </body>
        """,
        encoding="utf-8",
    )
    client = TestClient(app)

    response = client.post(
        "/api/v1/query",
        json={
            "question": "Summarize section 3.2",
            "docs_dir": str(docs_dir),
            "index_dir": str(tmp_path / "index"),
            "artifact_root": str(tmp_path / "artifacts"),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "section_summary"
    assert body["strategy"] == "section_lookup"
    assert body["tool_name"] == "section_lookup_tool"
    assert body["tool_status"] == "ok"
    assert body["tool_result"]["section_id"] == "3.2"
    assert "Section-scoped attention evidence" in body["tool_result"]["evidence"][0]["content"]
    assert "Training details" not in body["tool_result"]["evidence"][0]["content"]
