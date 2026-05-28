You are implementing Sprint 4 only for KnowledgeOps: Policy Layer + LLMOps + Guardrails.

Do not implement Sprint 5 work. Do not expand scope.

Objective:
Complete the Sprint 4 production-control layer on top of the completed Sprint 1-3 baseline: local ingest, dense/hybrid retrieval, context builder, artifact persistence, benchmark smoke, RAGAS dry-run scaffold, LangGraph research graph, citation validation, `/api/v1/query`, and MCP tool layer.

Sprint 4 must make policy routing, LLMOps integration paths, guardrails, trace propagation, business metrics, API key auth, and rate limiting locally testable without requiring real cloud services, real paid models, real API keys, Docker, Redis, Postgres, or a real Langfuse server.

Current baseline:

- Sprint 1 completed at commit `80f8590`: minimal research loop and evidence pipeline.
- Sprint 2 completed at commit `c56cbc6`: dense/hybrid retrieval, context builder, artifact persistence, benchmark smoke, and RAGAS dry-run scaffold.
- Sprint 3 completed at commit `b347f74`: LangGraph research graph, citation validation, `/api/v1/query`, and MCP tool layer.
- Current repository state includes Sprint 4 skeletons in `src/policy.py`, `src/guardrails/injection.py`, `src/observability/langfuse_setup.py`, and `src/observability/metrics.py`.
- Treat Sprint 1-3 contracts as dependencies. Do not redo ingest, retrieval, context building, artifact persistence, graph execution, citation validation, `/api/v1/query`, or MCP tools except for minimal compatibility changes directly required for Sprint 4 integration.

Scope:

1. Complexity Classifier:

   - Implement or complete a locally callable complexity classifier.
   - Keep it deterministic and testable without external model calls.
   - Ensure classification decisions can be recorded for observability/business metrics.

2. Model Router:

   - Implement or complete a locally callable model router.
   - Route by complexity and policy decision without requiring real paid models.
   - Preserve compatibility with existing graph state fields such as `complexity`, `model_tier`, and `trace_id`.

3. Cache / Retry / Fallback strategy:

   - Implement deterministic local cache/retry/fallback policy primitives where they fit the current architecture.
   - Do not hide unsupported final failures.
   - If a specific cache/retry/fallback integration needs a new dependency or external service, record a precise blocked reason instead of adding it.

4. Langfuse integration path and callbacks:

   - Keep Langfuse integration importable and dry-run safe.
   - Default local tests must not trigger real Langfuse network connections or real authentication.
   - If explicit local configuration is unavailable, `get_langfuse_handler()` must safely return `None` or a disabled/noop handler without emitting authentication errors.
   - Use a real `CallbackHandler` only when explicitly configured and doing so does not violate Sprint 4 Stop if conditions.
   - Propagate callback/trace hooks through graph/API boundaries where feasible without requiring a real Langfuse server.
   - Do not require real Langfuse credentials, real Langfuse network success, or a running Langfuse service for local acceptance.
   - If the current implementation is not dry-run safe, fix `src/observability/langfuse_setup.py` so missing real configuration safely disables Langfuse instead of producing external authentication errors.

5. `trace_id` propagation:

   - Ensure `trace_id` can propagate through graph execution and API responses.
   - Preserve existing Sprint 3 `trace_id` behavior and extend only where Sprint 4 policy/observability needs it.

6. Business metrics:

   - Implement local business metric recording or dry-run collection for policy decisions, model tier usage, fallback usage, guardrail decisions, and citation/verification outcomes where feasible.
   - Keep metrics independent of a real external metrics backend.

7. Prompt injection detection:

   - Implement or complete two-level injection detection at the Sprint 4 boundary.
   - First level must be deterministic/local.
   - Any second-level model-judge path must be optional and must return a precise blocked reason if it would require a real API key or paid external model.

8. Unicode normalization:

   - Implement local Unicode normalization for guardrail input handling.
   - Ensure confusable or normalized injection-like input can be locally tested.

