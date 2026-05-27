---
change: sprint-2-hybrid-context-engineering
design-doc: docs/superpowers/specs/2026-05-27-sprint-2-hybrid-context-engineering-design.md
status: draft
---

# Sprint 2 Plan: Hybrid Retrieval + Context Engineering

## Objective
Convert Sprint 1 dense-only retrieval into a hybrid, context-aware retrieval subsystem with evaluation scaffolding.

## Scope
1. Implement BM25 sparse retriever.
2. Add RRF hybrid fusion over dense and sparse candidates.
3. Add Cross-Encoder rerank stage.
4. Add HyDE, Multi-Query, and Query Decomposition modules.
5. Implement Context Builder and Artifact-to-context.
6. Prepare RAGAS dataset and `run_ragas.py`.
7. Write ADR 002 and ADR 003.

## Constraints
- Requires Sprint 1 completion and stable local evidence/artifact interfaces.
- Do not implement Sprint 3 LangGraph/MCP orchestration.
- Do not require real paid services for acceptance.
- Do not claim benchmark targets unless measured.

## Done When
- BM25, RRF hybrid retrieval, rerank, and query transforms are locally callable.
- Context Builder outputs bounded, citation-ready context.
- RAGAS runner can validate wiring in dry-run mode and run real metrics only when configured.
- ADR 002 and ADR 003 are recorded.

## Stop If
- Sprint 1 dense retrieval or artifact contract changes materially.
- Required Cross-Encoder or RAGAS dependency is not available and adding it needs approval.
- Evaluation cannot run locally without unapproved credentials.

## Checklist Mapping
| Backlog Item | Plan Step |
|---|---|
| BM25 稀疏检索 | Sparse retrieval |
| RRF 混合融合 | Hybrid fusion |
| Cross-Encoder Rerank | Rerank stage |
| HyDE 查询重写 | Query transform |
| Multi-Query 扩展 | Query transform |
| Query Decomposition | Query transform |
| Context Builder | Context engineering |
| Artifact-to-context | Context engineering |
| RAGAS 测试集准备 | Evaluation data |
| run_ragas.py | Evaluation runner |
| ADR 002 + ADR 003 | Architecture records |

## Verification Commands
```powershell
uv run pytest tests/unit/test_retrieval.py tests/unit/test_context_builder.py
uv run python eval/run_ragas.py --dry-run
uv run python scripts/benchmark.py --retrieval dense,hybrid --top-k 5
```

## Dependency on Previous Sprints
Depends on Sprint 1. Sprint 2 must be recalibrated after Sprint 1 execution because concrete loader metadata, FAISS persistence paths, and artifact schemas may shift.

## Manual / Non-Code Delivery Boundary
Manual RAGAS dataset curation is allowed; fabricated metrics, cloud deployment, demo video, resume, and job-application actions are excluded.

## `/goal` Draft Outline
- Read Sprint 1 actual outputs and contracts first.
- Implement retrieval modules, query transforms, Context Builder, and evaluation scaffolding.
- Run retrieval/context tests and dry-run evaluation.
- Update ADR 002/003 and benchmark notes only with real results.

## `/goal` Readiness
Do not finalize before Sprint 1 is executed and contracts are recalibrated.
