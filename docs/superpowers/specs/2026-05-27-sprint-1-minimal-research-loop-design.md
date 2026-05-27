---
change: sprint-1-minimal-research-loop
status: draft
---

# Sprint 1 Technical Design: Minimal Research Loop + Evidence Pipeline

## Objective
Deliver the first executable KnowledgeOps loop: ingest local documents, index dense vectors, retrieve evidence, plan minimal subtasks, synthesize an answer, and write artifacts.

## Architecture Slice
- Ingest Pipeline: loaders, splitter, embedder wrapper.
- Knowledge Layer: FAISS local vector index.
- Deterministic Retrieval Services: dense retrieval only.
- Cognitive Agent Layer: minimal planner and simple synthesis path.
- API Layer: ingest endpoint skeleton only.
- Evaluation/Docs: loader tests and dense baseline benchmark notes.

## Scope
This Sprint intentionally avoids hybrid search, reranking, LangGraph orchestration, MCP, policy routing, guardrails, SSE, and cloud/demo delivery.

## Constraints
- Local-first execution.
- No real secrets, paid API keys, cloud services, Docker-only dependencies, or runtime artifacts committed.
- Existing project positioning and learning notes remain intact.

## Acceptance
Sprint 1 is acceptable only when the CLI research loop runs locally with persisted artifacts and loader tests pass.