9. PostgresSaver optional path:

   - Provide or document the optional PostgresSaver boundary when configuration is present.
   - Do not require a real Postgres server, Docker daemon, or database service for local acceptance.
   - Keep `MemorySaver` as the local default unless an optional configured Postgres path is explicitly available.

10. API key auth:

   - Implement or complete API key auth for Sprint 4 applicable protected endpoints.
   - Use local test configuration or in-process dependency overrides; do not require a real external secret manager.
   - Do not leak expected secret values in error responses.

11. Rate limit middleware:

   - Implement or complete local rate limiting for Sprint 4 applicable API paths.
   - Do not require a real Redis server.
   - If Redis-backed rate limiting is only a future production option, record it as optional/pending and keep local acceptance in-memory or deterministic.

12. Observability / scoring foundation:

   - Prepare the lower-level observability/scoring capabilities needed by later feedback work.
   - Do not implement the final `/api/v1/feedback` endpoint in Sprint 4.

13. Sprint 4 tests:

   - Add or complete local tests for policy, guardrails, observability dry-run, API key auth, and rate limiting.
   - All Sprint 4 tests added or modified in this Sprint must pass.
   - At least one Sprint 4 policy / guardrails / auth / observability test file must exist and pass.
   - Do not skip, xfail, or delete existing tests to make Sprint 4 pass.

14. Docs and architecture records:

   - Add ADR 005 and ADR 006 in the repository's existing ADR location.
   - Keep Sprint 4 documentation sync limited to README.md, docs/benchmark.md, and ADRs unless a narrower required doc update is explicitly justified.
   - Update README.md only if needed to reflect real Sprint 4 behavior without unmeasured claims.
   - Update docs/benchmark.md only with real command output or explicit pending / blocked status.

Out of Scope:

- Do not implement `/api/v1/query/stream`.
- Do not implement `/api/v1/feedback` endpoint.
- Do not implement final feedback API behavior.
- Do not implement SSE streaming.
- Do not implement Streamlit demo.
- Do not implement docker-compose final integration.
- Do not implement cloud deployment.
- Do not implement final benchmark.
- Do not implement README v2.0 finalization.
- Do not implement demo video.
- Do not implement resume paragraph.
- Do not perform real external account operations.
- Do not require a real Langfuse server.
- Do not require a real Postgres server.
- Do not require a real Redis server.
- Do not add Sprint 5 features as hidden prerequisites.

Constraints:

- Sprint 1-3 must remain the dependency baseline.
- Keep compatibility with existing ingest, retrieval, context builder, artifact, graph, citation, API query, MCP, benchmark, and eval contracts.
- Use existing project architecture and dependencies where possible.
- Do not introduce generic product, deployment, streaming, UI, feedback, or cloud abstractions beyond Sprint 4 policy/LLMOps/guardrails needs.
- Do not add new dependencies without stopping for approval.
- Do not require real API keys.
- Do not require external paid models.
- Do not require cloud services.
- Do not require Docker daemon.
- Do not require real Redis, real Postgres, or real Langfuse services for local acceptance.
- Do not fabricate metrics, benchmark results, evaluation scores, trace propagation, guardrail decisions, auth/rate-limit results, or Langfuse/Postgres success.
- Do not mark README or docs metrics as achieved unless the corresponding commands actually ran.
- If a local model, dependency, fixture, optional service path, or external integration is unavailable, record the exact blocked reason instead of pretending success.
- Keep changes mechanically auditable by Sprint 4 checklist item.
- After each implementation phase, run the relevant available tests or record why they are blocked.

Done when:

