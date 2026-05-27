You are implementing Sprint 3 only for KnowledgeOps: LangGraph Agent Graph + MCP Tool Layer.

Do not implement Sprint 4-5 work. Do not expand scope.

Objective:
Complete the Sprint 3 LangGraph Agent Graph and MCP Tool Layer on top of the completed Sprint 1-2 baseline: local ingest, dense retrieval, hybrid retrieval, context builder, artifact persistence, benchmark smoke, and RAGAS dry-run scaffold.

Sprint 3 must make the research-agent graph, structured cited outputs, MCP tools, and `/api/v1/query` graph integration locally testable without requiring cloud services, paid models, Docker, databases, auth, rate limiting, streaming, or production observability.

Current baseline:

- Sprint 1 completed at commit `80f8590`: minimal research loop and evidence pipeline.
- Sprint 2 completed at commit `c56cbc6`: dense/hybrid retrieval, context builder, artifact persistence, benchmark smoke, and RAGAS dry-run scaffold.
- Treat Sprint 1-2 contracts as dependencies. Do not redo ingest, retrieval, context building, or artifact persistence except for minimal compatibility changes directly required for Sprint 3 integration.

Scope:

1. LangGraph main graph:

   - Implement or complete the Sprint 3 graph execution path:
     `plan -> retrieve -> synthesize -> report -> verify`.
   - Keep graph state auditable and compatible with existing Sprint 1-2 artifact and retrieval contracts.
   - Use local `MemorySaver` checkpointing only.
   - Do not introduce `PostgresSaver`.

2. Agent nodes:

   - Implement or complete Planner Node, Retrieval Orchestrator, Synthesizer, Reporter, and Verifier / Reflection at the Sprint 3 boundary.
   - Planner must remain compatible with the Sprint 1 2-4 subtask baseline.
   - Retrieval Orchestrator must call Sprint 2 retrieval/context services rather than reimplement retrieval.
   - Synthesizer and Reporter must produce grounded, citation-ready output.
   - Verifier must validate citations and evidence grounding rather than fabricate confidence.

3. Structured output:

   - Use existing Pydantic schema surfaces where possible.
   - Ensure graph-backed responses validate against explicit structured output models.
   - If an output cannot be validated, return a precise blocked or validation failure reason.

4. Citation validation and evidence grounding:

   - Implement or complete citation extraction and validation.
   - Validate citations against retrieved/context evidence metadata.
   - Reject or flag unsupported citations.
   - Preserve source metadata in graph state and response output.

5. MCP Tool Layer:

   - Implement or complete MCP server tools that expose Sprint 3 retrieval and synthesis capabilities.
   - Keep MCP tools locally callable.
   - MCP tools must connect to retrieval/context/synthesis services, not directly invent answers.
   - Add local smoke coverage for MCP tool behavior where feasible.
   - Claude Desktop client configuration remains a manual boundary; document exact pending or manual status instead of claiming end-to-end Desktop completion.

6. `/api/v1/query` integration:

   - Connect `/api/v1/query` to the Sprint 3 graph.
   - The endpoint must no longer return 501 for a minimal valid research query.
   - Keep the endpoint local and synchronous for Sprint 3.
   - Do not add auth, rate limiting, SSE streaming, feedback handling, or production policy routing.

7. Sprint 3 tests:

   - Add or complete local tests for graph execution, citation validation, `/api/v1/query`, and MCP behavior.
   - All Sprint 3 graph / MCP / API tests added or modified in this Sprint must pass.
   - At least one Sprint 3 graph / MCP / API test file must exist and pass.
   - Do not skip, xfail, or delete existing tests to make Sprint 3 pass.

8. Docs and architecture records:

   - Add ADR 004 and ADR 007 in the repository's existing ADR location.
   - Sync Sprint 3 behavior into docs only from real local runs or explicit pending / blocked status.
   - Update README.md only if needed to reflect real Sprint 3 behavior without unmeasured claims.
   - Update docs/benchmark.md only with real command output or explicit pending / blocked status.

Out of Scope:

- Do not implement Sprint 4 policy layer.
- Do not implement Complexity Classifier.
- Do not implement Model Router.
- Do not implement cache / retry / fallback hardening beyond what is strictly needed for local Sprint 3 tests.
- Do not implement Langfuse observability hardening.
- Do not implement API key auth.
- Do not implement rate limiting.
- Do not implement PostgresSaver.
- Do not implement `/api/v1/feedback`.
- Do not implement SSE streaming.
- Do not implement Streamlit demo.
- Do not implement cloud deployment.
- Do not implement Sprint 5 benchmark or final README claims.
- Do not implement demo video, resume, job application, or external account tasks.
- Do not add Sprint 4-5 features as hidden prerequisites.

