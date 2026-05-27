---
change: sprint-2-hybrid-context-engineering
status: draft
---

# Sprint 2 Technical Design: Hybrid Retrieval + Context Engineering

## Objective
Make retrieval production-oriented by combining sparse/dense recall, reranking, query transformation, context assembly, and evaluation scaffolding.

## Architecture Slice
- Deterministic Retrieval Services: sparse, hybrid, rerank, query transform.
- Context Engineering: Context Builder and Artifact-to-context.
- Observability & Eval: RAGAS test data and runner foundation.

## Scope
Sprint 2 builds retrieval services that Sprint 3 can orchestrate through LangGraph and MCP. It does not own agent graph state, policy routing, guardrails, SSE, or final delivery assets.

## Constraints
- Sprint 1 must provide stable ingest, dense retrieval, and artifacts.
- No fabricated metric claims.
- External model usage must have local fallback or stop for user approval.

## Acceptance
Sprint 2 is acceptable when hybrid retrieval and context building are locally testable and evaluation scaffolding is ready for measured runs.
