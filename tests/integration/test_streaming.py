import json
from pathlib import Path

from fastapi.testclient import TestClient

from src.main import app


def _parse_sse_events(payload: str) -> list[dict]:
    events = []
    current: dict[str, str] = {}
    data_lines: list[str] = []
    for raw_line in payload.splitlines():
        line = raw_line.strip()
        if not line:
            if current or data_lines:
                current["data"] = "\n".join(data_lines)
                events.append(current)
            current = {}
            data_lines = []
            continue
        if line.startswith("event:"):
            current["event"] = line.removeprefix("event:").strip()
        elif line.startswith("data:"):
            data_lines.append(line.removeprefix("data:").strip())
    if current or data_lines:
        current["data"] = "\n".join(data_lines)
        events.append(current)
    return events


def test_query_stream_emits_ordered_progress_and_completion_events(tmp_path: Path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "sample.html").write_text(
        "<body><p>Streaming evidence cites this local HTML document.</p></body>",
        encoding="utf-8",
    )
    client = TestClient(app)

    response = client.post(
        "/api/v1/query/stream",
        json={
            "question": "What evidence does the streaming endpoint cite?",
            "thread_id": "stream-thread",
            "docs_dir": str(docs_dir),
            "index_dir": str(tmp_path / "index"),
            "artifact_root": str(tmp_path / "artifacts"),
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    events = _parse_sse_events(response.text)

    assert [event["event"] for event in events] == [
        "progress",
        "progress",
        "completion",
    ]
    started = json.loads(events[0]["data"])
    graph_completed = json.loads(events[1]["data"])
    completion = json.loads(events[2]["data"])

    assert started["stage"] == "started"
    assert started["trace_id"] == "stream-thread"
    assert graph_completed["stage"] == "graph_completed"
    assert graph_completed["trace_id"] == "stream-thread"
    assert len(graph_completed["plan"]) >= 2
    assert completion["trace_id"] == "stream-thread"
    assert completion["answer"]
    assert completion["citations"][0]["source"].endswith("sample.html")
    assert completion["needs_human_review"] is False


def test_query_stream_reuses_sprint4_api_key_protection():
    previous_auth = app.state.api_auth_enabled
    previous_key = app.state.api_key
    previous_rate_limit = app.state.rate_limit_enabled
    app.state.api_auth_enabled = True
    app.state.api_key = "expected-secret"
    app.state.rate_limit_enabled = False
    try:
        response = TestClient(app).post(
            "/api/v1/query/stream",
            json={"question": "Will auth protect streaming?"},
        )
    finally:
        app.state.api_auth_enabled = previous_auth
        app.state.api_key = previous_key
        app.state.rate_limit_enabled = previous_rate_limit

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key."}