Constraints:

- Sprint 1-2 must remain the dependency baseline.
- Keep compatibility with existing loader, dense/hybrid retrieval, context builder, artifact, and benchmark/eval contracts.
- Use existing project architecture and dependencies where possible.
- Do not introduce generic service, policy, auth, observability, deployment, streaming, or UI abstractions beyond Sprint 3 graph/MCP/API needs.
- Do not add new dependencies without stopping for approval.
- Do not require real API keys.
- Do not require external paid models.
- Do not require cloud services.
- Do not require Docker daemon.
- Do not require database services for local acceptance.
- Do not fabricate metrics, benchmark results, evaluation scores, citation validation, or MCP/Claude Desktop success.
- Do not mark README or docs metrics as achieved unless the corresponding commands actually ran.
- If a local model, dependency, fixture, or MCP client integration is unavailable, record the exact blocked reason instead of pretending success.
- Keep changes mechanically auditable by Sprint 3 checklist item.
- After each implementation phase, run the relevant available tests or record why they are blocked.

Done when:

- LangGraph graph builds and invokes locally, or returns a precise blocked reason tied to a missing local dependency/fixture.
- Graph executes the Sprint 3 chain `plan -> retrieve -> synthesize -> report -> verify` for a local test query.
- Graph uses Sprint 2 retrieval/context builder contracts rather than reimplementing retrieval.
- Local `MemorySaver` checkpointing is used where checkpointing is needed.
- Structured output schema validation runs for graph-backed responses.
- Citation extraction and validation run against retrieved/context evidence metadata.
- Unsupported citations are rejected or explicitly flagged.
- MCP tools are locally callable or have precise blocked reasons.
- `/api/v1/query` no longer returns 501 for a minimal valid query and connects to the Sprint 3 graph.
- All Sprint 3 graph / MCP / API tests added or modified in this Sprint pass.
- At least one Sprint 3 graph / MCP / API test file exists and passes.
- ADR 004 and ADR 007 are added in the existing ADR location.
- docs/benchmark.md and README.md, if updated, contain only real outputs or explicit pending / blocked status.
- No Sprint 4-5 implementation items have been added.

Stop if:

- A required implementation needs a new dependency not already approved.
- A required implementation needs a real API key.
- A required implementation needs an external paid model.
- A required implementation needs cloud services, Docker daemon, or database services.
- Existing tests show regression.
- Required existing retrieval/context regression tests are skipped without a precise blocked reason.
- The diff exceeds a reasonable Sprint 3 scope and there is no phase-by-phase test record.
- Artifact, retrieval, context, graph, API, or MCP contracts cannot be validated from local fixtures.
- The available project contracts conflict with this Sprint 3 scope.
- You would need to implement Sprint 4-5 functionality to make Sprint 3 pass.

First action:
Before modifying any implementation file, read the project core documents, Sprint 3 plan/spec, and current agent/API/MCP/test code:

- README.md
- docs/architecture.md
- docs/development.md
- docs/api.md
- docs/benchmark.md
- docs/claude-comet-goal-workflow.md
- notes/day7/sprint_backlog.md
- docs/superpowers/plans/2026-05-27-sprint-3-agent-graph-mcp-plan.md
- docs/superpowers/specs/2026-05-27-sprint-3-agent-graph-mcp-design.md
- openspec/changes/sprint-3-agent-graph-mcp/proposal.md
- openspec/changes/sprint-3-agent-graph-mcp/design.md
- openspec/changes/sprint-3-agent-graph-mcp/specs/knowledge-ops-sprint-3/spec.md
- openspec/changes/sprint-3-agent-graph-mcp/tasks.md
- src/**/*.py
- tests/**/*.py

After reading, report and continue execution without waiting for confirmation:

1. Sprint 3 checklist count.
2. Current TODO / NotImplementedError / 501 Not implemented count, with emphasis on agents / graph / MCP / API distribution.
3. Current tests count and graph / MCP / API coverage overview.
4. Sprint 1-2 completed capabilities and Sprint 3 dependencies.
5. Any blockers, missing files, or scope conflicts.

