# Sprint 2: Hybrid Retrieval + Context Engineering

## Why
After Sprint 1 proves the dense retrieval baseline, KnowledgeOps needs production-grade retrieval quality, query expansion, context assembly, and evaluation scaffolding before agent orchestration is introduced.

## What
- Add BM25 sparse retrieval, RRF hybrid fusion, and Cross-Encoder reranking.
- Add HyDE, Multi-Query, and Query Decomposition.
- Add Context Builder and Artifact-to-context support.
- Prepare RAGAS dataset and `run_ragas.py` evaluation entrypoint.
- Record ADR 002 and ADR 003.

## Non-Code / Manual Boundaries
- RAGAS dataset preparation may include manual curation of examples, but no fabricated evaluation scores are allowed.
- No final benchmark claims belong in this Sprint unless commands actually run.
- No cloud deployment, demo video, or resume/application work belongs here.

## Dependencies
Depends on Sprint 1 loaders, chunking, dense index, dense retriever, artifact structure, and local pipeline baseline.
