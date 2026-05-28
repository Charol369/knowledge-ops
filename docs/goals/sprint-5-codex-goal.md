## Objective

完成 KnowledgeOps 最后一轮产品化与交付闭环：streaming query path、feedback capture、demo UI、final benchmark/reporting、README/API 文档收口、deployment/documentation boundary、demo/resume/job-application material preparation boundary。必须基于 Sprint 1-4 已有实现做集成和收口，不能重写前序核心架构。

## Current baseline

- Sprint 1 completed: Minimal Research Loop + Evidence Pipeline.
- Sprint 2 completed: Hybrid Retrieval + Context Engineering.
- Sprint 3 completed: LangGraph Agent Graph + MCP + `/api/v1/query`.
- Sprint 4 completed: Policy Layer + LLMOps + Guardrails.
- Sprint 4 baseline commit: `c568f9e feat: complete sprint 4 policy llmops guardrails`.
- Sprint 5 depends on the existing Sprint 1-4 contracts:
  - local ingest/load/split/embed/index and CLI research loop from Sprint 1;
  - dense/hybrid retrieval, context builder, artifact persistence, benchmark smoke, and RAGAS dry-run scaffold from Sprint 2;
  - LangGraph research graph, citation validation, `/api/v1/query`, and MCP tool layer from Sprint 3;
  - policy routing, guardrails, auth/rate-limit, trace propagation, metrics, optional memory/Langfuse dry-run boundaries from Sprint 4.
- Existing project docs may contain planned or outdated claims. Sprint 5 must reconcile README/API/benchmark docs with actual local behavior and explicitly mark manual or blocked delivery items.
- Treat Docker, cloud deployment, public demo/video upload, real job application submission, real Langfuse/Postgres/Redis, and external paid model access as optional/manual/environment-dependent boundaries unless explicitly available locally without violating this goal.

## Scope

1. Streaming / SSE query path:
   - Implement or complete `/api/v1/query/stream` as the Sprint 5 streaming query endpoint.
   - Reuse the existing `QueryRequest`, graph-backed query contract, Sprint 4 trace/auth/rate-limit behavior where applicable, and local fallback behavior.
   - Emit ordered Server-Sent Events for progress and completion, or return a precise local blocked reason only if the Sprint 5 spec permits the blocked condition.
   - Keep streaming bounded and locally testable through in-process tests or a bounded smoke, not by requiring an unbounded server process.

2. Feedback endpoint:
   - Implement or complete `/api/v1/feedback`.
   - Accept a local valid feedback request with a trace identifier and score/rating/comment fields as appropriate for the current schema.
   - Validate input at the API boundary.
   - Persist/capture feedback locally or record a Langfuse-compatible score only when explicit safe local configuration exists.
   - If Langfuse is not configured, return a deterministic local success or clear configuration status according to the implemented contract; do not emit authentication errors or require real credentials.
   - A valid local request must no longer return `501 Not implemented`.

3. Demo UI:
   - Complete the local Sprint 5 Streamlit demo UI using the existing `frontend/` path if present; do not skip the demo checklist item unless a Stop-if condition or exact blocked reason applies.
   - This Sprint allows adding exactly one new direct dependency: `streamlit`, solely for the Sprint 5 Streamlit demo.
   - Prefer a minimal Streamlit demo that shows the research flow, not just a plain chat box: question input, plan/progress, evidence/citations, final report/answer, trace/session information, and feedback affordance if locally wired.
   - The demo must prefer the existing FastAPI API and must not bypass the backend by reimplementing query/retrieval/agent logic in the frontend.
   - Do not add unrelated UI frameworks, frontend build tools, Node dependencies, or external service SDKs.
   - Keep the demo locally importable/checkable/smokable without requiring an unbounded server process as proof of completion.
   - If installing or locking `streamlit` fails, record the exact blocked reason and do not use external services to work around the failure.