Suggested Sprint 3 executable phase breakdown:

1. Inspect current graph, agent node, MCP, API, guardrail, retrieval/context, artifact, and test contracts.
2. Implement or complete citation extraction/validation and structured output validation at the Sprint 3 boundary.
3. Implement or complete agent nodes and graph invocation with local `MemorySaver`.
4. Connect graph execution to Sprint 2 retrieval/context builder contracts.
5. Connect `/api/v1/query` to the Sprint 3 graph without auth/rate-limit/streaming.
6. Implement or complete MCP tools/resources for retrieval/synthesis/artifact metadata local smoke use.
7. Add Sprint 3 graph/API/MCP/citation tests.
8. Run verification commands and update benchmark/docs only from real outputs or explicit blocked status.
9. Add ADR 004 and ADR 007.
10. Produce final summary.

Allowed file modification range:

- src/agents/**/*.py
- src/guardrails/output_schema.py
- src/guardrails/citation.py
- src/mcp/**/*.py
- src/api/routes.py and src/api/schemas.py only for `/api/v1/query` and directly related request/response schemas
- tests/unit/**/*.py only for Sprint 3 graph / citation / structured output / MCP unit coverage
- tests/integration/**/*.py only for Sprint 3 graph / API / MCP integration coverage
- docs/benchmark.md only for Sprint 3 smoke/pending/blocked status from real commands
- README.md only for real Sprint 3 behavior sync
- docs/decisions/**/*.md for ADR 004 and ADR 007, following the repository's existing ADR location
- minimal compatibility adjustments in Sprint 1-2 files only when strictly required for Sprint 3 graph/MCP/API integration

Do not modify:

- Sprint 4-5 implementation modules.
- Policy layer, model router, auth, rate limiting, Langfuse, PostgresSaver, SSE, Streamlit demo, or feedback implementation files except to leave existing placeholders untouched.
- cloud deployment docs.
- resume/job application/demo video materials.
- generated runtime artifact directories.
- .env or secret files.

Required verification commands:
Run the commands that are applicable in this local environment. If a command cannot run because fixtures, services, missing files, local environment, or dependencies are unavailable, record the exact blocked reason.

1. Agent graph unit tests, if the file exists or is added in Sprint 3:
   uv run pytest tests/unit/test_agents.py

2. Citation / structured output tests, if a dedicated file exists or is added in Sprint 3:
   uv run pytest tests/unit/test_citation.py

3. Query API integration tests, if the file exists or is added in Sprint 3:
   uv run pytest tests/integration/test_query_api.py

4. MCP server integration tests, if the file exists or is added in Sprint 3:
   uv run pytest tests/integration/test_mcp_server.py

5. Existing retrieval/context regression tests:
   uv run pytest tests/unit/test_retrieval.py tests/unit/test_context_builder.py

6. FastAPI app import smoke test:
   uv run python -c "from src.main import app; print(app.title)"

7. MCP server import-level smoke test:
   uv run python -c "from src.mcp.server import mcp; print(mcp.name if hasattr(mcp, 'name') else 'knowledge-ops')"

8. Do not start an unbounded stdio MCP server as proof of success. Only run `uv run python -m src.mcp.server --help` if the module explicitly implements a bounded help/CLI mode that exits immediately; otherwise record it as blocked with the reason that the current module entrypoint starts `mcp.run(transport="stdio")`.

Do not run an unbounded server command as proof of success unless it is wrapped in a bounded local smoke test and the result is recorded accurately.

Continuation and audit requirements:

- Keep work grouped by the Sprint 3 phase breakdown.
- After each phase, note what changed and which verification command was run or blocked.
- If interrupted, the next run must be able to continue from the last completed phase using the changed files, test output, and final/partial summary.
- Do not claim completion for any checklist item that has not been implemented and verified or explicitly marked blocked.
- Do not silently expand Sprint 3 to include Sprint 4-5 dependencies.
- Do not skip, xfail, or delete tests merely to pass.

Final summary requirements:
At the end, report:

1. Files changed.
2. Sprint 3 checklist items completed.
3. Verification commands run, with pass/fail/blocked status.
4. Any benchmark or smoke values recorded, including the exact command source; if none, say pending or blocked.
5. Any dependencies not added because approval is required.
6. Any blockers or known remaining work.
7. Confirmation that no Sprint 4-5 implementation items were included.
