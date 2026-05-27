---
change: sprint-5-demo-benchmark-delivery
design-doc: docs/superpowers/specs/2026-05-27-sprint-5-demo-benchmark-delivery-design.md
status: draft
---

# Sprint 5 Plan: SSE / Demo / Benchmark / README Finalization

## Objective
Finalize the project as a demonstrable, benchmarked, documented KnowledgeOps system.

## Scope
1. Implement `/api/v1/query/stream` SSE streaming.
2. Implement `/api/v1/feedback` to connect feedback scores to Langfuse when configured.
3. Build Streamlit demo for the golden research path.
4. Validate docker-compose full integration when Docker is available.
5. Prepare cloud deployment boundary and instructions.
6. Run Locust 100 QPS x 5min pressure test when environment supports it.
7. Run final evaluation and update benchmark docs.
8. Produce README v2.0 from actual behavior.
9. Track 5-10 minute demo video as manual deliverable.
10. Track Project 1 resume paragraph as manual deliverable.

## Constraints
- Requires Sprint 1-4 complete behavior.
- Do not fabricate benchmark, RAGAS, latency, cost, or QPS results.
- Do not claim real cloud deployment, video upload, resume finalization, or job applications as automated code work.
- Do not require public cloud or public upload for code acceptance.

## Done When
- SSE endpoint streams graph progress/results locally.
- Feedback endpoint handles Langfuse-compatible scores when configured.
- Streamlit demo exercises the golden path.
- Docker Compose integration path is tested or blocked with clear environment reason.
- Locust/final evaluation results are recorded only if commands ran.
- README v2.0 and benchmark docs match actual measured behavior.
- Manual deliverables are explicitly listed.

## Stop If
- Docker daemon, cloud account, Langfuse credentials, or public upload is required and unavailable.
- Benchmark environment cannot support 100 QPS x 5min.
- README would need to claim unmeasured metrics.

## Checklist Mapping
| Backlog Item | Plan Step |
|---|---|
| SSE 流式响应 `/api/v1/query/stream` | Streaming API |
| 反馈接口 `/api/v1/feedback` 接 Langfuse score | Feedback/observability |
| Streamlit Demo | Demo UI |
| docker-compose 全套联调 | Integration |
| 部署到云 | Manual deployment boundary |
| Locust 100 QPS × 5min 压测 | Performance benchmark |
| 最终评估 | Evaluation |
| README v2.0 | Documentation |
| 录制 5-10 分钟 Demo 视频 | Manual delivery |
| 项目 1 简历段落定稿 | Manual delivery |

## Verification Commands
```powershell
uv run pytest tests/integration/test_streaming.py tests/integration/test_feedback.py
uv run streamlit run frontend/app.py
docker compose up -d
uv run locust -f eval/locustfile.py --headless -u 100 -r 10 -t 5m
```

## Dependency on Previous Sprints
Depends on Sprint 1-4. Sprint 5 must be recalibrated after Sprint 4 because streaming, feedback, demo, and benchmarks must reflect the final guarded/observable API.

## Manual / Non-Code Delivery Boundary
Manual actions: real cloud deployment, public demo video recording/upload, resume finalization, LinkedIn/Boss/Niuke updates, and job applications. These can be planned and documented but not claimed as code execution.

## `/goal` Draft Outline
- Read final Sprint 1-4 API/observability contracts first.
- Implement SSE, feedback endpoint, Streamlit demo, integration checks, and benchmark scripts/docs.
- Run only available verification commands and document blocked manual/environment steps.
- Update README v2.0 from measured behavior.

## `/goal` Readiness
Do not finalize before Sprint 1-4 are executed and API/observability contracts are recalibrated.
