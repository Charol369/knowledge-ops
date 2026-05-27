You are implementing Sprint 2 only for KnowledgeOps: Hybrid Retrieval + Context Engineering.

Do not implement Sprint 3-5 work. Do not expand scope.

Objective:
Upgrade the Sprint 1 dense-only baseline into a hybrid retrieval subsystem with context engineering and evaluation scaffolding.

Sprint 2 must make sparse retrieval, hybrid fusion, reranking, query transformation, context assembly, and retrieval evaluation locally testable.

Scope:

1. BM25 sparse retrieval:
   
   - Implement a sparse retriever for local documents.
   - Support keyword-heavy and exact-term queries.
   - Keep it compatible with the Sprint 1 document metadata contract.

2. RRF hybrid fusion:
   
   - Fuse dense and sparse candidates with Reciprocal Rank Fusion.
   - Return ranked evidence with source metadata preserved.

3. Cross-Encoder rerank:
   
   - Add a rerank stage that can refine the top retrieved candidates.
   - Keep it callable as a standalone retrieval step.
   - If the required local model or dependency is unavailable, return a precise blocked reason instead of fabricating output.

4. Query transformation:
   
   - Implement HyDE.
   - Implement Multi-Query.
   - Implement Query Decomposition.
   - Keep each strategy independently callable.
   - Do not introduce LangGraph orchestration for these transforms.

5. Context Builder:
   
   - Build bounded, citation-ready context from retrieval evidence and prior artifacts.
   - Deduplicate, order, and budget evidence for downstream synthesis.
   - Ensure artifact-to-context conversion is supported.

6. Artifact-to-context retrieval:
   
   - Reuse Sprint 1 artifact outputs as input to the context builder.
   - Convert prior plan/evidence/final_answer artifacts into context-safe material.

7. Retrieval evaluation scaffold:
   
   - Add a RAGAS dataset scaffold and a local runner entrypoint such as eval/run_ragas.py or scripts/eval/run_ragas.py if the repository structure requires it.
   - Support dry-run validation locally.
   - Only record real metrics when commands actually run.

8. Docs and architecture records:
   
   - Sync Sprint 2 behavior into docs/benchmark.md only from real runs or explicit pending / blocked status.
   - Update README.md only if needed to reflect real Sprint 2 behavior without adding unmeasured claims.
   - Add ADR 002 and ADR 003 for retrieval and context-engineering decisions.

Out of Scope:

- Do not implement LangGraph main graph.
- Do not implement MCP tool layer.
- Do not implement /api/v1/query main graph integration.
- Do not implement /api/v1/feedback.
- Do not implement auth.
- Do not implement rate limiting.
- Do not implement Langfuse.
- Do not implement PostgresSaver.
- Do not implement SSE.
- Do not implement Streamlit demo.
- Do not implement cloud deployment.
- Do not implement Sprint 5 benchmark/final README claims.
- Do not add Sprint 3-5 features as hidden prerequisites.

Constraints:

- Sprint 1 must remain the dependency baseline.
- Keep compatibility with Sprint 1 loader, dense index, and artifact contracts.
- Use existing project architecture and dependencies where possible.
- Do not introduce generic orchestration, graph, service, API, auth, observability, or deployment abstractions beyond Sprint 2 retrieval/context needs.
- Do not add new dependencies without stopping for approval.
- Do not require real API keys.
- Do not require external paid models.
- Do not require cloud services.
- Do not require Docker daemon.
- Do not require database services for local acceptance.
- Do not fabricate metrics, benchmark results, or evaluation scores.
- Do not mark README metrics as achieved unless the corresponding commands actually ran.
- If a local model, dependency, or fixture is unavailable, record the exact blocked reason instead of pretending success.
- Keep changes mechanically auditable by Sprint 2 checklist item.
- After each implementation phase, run the relevant available tests or record why they are blocked.

Done when:

- BM25 sparse retrieval is locally callable.
- RRF hybrid retrieval is locally callable.
- Cross-Encoder rerank is locally callable or returns a precise blocked reason.
- HyDE, Multi-Query, and Query Decomposition are implemented at the Sprint 2 boundary and can be invoked independently.
- Context Builder produces bounded, citation-ready context.
- Artifact-to-context conversion works from Sprint 1 artifacts.
- At least one Sprint 2 retrieval/context evaluation test passes.
- Retrieval and context modules preserve source metadata in returned evidence.
- Evaluation scaffold exists and supports dry-run validation locally.
- docs/benchmark.md and README.md, if updated, contain only real outputs or explicit pending / blocked status.
- No Sprint 3-5 implementation items have been added.

Stop if:

- A required implementation needs a new dependency not already approved.
- A required implementation needs a real API key.
- A required implementation needs an external paid model.
- A required implementation needs cloud services, Docker daemon, or database services.
- Existing tests show regression.
- The diff exceeds a reasonable Sprint 2 scope and there is no phase-by-phase test record.
- Artifact or metadata requirements cannot be validated from local fixtures.
- The available project contracts conflict with this Sprint 2 scope.
- You would need to implement Sprint 3-5 functionality to make Sprint 2 pass.

First action:
Before modifying any file, read the project core documents, Sprint 2 plan/spec, and current retrieval/test code:

- README.md
- docs/architecture.md
- docs/development.md
- docs/api.md
- docs/benchmark.md
- docs/claude-comet-goal-workflow.md
- notes/day7/sprint_backlog.md
- docs/superpowers/plans/2026-05-27-sprint-2-hybrid-context-engineering-plan.md
- docs/superpowers/specs/2026-05-27-sprint-2-hybrid-context-engineering-design.md
- openspec/changes/sprint-2-hybrid-context-engineering/proposal.md
- openspec/changes/sprint-2-hybrid-context-engineering/design.md
- openspec/changes/sprint-2-hybrid-context-engineering/specs/knowledge-ops-sprint-2/spec.md
- openspec/changes/sprint-2-hybrid-context-engineering/tasks.md
- src/**/*.py
- tests/**/*.py

After reading, report and continue execution without waiting for confirmation:

1. Sprint 2 checklist count.
2. Current TODO / NotImplementedError / 501 Not implemented count, with emphasis on retrieval / context / eval distribution.
3. Current tests count and retrieval/context coverage overview.
4. Sprint 1 completed capabilities and Sprint 2 dependencies.
5. Any blockers, missing files, or scope conflicts.

Suggested Sprint 2 executable phase breakdown:

1. Inspect current retrieval contracts, artifacts, and fixtures.
2. Implement or complete BM25 sparse retrieval and RRF hybrid fusion.
3. Implement or complete rerank and query transformation modules.
4. Implement or complete Context Builder and artifact-to-context conversion.
5. Implement or complete retrieval evaluation scaffold and dry-run entrypoint.
6. Add Sprint 2 tests.
7. Run verification commands and update benchmark/docs only from real outputs.
8. Produce final summary.

Allowed file modification range:

- src/retrieval/**/*.py
- eval/**/*.py
- scripts/eval/**/*.py
- scripts/benchmark.py for Sprint 2 retrieval benchmark baseline implementation
- tests/unit/**/*.py
- tests/integration/**/*.py only for Sprint 2 retrieval/context coverage
- docs/benchmark.md
- README.md only for real Sprint 2 behavior sync
- docs/decisions/**/*.md for ADR 002 and ADR 003, following the repository's existing ADR location
- minimal compatibility adjustments in Sprint 1 files only when strictly required for Sprint 2 retrieval/context integration

Do not modify:

- Sprint 3-5 implementation modules.
- API route layers for /api/v1/query, /api/v1/feedback, auth, rate limiting, SSE, or demo UI.
- cloud deployment docs.
- resume/job application/demo video materials.
- generated runtime artifact directories.
- .env or secret files.

Required verification commands:
Run the commands that are applicable in this local environment. If a command cannot run because fixtures, services, missing files, or local environment are unavailable, record the exact blocked reason.

1. Retrieval unit tests:
   uv run pytest tests/unit/test_retrieval.py

2. Context builder tests, if tests/unit/test_context_builder.py exists or is added:
   uv run pytest tests/unit/test_context_builder.py

3. Sprint 2 integration tests, only if the file exists or is added in Sprint 2:
   uv run pytest tests/integration/test_hybrid_retrieval.py

4. RAGAS dry-run:
   uv run python eval/run_ragas.py --dry-run

5. Retrieval benchmark smoke test:
   uv run python scripts/benchmark.py --retrieval dense,hybrid --top-k 5

If a command path does not exist, do not invent it; either use the repository's actual equivalent or record the blocked reason.

Continuation and audit requirements:

- Keep work grouped by the Sprint 2 phase breakdown.
- After each phase, note what changed and which verification command was run or blocked.
- If interrupted, the next run must be able to continue from the last completed phase using the changed files, test output, and final/partial summary.
- Do not claim completion for any checklist item that has not been implemented and verified or explicitly marked blocked.

Final summary requirements:
At the end, report:

1. Files changed.
2. Sprint 2 checklist items completed.
3. Verification commands run, with pass/fail/blocked status.
4. Any benchmark values recorded, including the exact command source; if none, say pending or blocked.
5. Any dependencies not added because approval is required.
6. Any blockers or known remaining work.
7. Confirmation that no Sprint 3-5 implementation items were included.
