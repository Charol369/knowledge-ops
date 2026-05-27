# Sprint 5: SSE / Demo / Benchmark / README Finalization

## Why
After the production controls are in place, KnowledgeOps needs final user-facing delivery: streaming API, feedback, demo, reproducible deployment path, measured benchmark, final README, and non-code career deliverables.

## What
- Add SSE streaming endpoint `/api/v1/query/stream`.
- Add `/api/v1/feedback` connected to Langfuse score.
- Build Streamlit Demo.
- Validate docker-compose full integration.
- Prepare cloud deployment boundary.
- Run Locust 100 QPS x 5min pressure test when environment supports it.
- Produce final evaluation and README v2.0.
- Record demo video and project resume paragraph as manual/non-code deliverables.

## Non-Code / Manual Boundaries
- Real cloud deployment is manual and environment-dependent.
- Demo video recording/upload and resume finalization are manual deliverables.
- Job applications or profile updates are outside code execution.
- Benchmark results must be measured, not invented.

## Dependencies
Depends on Sprint 1-4 completed system behavior and observability/security controls.
