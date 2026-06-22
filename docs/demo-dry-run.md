# Demo Dry Run

Date: 2026-06-22

This document records the bounded local demo dry run that was actually executed. It verifies that the Streamlit demo can load locally and that the demo's backend query/feedback path works against the current local Docker API. It does not claim that a public demo video was recorded or uploaded.

## Environment

| Item | Observed value |
|---|---|
| API base URL | `http://localhost:8000` |
| API runtime | Docker Compose `knowledge-ops-app` |
| Streamlit URL | `http://localhost:8501` |
| Streamlit command | `uv run streamlit run frontend/app.py --server.headless true --server.port 8501 --browser.gatherUsageStats false` |
| Query | `Summarize the indexed evidence` |
| Thread / trace id | `demo-dry-run-20260622` |
| Embedding backend | `hash` |

## Checks

| Check | Result |
|---|---|
| API health | `GET /health` returned `200`, `{"status":"ok","version":"0.0.1"}` |
| Streamlit page load | `GET http://localhost:8501/` returned `200` |
| Streamlit health | `GET http://localhost:8501/_stcore/health` returned `ok` |
| Demo query path | Frontend helper `post_query_stream()` returned SSE events `progress -> progress -> completion` |
| Plan display data | Completion contained `3` plan steps |
| Citation display data | Completion contained `5` citations |
| Confidence | Completion returned `0.85` |
| Artifact session | Completion returned `20260622T093241Z-869d51b3` |
| Feedback path | Frontend helper `post_feedback()` returned `status=ok` |
| Langfuse score path | Feedback returned `langfuse_status=recorded` |

## Command Evidence

API health:

```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:8000/health
```

Streamlit startup:

```powershell
uv run streamlit run frontend/app.py --server.headless true --server.port 8501 --browser.gatherUsageStats false
```

Streamlit HTTP checks:

```powershell
curl.exe -I --max-time 10 http://localhost:8501/
curl.exe --max-time 10 http://localhost:8501/_stcore/health
```

Bounded demo query and feedback smoke:

```powershell
@'
from frontend.app import post_feedback, post_query_stream

api_base_url = "http://localhost:8000"
thread_id = "demo-dry-run-20260622"
events = post_query_stream(
    api_base_url=api_base_url,
    payload={
        "question": "Summarize the indexed evidence",
        "thread_id": thread_id,
        "docs_dir": "data",
        "index_dir": "data/faiss/sprint1",
        "embedding_backend": "hash",
    },
)
completion = next((event["data"] for event in events if event.get("event") == "completion"), None)
feedback = post_feedback(
    api_base_url=api_base_url,
    trace_id=completion["trace_id"],
    score=1.0,
    comment="Demo dry run feedback.",
)
print({
    "events": [event.get("event") for event in events],
    "plan_steps": len(completion.get("plan") or []),
    "citations": len(completion.get("citations") or []),
    "confidence": completion.get("confidence"),
    "trace_id": completion.get("trace_id"),
    "artifact_session_id": completion.get("artifact_session_id"),
    "feedback_status": feedback.get("status"),
    "langfuse_status": feedback.get("langfuse_status"),
})
'@ | uv run python -
```

Observed output:

```text
{
  'events': ['progress', 'progress', 'completion'],
  'plan_steps': 3,
  'citations': 5,
  'confidence': 0.85,
  'trace_id': 'demo-dry-run-20260622',
  'artifact_session_id': '20260622T093241Z-869d51b3',
  'feedback_status': 'ok',
  'langfuse_status': 'recorded'
}
```

## Boundary

This is a bounded local dry run. It confirms the local demo page can load and the demo query/feedback path works, but it does not prove public deployment, uploaded video, browser-recorded UX walkthrough, 100 QPS, real RAGAS, or production persistence.
