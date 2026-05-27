# Sprint 1 Design

## Objective
Create the smallest production-oriented research loop that proves local ingestion, dense retrieval, planning, artifact capture, and answer synthesis can work end to end.

## Scope
- Ingest loaders: PDF, Word, HTML.
- Splitter: RecursiveCharacterTextSplitter with chunk_size=500 and overlap=50.
- Embedder wrapper with bge-m3 preferred and configuration-based switching.
- FAISS dense baseline index and persisted local index.
- Dense retrieval interface with k=5.
- Minimal planner producing research decision and 2-4 subtasks.
- Session artifact directory for plan/evidence/final_answer.
- CLI loop and ingest API skeleton.
- Unit loader tests and baseline benchmark notes.

## Constraints
- Keep implementation local and reproducible with existing project stack.
- Do not require paid API keys, external cloud services, Docker daemon, Milvus, or production databases.
- Do not commit `.env`, secrets, runtime artifacts, large data files, model weights, or database files.
- Do not mark benchmark targets as achieved unless commands actually run.

## Done When
- CLI pipeline runs question -> plan -> retrieve -> synthesize -> answer on local fixture data.
- Ingest API skeleton exists but remains unauthenticated until Sprint 4.
- Dense retrieval returns source-grounded evidence with metadata.
- Session artifacts are written for plan, evidence, and final answer.
- Loader unit tests exist and pass.
- Sprint 1 baseline benchmark entry is updated only with measured local values.

## Stop If
- A new heavy dependency is required but not already approved.
- Real credentials, external paid services, cloud infrastructure, or Docker-only dependencies become necessary.
- Existing docs do not clearly resolve metadata, artifact, or benchmark boundary decisions.

## Verification Commands
```powershell
uv run pytest tests/unit/test_loaders.py
uv run python scripts/ingest_pdfs.py data/pdfs/
uv run python -m src.agents.graph --question "Summarize the indexed evidence"
uv run uvicorn src.main:app --reload
```
