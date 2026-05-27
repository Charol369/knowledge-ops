# Sprint 5 Design

## Objective
Finalize KnowledgeOps as a demonstrable, benchmarked, documented project with streaming interaction and explicit manual delivery boundaries.

## Scope
- SSE streaming response `/api/v1/query/stream`.
- Feedback endpoint `/api/v1/feedback` connected to Langfuse score.
- Streamlit demo.
- Docker Compose full integration.
- Cloud deployment preparation/boundary.
- Locust 100 QPS x 5min benchmark if local environment supports it.
- Final evaluation.
- README v2.0.
- 5-10 minute demo video manual deliverable.
- Project 1 resume paragraph manual deliverable.

## Constraints
- Requires Sprint 1-4 complete behavior.
- Do not fabricate benchmark/evaluation results.
- Do not mark cloud deployment, video upload, resume finalization, or job applications as code-complete.
- Do not require real public cloud or public upload to pass code acceptance.

## Done When
- Streaming query endpoint works locally.
- Feedback endpoint can submit Langfuse-compatible scores when configured.
- Streamlit demo exercises the primary research flow.
- Docker Compose path is documented/tested when environment supports Docker.
- Benchmark/evaluation results are recorded only after commands run.
- README v2.0 reflects actual system behavior.
- Manual deliverables are listed with owner/action status rather than claimed as automated.

## Stop If
- Benchmarks cannot be run in the available environment.
- Docker/cloud/video/resume tasks require manual user action.
- Observability feedback depends on unavailable Langfuse configuration.

## Verification Commands
```powershell
uv run pytest tests/integration/test_streaming.py tests/integration/test_feedback.py
uv run streamlit run frontend/app.py
docker compose up -d
uv run locust -f eval/locustfile.py --headless -u 100 -r 10 -t 5m
```