4. Final benchmark/report:
   - Run or preserve the existing Sprint 1-4 benchmark/eval scaffold and add Sprint 5 final reporting only from real command output.
   - Keep Recall@5, RAGAS Faithfulness, Answer Relevancy, P95 latency, cost, and QPS as `_待测_`, `pending`, or `blocked` unless the matching command actually ran and produced that result.
   - Include streaming/feedback/demo benchmark or smoke outputs only if bounded commands actually ran.
   - If Docker, Locust, external services, fixture data, or local environment support is unavailable, record exact blocked reasons instead of fabricating results.

5. README / API docs finalization:
   - Update README.md and docs/api.md so they match actual implemented local behavior.
   - Fix the known API documentation boundary: `/api/v1/feedback` is Sprint 5, not Sprint 4.
   - Remove or qualify unverified claims such as production deployment, public demo, uploaded video, Docker/Langfuse/Milvus success, 100 QPS, achieved P95/cost/quality targets, or final metrics unless backed by real command output.
   - Keep startup commands, schema descriptions, auth/rate-limit behavior, streaming endpoint behavior, feedback endpoint behavior, MCP notes, benchmark commands, and manual delivery boundaries consistent.

6. Deployment boundary:
   - Keep Docker Compose and cloud deployment as documented/manual/environment-dependent boundaries unless the local environment safely supports bounded validation.
   - Do not require Docker daemon, cloud accounts, public deployment, or external services for local acceptance.
   - If deployment files are updated, document what is locally validated, what is planned, and what requires manual external action.

7. Resume / demo video / job application material boundary:
   - Prepare only local drafts, checklists, or documentation boundaries for demo video, resume paragraph, and job application materials if required by the Sprint 5 checklist.
   - Do not upload a video, publish a real demo, submit a job application, update an external profile, or claim those manual actions were completed.
   - Clearly separate code-completed deliverables from manual human actions.

8. Tests:
   - Add or complete Sprint 5 tests for streaming and feedback.
   - Add or complete bounded demo checks where practical.
   - Preserve applicable Sprint 1-4 regression tests.
   - Do not skip, xfail, delete assertions, or weaken tests merely to pass.

## Out of Scope

- Rewriting Sprint 1 loaders, dense index, ingest pipeline, artifact store, or CLI research loop.
- Rewriting Sprint 2 hybrid retrieval, BM25/RRF/rerank/query transform/context builder, RAGAS scaffold, or benchmark baseline.
- Rewriting Sprint 3 LangGraph graph, MCP server/tools, citation validation, reporter/verifier, or `/api/v1/query` except for minimal Sprint 5 compatibility hooks.
- Rewriting Sprint 4 policy routing, guardrails, API key auth, rate limiting, Langfuse dry-run path, optional Postgres/MemorySaver boundary, metrics, or trace propagation except for minimal Sprint 5 integration hooks.
- Adding new real external service dependencies.
- Requiring a real API key.
- Requiring an external paid model.
- Requiring a real Langfuse server or real Langfuse credentials.
- Requiring real Postgres or Redis.
- Requiring Docker daemon.
- Performing cloud deployment.
- Publishing a real public demo.
- Uploading a real demo video.
- Submitting a real job application.
- Adding unlisted new product features.
- Turning manual delivery artifacts into claimed automated completion.

## Constraints

- Local-first: Sprint 5 acceptance must be possible in a local development environment without external paid services.
- Use existing architecture and dependencies where possible.
- This Sprint allows adding exactly one new direct dependency: `streamlit`, solely for the Sprint 5 Streamlit demo.
- Do not add dependencies other than `streamlit` without stopping for approval; if any other dependency is required, report the dependency name, purpose, affected Sprint 5 checklist item, and local alternative.
- Do not commit `.env`, API keys, credentials, runtime artifacts, FAISS index, database files, model weights, cache files, generated demo artifacts, or generated benchmark output directories.
- Do not require real API keys.
- Do not require external paid models.
- Do not require cloud services.
- Do not require Docker daemon.
- Do not require real Redis, real Postgres, or real Langfuse.
- Do not fabricate benchmark, evaluation, demo, deployment, Langfuse, Docker, latency, cost, QPS, or video/job-application results.
- Do not mark README metrics as achieved unless matching commands actually ran.
- Keep manual/non-code deliverables clearly separate from automated code delivery.
- If a fixture, service, dependency, account, Docker daemon, external model, or local environment capability is unavailable, record the exact blocked reason instead of pretending success.
- Keep changes mechanically auditable by Sprint 5 checklist item.
- After each phase, run the relevant available tests or record the exact blocked reason.
- Keep implementation simple and compatible with existing Sprint 1-4 contracts.
- Keep deterministic services deterministic; do not move retrieval, citation, benchmark, feedback persistence, or validation logic into opaque prompts.
- Do not silently expand Sprint 5 into a new architecture or new product scope.
- Do not use unbounded long-running server commands as proof of completion unless wrapped in a bounded local smoke test and recorded accurately.
- No token budget.
- No use limit.

