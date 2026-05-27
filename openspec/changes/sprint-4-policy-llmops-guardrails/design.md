# Sprint 4 Design

## Objective
Harden the graph-backed system with policy routing, reliability controls, observability, guardrails, persistence, and API protection.

## Scope
- Complexity Classifier.
- Model Router.
- Cache / Retry / Fallback.
- Langfuse self-hosting integration path.
- CallbackHandler injection into graph, retrieval, and policy decisions.
- trace_id in API responses.
- Business metrics.
- Two-level injection detection.
- Unicode normalization.
- PostgresSaver replacing MemorySaver.
- Rate Limit middleware.
- API Key authentication.
- ADR 005 and ADR 006.

## Constraints
- Requires Sprint 3 graph/API surfaces and Sprint 2 retrieval context.
- Do not commit secrets or real API keys.
- Local acceptance must not require real cloud services.
- Docker/Postgres/Langfuse availability should be treated as integration configuration, not assumed.
- `/api/v1/feedback` has a documented Sprint boundary discrepancy; implement it in Sprint 5 unless user confirms moving it into Sprint 4.

## Done When
- Policy decisions can route by complexity and model policy.
- Cache/retry/fallback behavior is testable locally.
- Langfuse trace wiring exists and trace_id is returned through API responses.
- Input guardrails normalize Unicode and classify injection risk.
- API key auth and rate limiting protect applicable endpoints.
- Memory checkpointing uses PostgresSaver when configured.
- ADR 005 and ADR 006 are recorded.

## Stop If
- Real credentials or cloud services are required for acceptance.
- Postgres/Langfuse cannot be locally mocked or configured without user action.
- Auth/rate-limit requirements conflict with Sprint 1 ingest skeleton assumptions.

## Verification Commands
```powershell
uv run pytest tests/unit/test_policy.py tests/unit/test_guardrails.py tests/integration/test_auth_rate_limit.py
uv run pytest tests/integration/test_observability.py
uv run uvicorn src.main:app --reload
```
