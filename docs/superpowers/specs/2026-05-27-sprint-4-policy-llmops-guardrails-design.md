---
change: sprint-4-policy-llmops-guardrails
status: draft
---

# Sprint 4 Technical Design: Policy Layer + LLMOps + Guardrails

## Objective
Add production controls around the graph: policy routing, reliability, tracing, safety checks, persistence, and API protection.

## Architecture Slice
- Policy Layer: complexity classifier, model router, cache/retry/fallback.
- Observability & Eval: Langfuse traces, trace_id propagation, business metrics.
- Guardrails Layer: injection detection and Unicode normalization.
- API Layer: API key auth and rate limiting.
- Agent State: PostgresSaver checkpointing.

## Scope
Sprint 4 hardens the existing graph/API. It does not own SSE streaming, final benchmark report, Streamlit demo, final README, public video, deployment, resume, or applications.

## Constraints
- No committed secrets.
- Local acceptance cannot depend on real cloud services.
- The `/api/v1/feedback` boundary conflicts across docs; keep feedback implementation in Sprint 5 unless Boss explicitly moves it.

## Acceptance
Sprint 4 is acceptable when protected graph-backed requests are observable, policy-routed, guarded, and locally testable.