## Done when

- Sprint 5 checklist count is reported from the Sprint 5 spec/plan/tasks/backlog sources, including any discrepancy between sources.
- The first implementation summary maps Sprint 5 checklist items to status and file paths.
- `/api/v1/query/stream` exists and has a bounded local test or smoke proving ordered progress/completion events, or an exact blocked reason if the Sprint 5 spec permits the blocked condition.
- `/api/v1/query/stream` reuses existing query/graph contracts and Sprint 4 auth/rate-limit behavior where applicable.
- `/api/v1/feedback` exists and a local valid request no longer returns `501 Not implemented`.
- `/api/v1/feedback` validates input and persists/captures feedback locally, records a Langfuse-compatible score only when safely configured, or returns an exact local blocked/configuration status without requiring real credentials.
- Feedback and streaming response schemas are documented and locally testable.
- Demo UI exists for the Sprint 5 demo checklist item and can be imported, syntax-checked, or otherwise bounded-smoked; if not runnable locally, the exact blocked reason is recorded.
- Demo UI shows the research flow at least at the level of question, plan/progress, evidence/citations, answer/final report, trace/session metadata, and feedback affordance where locally supported.
- Final benchmark/docs contain only measured values from executed commands or explicit pending/blocked status.
- README.md and docs/api.md are accurate for implemented endpoints, startup commands, auth/rate-limit behavior, streaming, feedback, demo, benchmark, MCP, deployment boundaries, and manual deliverables.
- Manual deliverables are drafts/checklists/boundaries only: demo video, public upload, cloud deployment, resume finalization, and job applications are not claimed as completed automated work.
- Sprint 5 streaming and feedback tests pass if files exist or are added.
- Relevant Sprint 1-4 regression tests pass or have exact blocked reasons tied to local environment constraints, not code regressions.
- No secrets, runtime artifacts, generated demo assets, FAISS index files, database files, model weights, cache files, or credentials are in the worktree changes.
- No out-of-scope rewrites or external-service-dependent implementation was added.
- `git diff --check` passes.

## Stop if

- A required implementation needs a new dependency other than the allowed direct `streamlit` dependency.
- A required implementation needs a real API key.
- A required implementation needs an external paid model.
- A required implementation needs cloud services.
- A required implementation needs Docker daemon.
- A required implementation needs real Redis, real Postgres, or real Langfuse.
- A required implementation needs login to an external account.
- Completing the task would require uploading a video, publishing a demo, submitting a real job application, or changing an external profile.
- Existing Sprint 1-4 tests show a regression caused by Sprint 5 changes.
- Sprint 1-4 contracts conflict with the Sprint 5 implementation requirements.
- The diff exceeds a reasonable Sprint 5 scope without phase-by-phase test records.
- Benchmark, demo, deployment, latency, cost, QPS, or evaluation claims cannot be locally validated by matching commands.
- Making Sprint 5 pass would require rewriting Sprint 1-4 core modules instead of adding Sprint 5 integration and delivery closure.
- The current project docs/specs disagree on a core Sprint 5 requirement and the conflict cannot be resolved by the user's established boundary decisions.
- `streamlit` installation or lock update fails; record the exact blocked reason and do not use external services to work around it.
- `git status` shows `.env`, credentials, runtime artifacts, FAISS indexes, database files, model weights, cache files, or generated demo artifacts entering the change set.

## First action

Before modifying any file, read the project core documents, Sprint 5 Comet/OpenSpec spec/plan, existing Sprint goal files, current source/test code, frontend/demo files, and deployment docs if present:

