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
    assert body["artifact_session_id"]
    assert body["trace_id"] == "api-thread"
    assert body["needs_human_review"] is False
