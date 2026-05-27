# Sprint 1 Codex Goal

You are implementing Sprint 1 only for KnowledgeOps: Minimal Research Loop + Evidence Pipeline.

Do not implement Sprint 2-5 work. Do not expand scope.

## Objective

Create the smallest local KnowledgeOps research loop:

`question -> plan -> retrieve -> synthesize -> answer`

Sprint 1 must support local document ingestion, dense indexing, dense retrieval, minimal planning, answer synthesis, artifact persistence, CLI execution, and an unauthenticated `/api/v1/ingest` implementation that no longer returns 501 for a minimal valid local ingest request.

## Scope

1. Document loaders:
   - Implement PDF loader.
   - Implement Word loader.
   - Implement HTML loader.
   - Loaded evidence metadata must include `source`.
   - PDF metadata must include `page` when available.

2. Recursive chunking:
   - `chunk_size = 500`
   - `overlap = 50`

3. Embedder wrapper:
   - Prefer `bge-m3` when available/configured.
   - Keep embedding backend configurable.
   - Local acceptance must not require real paid external API keys.

4. FAISS dense index baseline:
   - Build dense index from loaded/chunked documents.
   - Persist index locally.
   - Re-load persisted index when needed.
   - Do not commit generated index files.

5. Dense retrieval:
   - Similarity search with `k = 5`.
   - Returned evidence must include `source` metadata.

6. Minimal Sprint 1 Planner:
   - Decide whether the question needs research.
   - Generate 2-4 subtasks.
   - Sprint 1 acceptance is 2-4 subtasks only.
   - Do not write 2-5 as Sprint 1 behavior or acceptance.

7. Session artifact persistence:
   - Persist at least `plan`, `evidence`, and `final_answer`.
   - Keep runtime artifacts out of git.
   - Do not commit generated artifacts.

8. CLI research loop:
   - Add or complete the dedicated Sprint 1 linear CLI entrypoint at `scripts/run_research_loop.py`.
   - Input question.
   - Run `plan -> retrieve -> synthesize -> answer`.
   - Persist session artifacts.
   - Produce a usable local answer from retrieved evidence.
   - This must remain a simple Sprint 1 linear loop, not LangGraph orchestration.

9. `/api/v1/ingest` implementation:
   - Endpoint path: `/api/v1/ingest`.
   - No auth in Sprint 1.
   - Validate basic request input.
   - For a minimal valid local ingest request, the endpoint must not return 501.
   - Wire to the Sprint 1 local ingest path or return a clear local blocked reason when required local sample input is unavailable.
   - Do not add `/api/v1/query` or `/api/v1/feedback`.

10. Sprint 1 tests:
   - `tests/unit/test_loaders.py` must cover at least 3 loader cases.
   - Add only tests needed for Sprint 1 behavior.
   - `tests/unit/test_retrieval.py` may be added only if needed for dense retrieval tests.
   - Do not skip, xfail, or delete tests just to pass.

11. Sprint 1 baseline documentation:
   - Record local dense retrieval latency and/or CLI pipeline latency only if measured from real local command output.
   - If not measured, write `pending` / `placeholder` / blocked reason.
   - Do not fabricate benchmark, RAGAS, Recall@5, faithfulness, cost, QPS, or README metric claims.

## Out Of Scope

- Do not implement hybrid retrieval.
- Do not implement BM25.
- Do not implement RRF.
- Do not implement rerank.
- Do not implement HyDE.
- Do not implement Multi-Query.
- Do not implement Query Decomposition.
- Do not implement Context Builder.
- Do not implement LangGraph main graph.
- Do not implement MCP tool layer.
- Do not implement graph orchestration.
- Do not implement `/api/v1/query`.
- Do not implement `/api/v1/feedback`.
- Do not implement auth.
- Do not implement rate limiting.
- Do not implement observability hardening.
- Do not implement Langfuse.
- Do not implement PostgresSaver.
- Do not implement model router.
- Do not implement SSE.
- Do not implement Streamlit Demo.
- Do not implement cloud deployment.
- Do not implement demo video delivery.
- Do not implement resume paragraph delivery.