- README.md
- docs/architecture.md
- docs/development.md
- docs/api.md
- docs/benchmark.md
- docs/claude-comet-goal-workflow.md
- notes/day7/sprint_backlog.md
- docs/superpowers/knowledge-ops-sprint-1-5-development-plan.md
- docs/superpowers/plans/2026-05-27-sprint-5-*.md
- docs/superpowers/specs/2026-05-27-sprint-5-*.md
- openspec/changes/sprint-5-*/proposal.md
- openspec/changes/sprint-5-*/design.md
- openspec/changes/sprint-5-*/tasks.md
- openspec/changes/sprint-5-*/specs/**/spec.md
- docs/goals/sprint-1-codex-goal.md
- docs/goals/sprint-2-codex-goal.md
- docs/goals/sprint-3-codex-goal.md
- docs/goals/sprint-4-codex-goal.md
- pyproject.toml
- src/**/*.py
- tests/**/*.py
- frontend/**/* if present
- demo/**/* if present
- Dockerfile, docker-compose.yml, deployment docs, and scripts/eval files if present

After reading, report and continue execution without waiting for confirmation:

1. Sprint 5 checklist count from the Sprint 5 spec/plan/tasks/backlog sources, including any count discrepancy.
2. Current TODO / NotImplementedError / `501 Not implemented` count and file distribution, with emphasis on streaming, feedback, frontend/demo, docs, benchmark, and deployment boundary files.
3. Current tests count and relevant Sprint 5 test files, including whether `tests/integration/test_streaming.py` and `tests/integration/test_feedback.py` exist.
4. Sprint 5 executable phase breakdown for the current repository state.
5. Blockers, missing files, or scope conflicts.
6. Confirmation that execution will continue automatically unless a Stop-if condition is reached.

## Executable phase breakdown

1. Inspect current Sprint 1-4 contracts and Sprint 5 target files:
   - API schemas/routes/main app middleware;
   - graph/query behavior and trace propagation;
   - observability/Langfuse dry-run interfaces;
   - frontend/demo files;
   - benchmark/eval scripts;
   - README/docs/api/docs/benchmark;
   - tests and fixtures.

2. Implement or complete streaming query path:
   - add bounded `/api/v1/query/stream` behavior;
   - reuse existing graph/query contracts;
   - emit deterministic ordered SSE events;
   - preserve applicable auth/rate-limit behavior;
   - add local integration tests.

3. Implement or complete feedback capture:
   - add request/response schemas;
   - add `/api/v1/feedback` route;
   - validate boundary input;
   - record feedback locally or via safe configured Langfuse-compatible path;
   - avoid real credential/network requirements;
   - add local integration tests.

4. Complete demo UI boundary:
   - update existing `frontend/` demo if present;
   - show plan/progress/evidence/final answer/trace and feedback affordance;
   - keep bounded smoke/import/syntax checks;
   - record dependency or runtime blockers precisely.

5. Complete final benchmark/reporting boundary:
   - run available benchmark/eval commands;
   - add or update Sprint 5 benchmark scripts only if required and within existing dependencies;
   - update docs/benchmark.md only with real outputs or pending/blocked status.

6. Finalize README and API docs:
   - sync implemented endpoints and schemas;
   - fix `/api/v1/feedback` Sprint boundary;
   - remove or qualify unverified production, Docker, cloud, public demo, video, QPS, P95, cost, and quality claims;
   - document manual deliverable boundaries.

7. Validate deployment/manual-delivery boundaries:
   - document Docker/cloud constraints without requiring Docker or cloud;
   - prepare local drafts/checklists for video/resume/job-application materials because they are Sprint 5 checklist items;
   - keep these separate from code completion.

8. Run verification commands:
   - run Sprint 5 tests;
   - run relevant Sprint 1-4 regressions;
   - run bounded demo/API smokes;
   - run benchmark commands where available;
   - run full test suite and diff hygiene if local environment permits.

9. Produce final summary:
   - map Sprint 5 checklist items to status and file paths;
   - list commands run and outputs;
   - list measured vs pending/blocked metrics;
   - list manual deliverables still requiring human action;
   - confirm no Sprint 1-4 rewrites or out-of-scope external work.