- Complexity Classifier is locally callable and covered by a local test.
- Model Router is locally callable, covered by a local test, and does not force real paid model access.
- Cache / Retry / Fallback strategy has a local testable implementation or a precise blocked reason tied to an unapproved dependency or unavailable optional service.
- `trace_id` can propagate through graph/API response paths and is covered by a local test or existing regression test.
- Business metrics can be recorded locally or dry-run locally without an external metrics backend.
- Prompt injection detection is locally testable.
- Unicode normalization is locally testable.
- API key auth is locally testable and does not require a real external secret.
- Rate limit middleware is locally testable and does not require real Redis.
- Langfuse integration path can be imported, dry-run tested, or precisely marked blocked without requiring a real Langfuse server.
- PostgresSaver remains an optional configured path; local acceptance does not require a real database service.
- At least one Sprint 4 policy / guardrails / auth / observability test file exists and passes.
- All Sprint 4 tests added or modified in this Sprint pass.
- Existing Sprint 1-3 regression tests that are applicable to modified areas pass, or are recorded with precise blocked reasons.
- ADR 005 and ADR 006 are added in the existing ADR location.
- docs/benchmark.md and README.md, if updated, contain only real outputs or explicit pending / blocked status.
- No Sprint 5 implementation items have been added.

Stop if:

- A required implementation needs a new dependency not already approved.
- A required implementation needs a real API key.
- A required implementation needs an external paid model.
- A required implementation needs cloud services, Docker daemon, real Redis, real Postgres, or a real Langfuse server.
- Existing tests show regression.
- Required existing graph/API/retrieval/context regression tests are skipped without a precise blocked reason.
- The diff exceeds a reasonable Sprint 4 scope and there is no phase-by-phase test record.
- The available project contracts conflict with this Sprint 4 scope.
- You would need to implement Sprint 5 functionality to make Sprint 4 pass.

First action:
Before modifying any implementation file, read the project core documents, Sprint 4 plan/spec, and current source/test code:

- README.md
- docs/architecture.md
- docs/development.md
- docs/api.md
- docs/benchmark.md
- docs/claude-comet-goal-workflow.md
- notes/day7/sprint_backlog.md
- docs/superpowers/plans/2026-05-27-sprint-4-policy-llmops-guardrails-plan.md
- docs/superpowers/specs/2026-05-27-sprint-4-policy-llmops-guardrails-design.md
- openspec/changes/sprint-4-policy-llmops-guardrails/proposal.md
- openspec/changes/sprint-4-policy-llmops-guardrails/design.md
- openspec/changes/sprint-4-policy-llmops-guardrails/specs/knowledge-ops-sprint-4/spec.md
- openspec/changes/sprint-4-policy-llmops-guardrails/tasks.md
- src/**/*.py
- tests/**/*.py

After reading, report and continue execution without waiting for confirmation:

1. Sprint 4 checklist count.
2. Current TODO / NotImplementedError / 501 Not implemented count, with emphasis on policy / observability / guardrails / API distribution.
3. Current tests count and policy / guardrails / observability / API auth/rate-limit coverage overview.
4. Sprint 1-3 completed capabilities and Sprint 4 dependencies.
5. Any blockers, missing files, or scope conflicts.

Suggested Sprint 4 executable phase breakdown:

1. Inspect current policy, guardrail, observability, graph, API, config, and test contracts.
2. Implement or complete Complexity Classifier, Model Router, and deterministic Cache / Retry / Fallback policy primitives.
3. Implement or complete Unicode normalization and two-level prompt injection detection with local-only default behavior.
4. Implement or complete trace_id propagation, local business metrics, and Langfuse import/dry-run integration path.
5. Implement or document optional PostgresSaver path without requiring a real database service; keep local MemorySaver default when no configured service is available.
6. Implement or complete API key auth and local rate limiting without real external secrets or Redis.
7. Add Sprint 4 policy / guardrails / auth / rate-limit / observability tests.
8. Run verification commands and update benchmark/docs only from real outputs or explicit blocked status.
9. Add ADR 005 and ADR 006.
10. Produce final summary.

Allowed file modification range:

