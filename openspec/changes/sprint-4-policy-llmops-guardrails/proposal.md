# Sprint 4: Policy Layer + LLMOps + Guardrails

## Why
After the graph and API surfaces are working, KnowledgeOps needs production controls: model routing, reliability, observability, input/output safety, persistence, and API protection.

## What
- Add Complexity Classifier, Model Router, Cache / Retry / Fallback.
- Add Langfuse self-hosting path and CallbackHandler injection into graph/retrieval/policy decisions.
- Propagate trace_id to API responses and define business metrics.
- Add injection detection levels and Unicode normalization.
- Replace MemorySaver with PostgresSaver.
- Add rate limiting and API key authentication.
- Record ADR 005 and ADR 006.

## Non-Code / Manual Boundaries
- Real Langfuse self-hosting and Postgres service startup may require local/manual Docker or environment setup.
- No real production secrets should be committed.
- Cloud deployment and public demo delivery remain Sprint 5/manual boundaries.

## Dependencies
Depends on Sprint 1-3 graph/API/retrieval contracts.
