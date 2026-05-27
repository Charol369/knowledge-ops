# Sprint 2 Design

## Objective
Upgrade the retrieval subsystem from dense-only baseline to hybrid retrieval plus context engineering and evaluation scaffolding.

## Scope
- BM25 sparse retrieval.
- RRF hybrid fusion combining dense and sparse candidates.
- Cross-Encoder rerank stage.
- Query transformations: HyDE, Multi-Query, Query Decomposition.
- Context Builder that selects, orders, deduplicates, and budgets evidence.
- Artifact-to-context integration.
- RAGAS test set and `run_ragas.py`.
- ADR 002 and ADR 003.

## Constraints
- Depends on Sprint 1 data model, loaders, FAISS baseline, and artifacts.
- Do not introduce LangGraph graph orchestration or MCP endpoints yet.
- Do not require external paid LLM calls to pass local acceptance.
- Do not fabricate Recall@5, faithfulness, relevancy, latency, or cost metrics.

## Done When
- Dense, sparse, hybrid, and rerank retrieval modes are locally callable.
- Query transform modules can be invoked independently and composed by retrieval orchestration later.
- Context Builder produces bounded, citation-ready context from evidence/artifacts.
- RAGAS dataset and runner exist with documented local execution path.
- ADR 002 and ADR 003 describe retrieval and context-engineering choices.

## Stop If
- Sprint 1 artifacts/index interfaces are missing or unstable.
- Evaluation requires real paid credentials or unavailable external services.
- Retrieval quality claims cannot be backed by executed commands.

## Verification Commands
```powershell
uv run pytest tests/unit/test_retrieval.py tests/unit/test_context_builder.py
uv run python eval/run_ragas.py --dry-run
uv run python scripts/benchmark.py --retrieval dense,hybrid --top-k 5
```