## Constraints

- Local-first only.
- Use existing project architecture and dependencies where possible.
- Prefer existing `pyproject.toml` dependencies.
- Do not add new dependencies without stopping for approval.
- Do not commit `.env`, API keys, credentials, runtime artifacts, large data files, model weights, database files, or generated FAISS/artifact output.
- Do not require real API keys.
- Do not require external paid models.
- Do not require cloud services.
- Do not require Docker daemon.
- Do not fabricate benchmark or evaluation results.
- Do not mark README metrics as achieved unless the corresponding commands actually ran.
- Do not rewrite learning notes or remove core architecture positioning.
- Keep manual/non-code deliverables separate from automated code delivery.
- If a dependency, fixture, command, or service is unavailable, record the blocked reason instead of pretending success.
- Keep changes mechanically auditable by Sprint 1 checklist item.
- After each implementation phase, run the relevant available tests or record why they are blocked.

## Done When

- Local Sprint 1 pipeline runs or has a precise local blocked reason: `question -> plan -> retrieve -> synthesize -> answer`.
- Dense evidence objects include `source` metadata.
- PDF evidence includes `page` metadata when available.
- Session artifacts are written for `plan`, `evidence`, and `final_answer`.
- Minimal Planner generates 2-4 subtasks.
- Dedicated Sprint 1 CLI entrypoint `scripts/run_research_loop.py` runs locally or reports a precise blocked reason.
- `/api/v1/ingest` exists without auth.
- `/api/v1/ingest` does not return 501 for a minimal valid local ingest request.
- `/api/v1/ingest` performs basic request validation.
- `/api/v1/ingest` is connected to the Sprint 1 local ingest path or returns a clear local blocked reason when required local sample input is unavailable.
- `tests/unit/test_loaders.py` exists and includes at least 3 loader cases.
- Loader tests pass.
- `tests/unit/test_retrieval.py` passes if the file exists or is added for dense retrieval.
- Sprint 1 documentation contains only measured baseline results or explicitly says `pending` / `placeholder` / blocked reason.
- No Sprint 2-5 implementation has been added.

## Stop If

- A required implementation needs a new dependency not already approved.
- A required implementation needs a real API key.
- A required implementation needs an external paid model.
- A required implementation needs cloud services or Docker daemon.
- Existing tests show regression.
- The diff exceeds a reasonable Sprint 1 scope and there is no phase-by-phase test record.
- Artifact or metadata requirements cannot be validated from local fixtures.
- The available project contracts conflict with this Sprint 1 scope.
- You would need to implement Sprint 2-5 functionality to make Sprint 1 pass.

## First Action

Before modifying any file, read the project core documents and Sprint 1 related Comet spec/plan:

- `README.md`
- `docs/architecture.md`
- `docs/development.md`
- `docs/api.md`
- `docs/benchmark.md`
- `docs/claude-comet-goal-workflow.md`
- `notes/day7/sprint_backlog.md`
- `docs/superpowers/knowledge-ops-sprint-1-5-development-plan.md`
- Any active Sprint 1 OpenSpec / Comet files under `openspec/changes/` if present
- Any Sprint 1 Superpowers spec/plan files under `docs/superpowers/specs/` and `docs/superpowers/plans/` if present
- `pyproject.toml`
- Existing `src/**/*.py`
- Existing `tests/**/*.py`

After reading, report and wait for confirmation before implementation:

1. Sprint 1 checklist count.
2. Current TODO / NotImplementedError / 501 Not implemented count and file distribution.
3. Current tests count and relevant test files.
4. Sprint 1 executable phase breakdown.
5. Any blockers, missing files, or scope conflicts.

Do not start implementation until confirmation is provided.

## Suggested Sprint 1 Executable Phase Breakdown

