---
change: sprint-1-minimal-research-loop
design-doc: docs/superpowers/specs/2026-05-27-sprint-1-minimal-research-loop-design.md
status: draft
---

# Sprint 1 Plan: Minimal Research Loop + Evidence Pipeline

## Objective
Establish the minimum local research pipeline required by all later Sprints.

## Scope
1. Implement PDF, Word, and HTML loaders.
2. Implement fixed baseline splitting.
3. Add configurable embedder wrapper.
4. Build and persist FAISS dense index.
5. Expose dense retrieval with k=5.
6. Add minimal planner, artifact store, CLI loop, and ingest API skeleton.
7. Add loader unit tests and baseline benchmark documentation.

## Constraints
- Do not require external paid models, real credentials, cloud services, or Docker-only services.
- Do not add heavy dependencies without stopping for approval.
- Do not fabricate metrics in `docs/benchmark.md`.
- Do not implement Sprint 2-5 features in this Sprint.

## Done When
- `question -> plan -> retrieve -> synthesize -> answer` works locally.
- `plan`, `evidence`, and `final_answer` artifacts are written per session.
- FAISS index can be persisted and reused.
- `/api/v1/ingest` exists as a skeleton without auth.
- At least 3 loader unit cases pass.
- Sprint 1 benchmark baseline is documented only if measured.

## Stop If
- Existing fixtures/data are insufficient to validate local ingestion.
- A real secret, paid model, cloud service, or unapproved dependency is required.
- Benchmark values cannot be measured locally.

## Checklist Mapping
| Backlog Item | Plan Step |
|---|---|
| PDF Loader | Loaders |
| Word / HTML Loader | Loaders |
| Recursive splitter | Splitting |
| Embedder wrapper | Embedding |
| FAISS baseline | Indexing |
| Dense retrieval | Retrieval |
| Minimal Planner | Agent baseline |
| Session artifacts | Artifact persistence |
| CLI research loop | Pipeline |
| `/api/v1/ingest` skeleton | API |
| Loader tests | Testing |
| Benchmark baseline | Docs/eval |

## Verification Commands
```powershell
uv run pytest tests/unit/test_loaders.py
uv run python scripts/ingest_pdfs.py data/pdfs/
uv run python -m src.agents.graph --question "Summarize the indexed evidence"
uv run uvicorn src.main:app --reload
```

## Dependency on Previous Sprints
None. Sprint 1 is the prerequisite for all later work.

## Manual / Non-Code Delivery Boundary
Excluded: real cloud deployment, Bilibili upload, resume finalization, job applications, final demo video, and real production benchmark claims.

## `/goal` Readiness
Sprint 1 can directly enter `/goal` finalization because its checklist, dependencies, and boundaries are fully identified from project docs.
