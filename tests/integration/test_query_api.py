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