1. Inspect current contracts and fixtures.
2. Implement or complete loaders and chunking.
3. Implement or complete embedder, FAISS dense index, and dense retrieval.
4. Implement or complete minimal Planner and linear CLI research loop.
5. Implement or complete session artifact persistence.
6. Implement or complete `/api/v1/ingest` local implementation.
7. Add Sprint 1 tests.
8. Run verification commands and update benchmark/docs only from real outputs.
9. Produce final summary.

## Allowed File Modification Range

- `src/ingest/**/*.py`
- `src/retrieval/**/*.py`
- `src/agents/**/*.py` only for Sprint 1 minimal planner, synthesis, artifacts, or linear CLI loop
- `src/api/**/*.py` only for `/api/v1/ingest`
- `src/config.py` only for Sprint 1 local configuration
- `src/main.py` only for wiring `/api/v1/ingest` or app import consistency
- `scripts/ingest_pdfs.py`
- `scripts/run_research_loop.py`
- `tests/unit/test_loaders.py`
- `tests/unit/test_retrieval.py` only if needed for dense retrieval
- `docs/benchmark.md` only for measured Sprint 1 baseline or pending / blocked status
- `README.md` only if needed to correct Sprint 1 actual local behavior, without adding unmeasured claims
- `pyproject.toml` only if configuration alignment is needed for already-present dependencies; stop before adding new dependencies

## Do Not Modify

- Sprint 2-5 implementation modules unless only fixing imports broken by Sprint 1 and the change is minimal.
- `docs/api.md` feedback Sprint assignment during this Sprint 1 implementation.
- Cloud deployment docs.
- Resume/job application/demo video materials.
- Generated runtime artifact directories.
- `.env` or secret files.

## Required Verification Commands

Run the commands that are applicable in this local environment. If a command cannot run because fixtures, services, missing files, or local environment are unavailable, record the exact blocked reason.

1. Loader tests:

   `uv run pytest tests/unit/test_loaders.py`

2. Dense retrieval tests, only if `tests/unit/test_retrieval.py` exists or is added:

   `uv run pytest tests/unit/test_retrieval.py`

3. Ingestion script smoke test, only when a local fixture/sample directory exists:

   `uv run python scripts/ingest_pdfs.py <existing-local-sample-directory>`

   If no local fixture/sample directory exists, do not invent one; record the exact blocked reason.

4. Sprint 1 CLI research loop smoke test:

   `uv run python scripts/run_research_loop.py --question "Summarize the indexed evidence"`

5. API app smoke test:

   `uv run python -c "from src.main import app; print(app.title)"`

6. `/api/v1/ingest` minimal request smoke test:

   Run an in-process FastAPI/TestClient or equivalent local smoke test proving that a minimal valid local ingest request no longer returns 501, performs basic validation, and either reaches the Sprint 1 local ingest path or returns a clear local blocked reason.

7. Optional bounded server startup smoke test only if practical in the local environment:

   `uv run uvicorn src.main:app --reload`

For command 7, do not leave a long-running server process behind. If bounded startup cannot be performed safely, record it as blocked and use command 5 as the import-level API smoke test.

If benchmark documentation is updated, include the exact command output source or mark the benchmark as pending / blocked.

## Continuation And Audit Requirements

- Keep work grouped by the Sprint 1 phase breakdown.
- After each phase, note what changed and which verification command was run or blocked.
- If interrupted, the next run must be able to continue from the last completed phase using the changed files, test output, and final/partial summary.
- Do not claim completion for any checklist item that has not been implemented and verified or explicitly marked blocked.

## Final Summary Requirements

At the end, report:

1. Files changed.
2. Sprint 1 checklist items completed.
3. Verification commands run, with pass/fail/blocked status.
4. Any benchmark values recorded, including the exact command source; if none, say pending or blocked.
5. Any dependencies not added because approval is required.
6. Any blockers or known remaining work.
7. Confirmation that no Sprint 2-5 implementation items were included.