## Allowed file modification range

- src/api/routes.py for Sprint 5 streaming and feedback endpoints, plus minimal integration with existing auth/rate-limit/trace behavior.
- src/api/schemas.py for Sprint 5 streaming/feedback request and response schemas.
- src/main.py only for minimal Sprint 5 route/middleware compatibility if strictly required.
- src/observability/**/*.py only for safe local feedback score recording or Langfuse-compatible dry-run integration required by `/api/v1/feedback`.
- src/agents/**/*.py only for minimal streaming progress, trace, or query contract compatibility required by `/api/v1/query/stream`.
- src/guardrails/**/*.py only for minimal Sprint 5 API boundary compatibility if required.
- src/policy.py only for minimal Sprint 5 auth/rate-limit/policy compatibility if required.
- frontend/**/* for the Sprint 5 demo UI.
- demo/**/* if the repository already uses or requires a demo directory.
- tests/integration/test_streaming.py and related integration fixtures for streaming.
- tests/integration/test_feedback.py and related integration fixtures for feedback.
- tests/unit/**/*.py only for Sprint 5 unit coverage directly tied to streaming, feedback, demo helper logic, or benchmark/doc helper logic.
- tests/integration/**/*.py only for Sprint 5 integration coverage and required regressions.
- scripts/benchmark.py and eval/**/* only for Sprint 5 benchmark/final evaluation work using existing dependencies.
- docs/api.md for final API documentation sync.
- docs/benchmark.md for real Sprint 5 outputs or pending/blocked status.
- README.md for final behavior sync and manual boundary documentation.
- Dockerfile and docker-compose.yml only for documentation-level or configuration consistency fixes that do not require Docker acceptance.
- docs/deployment*.md or docs/deployment/**/* if such files exist or are strictly needed to document deployment boundary.
- docs/demo*.md, docs/resume*.md, or docs/delivery*.md only if strictly needed for Sprint 5 manual deliverable drafts/checklists and not as fabricated completion proof.
- pyproject.toml and uv.lock only for adding and locking the allowed direct `streamlit` dependency; otherwise do not modify them.
- Minimal compatibility adjustments in Sprint 1-4 files only when strictly required for Sprint 5 integration.

## Do not modify

- Sprint 1 ingest/retrieval/artifact/CLI implementations except for minimal Sprint 5 compatibility explicitly justified.
- Sprint 2 hybrid retrieval/context/RAGAS/benchmark baseline implementations except for minimal Sprint 5 compatibility explicitly justified.
- Sprint 3 graph/MCP/citation validation implementations except for minimal Sprint 5 streaming compatibility explicitly justified.
- Sprint 4 policy/guardrails/auth/rate-limit/Langfuse dry-run/memory/metrics implementations except for minimal Sprint 5 feedback/streaming compatibility explicitly justified.
- `notes/` learning notes except for referencing them; do not rewrite learning plans.
- `.env` or any secret/credential files.
- runtime artifact directories.
- FAISS index files.
- database files.
- model weights.
- cache directories/files.
- generated demo assets.
- generated benchmark output artifacts unless explicitly intended and safe to track.
- external account state, cloud resources, public demo hosting, uploaded videos, resumes on external sites, or job applications.

## Required verification commands

Run the commands that are applicable in this local environment. If a command cannot run because files, fixtures, services, local environment, dependencies, Docker daemon, external accounts, or configuration are unavailable, record the exact blocked reason.

1. Streaming integration tests, if the file exists or is added in Sprint 5:
   `uv run pytest tests/integration/test_streaming.py`

2. Feedback integration tests, if the file exists or is added in Sprint 5:
   `uv run pytest tests/integration/test_feedback.py`

3. Demo UI bounded smoke/import/check, if `frontend/app.py` exists or is added:
   `uv run python -m py_compile frontend/app.py`

   Optional bounded Streamlit import smoke after adding the allowed dependency:
   `uv run python -c "import streamlit; print(streamlit.__version__)"`

   Do not use `uv run streamlit run frontend/app.py` as a required acceptance command or proof of success unless it is wrapped in a bounded local smoke that exits; otherwise record it as blocked because it starts an interactive long-running server.