- src/policy.py
- src/guardrails/**/*.py
- src/observability/**/*.py
- src/config.py only for Sprint 4 local configuration needed by policy/auth/rate-limit/observability optional paths
- src/main.py only for Sprint 4 middleware wiring needed by auth/rate-limit/trace behavior
- src/api/routes.py and src/api/schemas.py only for API key auth, rate limit, trace_id, and other directly related Sprint 4 request/response behavior
- src/agents/**/*.py only for trace_id / callback / policy hook / optional checkpointer compatibility required by Sprint 4
- tests/unit/**/*.py only for Sprint 4 policy / guardrails / auth / rate-limit / observability unit coverage
- tests/integration/**/*.py only for Sprint 4 policy / guardrails / auth / rate-limit / observability integration coverage
- docs/benchmark.md only for real Sprint 4 smoke results or pending / blocked status
- README.md only for real Sprint 4 behavior sync
- docs/decisions/**/*.md for ADR 005 and ADR 006, following the repository's existing ADR location
- minimal compatibility adjustments in Sprint 1-3 files only when strictly required for Sprint 4 integration

Do not modify:

- Sprint 5 implementation modules.
- `/api/v1/feedback`, SSE streaming, Streamlit demo, cloud deployment, final benchmark, final README v2.0, demo video, resume, or external account materials.
- ingest/retrieval/context/graph/MCP implementations except for minimal Sprint 4 compatibility hooks explicitly listed above.
- generated runtime artifact directories.
- .env or secret files.

Required verification commands:
Run the commands that are applicable in this local environment. If a command cannot run because fixtures, services, missing files, local environment, or dependencies are unavailable, record the exact blocked reason.

1. Policy unit tests, if the file exists or is added in Sprint 4:
   uv run pytest tests/unit/test_policy.py

2. Guardrails unit tests, if the file exists or is added in Sprint 4:
   uv run pytest tests/unit/test_guardrails.py

3. Observability unit tests, if the file exists or is added in Sprint 4:
   uv run pytest tests/unit/test_observability.py

4. API auth/rate-limit integration tests, if the file exists or is added in Sprint 4:
   uv run pytest tests/integration/test_auth_rate_limit.py

5. Observability integration tests, if the file exists or is added in Sprint 4:
   uv run pytest tests/integration/test_observability.py

6. Existing Sprint 3 graph/API/MCP regression tests:
   uv run pytest tests/unit/test_agents.py tests/integration/test_query_api.py tests/integration/test_mcp_server.py

7. Existing Sprint 2 retrieval/context regression tests:
   uv run pytest tests/unit/test_retrieval.py tests/unit/test_context_builder.py

8. FastAPI app import smoke test:
   uv run python -c "from src.main import app; print(app.title)"

9. Policy import/local smoke test:
   uv run python -c "from src.policy import ComplexityClassifier, ModelRouter, FallbackPolicy; print('policy-import-ok')"

10. Guardrails import/local smoke test:
   uv run python -c "from src.guardrails.injection import detect_injection; print(detect_injection('hello')[0])"

11. Observability import/dry-run smoke test:
   uv run python -c "from src.observability.langfuse_setup import get_langfuse_handler; handler = get_langfuse_handler(); print('langfuse-disabled' if handler is None else 'langfuse-configured')"

   `langfuse-disabled` is the acceptable local default. `langfuse-configured` only means local configuration exists; it does not prove or require real Langfuse server acceptance. Do not require real Langfuse connection success for Sprint 4 acceptance, and do not treat authentication errors as passing.

Do not run unbounded server commands as proof of success unless wrapped in a bounded local smoke test and recorded accurately.

Continuation and audit requirements:

- Keep work grouped by the Sprint 4 phase breakdown.
- After each phase, note what changed and which verification command was run or blocked.
- If interrupted, the next run must be able to continue from the last completed phase using the changed files, test output, and final/partial summary.
- Do not claim completion for any checklist item that has not been implemented and verified or explicitly marked blocked.
- Do not silently expand Sprint 4 to include Sprint 5 dependencies.
- Do not skip, xfail, or delete tests merely to pass.
- Unless a Stop if condition or explicit blocker is reached, do not pause between phases for human confirmation.

Final summary requirements:
At the end, report:

1. Files changed.
2. Sprint 4 checklist items completed.
3. Verification commands run, with pass/fail/blocked status.
4. Any benchmark, metric, trace, or smoke values recorded, including the exact command source; if none, say pending or blocked.
5. Any dependencies not added because approval is required.
6. Any blockers or known remaining work.
7. Confirmation that no Sprint 5 implementation items were included.
