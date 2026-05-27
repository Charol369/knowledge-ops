---
change: sprint-4-policy-llmops-guardrails
design-doc: docs/superpowers/specs/2026-05-27-sprint-4-policy-llmops-guardrails-design.md
status: draft
---

# Sprint 4 Plan: Policy Layer + LLMOps + Guardrails

## Objective
Add production-grade control, safety, persistence, and observability around the graph-backed KnowledgeOps system.

## Scope
1. Implement Complexity Classifier and Model Router.
2. Add Cache / Retry / Fallback.
3. Add Langfuse tracing integration and callback injection into graph/retrieval/policy decisions.
4. Propagate trace_id to API responses and define business metrics.
5. Add two-level injection detection and Unicode normalization.
6. Replace MemorySaver with PostgresSaver when configured.
7. Add rate limiting middleware and API key auth.
8. Write ADR 005 and ADR 006.

## Constraints
- Requires Sprint 1-3 contracts.
- Do not commit real credentials or secrets.
- Do not require real cloud services for local acceptance.
- Treat Langfuse/Postgres runtime startup as integration/manual if local services are unavailable.
- Keep `/api/v1/feedback` for Sprint 5 unless user confirms the Sprint 4 API-doc boundary should win.

## Done When
- Policy decisions are testable and observable.
- Cache/retry/fallback has deterministic tests.
- API responses include trace_id.
- Guardrails detect injection risk and normalize Unicode.
- Protected endpoints enforce API key auth and rate limits.
- PostgresSaver is used when configuration is present.
- ADR 005 and ADR 006 are recorded.

## Stop If
- Any implementation requires committing secrets or real credentials.
- Langfuse/Postgres requires unavailable manual service setup to pass tests.
- Existing API contract makes auth/rate-limit rollout ambiguous.

## Checklist Mapping
| Backlog Item | Plan Step |
|---|---|
| Complexity Classifier | Policy |
| Model Router | Policy |
| Cache / Retry / Fallback | Reliability |
| Langfuse 自托管部署 | Observability integration/manual boundary |
| CallbackHandler 注入 graph / retrieval / policy 决策 | Observability instrumentation |
| trace_id 透传到 API 响应 | API observability |
| 业务指标 | Metrics |
| Injection 检测二级化 | Guardrails |
| Unicode 归一化 | Guardrails |
| PostgresSaver 替代 MemorySaver | Persistence |
| Rate Limit 中间件 | API protection |
| API Key 鉴权 | API protection |
| ADR 005 + ADR 006 | Architecture records |

## Verification Commands
```powershell
uv run pytest tests/unit/test_policy.py tests/unit/test_guardrails.py tests/integration/test_auth_rate_limit.py
uv run pytest tests/integration/test_observability.py
uv run uvicorn src.main:app --reload
```

## Dependency on Previous Sprints
Depends on Sprint 1-3. Sprint 4 must be recalibrated after Sprint 3 because policy, guardrail, and tracing hooks must match the actual graph/API boundaries.

## Manual / Non-Code Delivery Boundary
Manual Langfuse/Postgres local service setup may be needed for full integration. Real secrets, cloud deployment, public demo, resume, and applications are excluded.

## `/goal` Draft Outline
- Read final Sprint 1-3 graph/API contracts first.
- Implement policy, observability, guardrails, persistence, auth, and rate limiting.
- Add tests for protected endpoints and trace propagation.
- Record ADR 005/006.

## `/goal` Readiness
Do not finalize before Sprint 1-3 are executed and graph/API contracts are recalibrated.
