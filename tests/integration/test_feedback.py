from fastapi.testclient import TestClient

from src.main import app
from src.observability.metrics import business_metrics


def test_feedback_endpoint_captures_local_feedback_without_langfuse_credentials():
    business_metrics.reset()
    client = TestClient(app)

    response = client.post(
        "/api/v1/feedback",
        json={
            "trace_id": "trace-feedback",
            "score": 1,
            "comment": "Useful answer.",
            "source": "streamlit-demo",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "status": "ok",
        "trace_id": "trace-feedback",
        "score": 1.0,
        "storage": "local-memory",
        "langfuse_status": "disabled",
        "blocked_reason": None,
    }

    snapshot = business_metrics.snapshot()
    assert snapshot["feedback_total"] == 1
    assert snapshot["trace_ids"] == ["trace-feedback"]
    assert snapshot["events"][-1] == {
        "type": "feedback",
        "trace_id": "trace-feedback",
        "score": 1.0,
        "comment": "Useful answer.",
        "source": "streamlit-demo",
    }


def test_feedback_endpoint_validates_trace_id_and_score_boundaries():
    client = TestClient(app)

    missing_trace = client.post("/api/v1/feedback", json={"score": 1})
    score_too_high = client.post(
        "/api/v1/feedback",
        json={"trace_id": "trace-feedback", "score": 2},
    )

    assert missing_trace.status_code == 422
    assert score_too_high.status_code == 422