4. Existing query API regression:
   `uv run pytest tests/integration/test_query_api.py`

5. Existing auth/rate-limit regression:
   `uv run pytest tests/integration/test_auth_rate_limit.py`

6. Existing graph/MCP regression:
   `uv run pytest tests/unit/test_agents.py tests/integration/test_mcp_server.py`

7. Existing retrieval/context regression:
   `uv run pytest tests/unit/test_retrieval.py tests/unit/test_context_builder.py`

8. Existing policy/guardrails/observability/memory regression:
   `uv run pytest tests/unit/test_policy.py tests/unit/test_guardrails.py tests/unit/test_observability.py tests/unit/test_memory.py`

9. FastAPI app import smoke:
   `uv run python -c "from src.main import app; print(app.title)"`

10. API route smoke for `/api/v1/feedback` using in-process TestClient or equivalent bounded command, for example:
    `uv run python -c "from fastapi.testclient import TestClient; from src.main import app; client = TestClient(app); response = client.post('/api/v1/feedback', json={'trace_id':'sprint5-smoke','score':1}); print(response.status_code); print(response.text[:300])"`

11. API route smoke for `/api/v1/query/stream` using in-process TestClient or equivalent bounded command, for example:
    `uv run python -c "from fastapi.testclient import TestClient; from src.main import app; client = TestClient(app); response = client.post('/api/v1/query/stream', json={'question':'Sprint 5 smoke question','thread_id':'sprint5-stream-smoke'}); print(response.status_code); print(response.headers.get('content-type')); print(response.text[:500])"`

12. Existing benchmark command:
    `uv run python scripts/benchmark.py --retrieval dense,hybrid --top-k 5`

13. Any Sprint 5 required benchmark/eval command that exists and is bounded locally. If Locust is required by docs but unavailable, unconfigured, too long-running, or requires a running server/Docker/external service, record the exact blocked reason instead of fabricating QPS/P95 results.

14. Full test suite:
    `uv run pytest -q`

15. Diff hygiene:
    `git diff --check`

Do not run unbounded server commands as proof of success unless they are wrapped in bounded local smokes and the result is recorded accurately.

## Continuation and audit requirements

- Keep work grouped by the Sprint 5 phase breakdown.
- After each implementation phase, note what changed and which verification command was run or blocked.
- Keep a checklist mapping from Sprint 5 backlog/spec/task items to implementation status and file paths.
- If interrupted, the next run must be able to continue from the last completed phase using changed files, test output, and partial summary.
- Do not claim completion for any checklist item that has not been implemented and verified or explicitly marked pending/blocked/manual.
- Do not silently expand Sprint 5 to include new product features or Sprint 1-4 rewrites.
- Do not skip, xfail, delete, or weaken tests merely to pass.
- Do not mark benchmark, deployment, public demo, video, resume, or job-application work as complete unless it is actually completed within the safe local/manual boundary described here.
- Maintain a phase-by-phase verification record in the final summary.
- Unless a Stop-if condition is reached, continue automatically through phases without waiting for human confirmation.

## Final summary requirements

At the end, report:

1. Files changed.
2. Sprint 5 checklist items completed, pending, blocked, or manual, with corresponding file paths.
3. Verification commands run, with pass/fail/blocked status and exact outputs or summaries.
4. Streaming endpoint behavior and local test/smoke result.
5. Feedback endpoint behavior and local test/smoke result.
6. Demo UI status and bounded smoke/import/check result.
7. Benchmark, metric, trace, demo, Docker, deployment, and evaluation values recorded, including exact command source; if not measured, say pending or blocked with exact reason.
8. README/API/benchmark documentation sync summary.
9. Dependencies not added because approval is required, if any.
10. Blockers or known remaining work.
11. Manual deliverables requiring human action: cloud deployment, public demo, video upload, resume finalization, and job applications.
12. Confirmation that no Sprint 1-4 core rewrites, unapproved dependencies, secrets, runtime artifacts, external-service requirements, or unlisted product features were included.
