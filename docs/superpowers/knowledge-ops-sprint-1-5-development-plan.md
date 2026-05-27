# KnowledgeOps Sprint 1-5 Complete Development Plan

## Source of Truth
This document organizes the five-Sprint development plan described by `docs/claude-comet-goal-workflow.md`, `notes/day7/sprint_backlog.md`, `docs/architecture.md`, `README.md`, `docs/api.md`, `docs/benchmark.md`, and external career-sprint planning notes.

## Workflow Boundary
The workflow remains strictly staged:

```text
Comet spec/plan for the current Sprint
        ↓
goal-prompt-builder creates the current Sprint Codex /goal
        ↓
Codex executes implementation, tests, and documentation updates
```

Do not hand Sprint 1-5 to Codex in a single `/goal`. Each Sprint must close independently before the next Sprint is finalized.

## Dependency Order

```text
Sprint 1 → Sprint 2 → Sprint 3 → Sprint 4 → Sprint 5
```

- Sprint 1 establishes ingestion, dense retrieval, minimal planner, artifacts, CLI loop, and ingest API skeleton.
- Sprint 2 depends on Sprint 1 and adds hybrid retrieval, query transforms, context engineering, and evaluation scaffolding.
- Sprint 3 depends on Sprint 1-2 and adds LangGraph graph, structured output, citation validation, MCP, and `/api/v1/query`.
- Sprint 4 depends on Sprint 1-3 and adds policy routing, observability, guardrails, checkpointing, auth, and rate limiting.
- Sprint 5 depends on Sprint 1-4 and finalizes streaming, feedback, demo, Docker integration, benchmark, README, and manual delivery assets.

## Global Constraints
- Do not write or commit `.env`, API keys, credentials, runtime artifacts, large data files, model weights, or database files.
- Do not require real API keys, paid external models, cloud services, Docker daemon, or database services for local acceptance unless explicitly approved.
- Do not fabricate benchmark or evaluation results.
- Do not mark README metrics as achieved unless the corresponding commands actually ran.
- Do not skip, xfail, or delete tests just to pass.
- Do not introduce heavy dependencies without stopping for approval.
- Do not rewrite learning notes or remove the core architecture positioning.
- Keep manual/non-code deliverables separate from automated code delivery.

## Sprint 1: Minimal Research Loop + Evidence Pipeline

### Objective
Create the smallest local KnowledgeOps research loop: ingest documents, index dense vectors, retrieve evidence, plan minimal subtasks, synthesize an answer, and persist artifacts.

### Scope
- PDF, Word, and HTML loaders.
- Recursive chunking with chunk_size=500 and overlap=50.
- Configurable embedder wrapper with bge-m3 preferred.
- FAISS dense index and persistence.
- Dense retrieval k=5.
- Minimal Planner.
- Session artifacts for plan/evidence/final_answer.
- CLI research loop.
- `/api/v1/ingest` skeleton without auth.
- Loader tests and Sprint 1 baseline benchmark documentation.

### Constraints
- Local-first only.
- No external paid services, real secrets, Docker-only dependencies, cloud resources, or production database required.
- Benchmark docs may include only measured local baseline values.

### Done When
- `question -> plan -> retrieve -> synthesize -> answer` works locally.
- Dense evidence includes source metadata.
- Session artifacts are written.
- Loader tests pass.
- `/api/v1/ingest` skeleton exists.
- Sprint 1 baseline is documented only if measured.

### Stop If
- A required dependency is not already approved.
- Real credentials or paid/cloud services become necessary.
- Artifact or metadata requirements cannot be validated from local fixtures.

### Checklist Mapping
- PDF Loader → loaders.
- Word / HTML Loader → loaders.
- Recursive splitter → chunking.
- Embedder wrapper → embedding.
- FAISS baseline → indexing.
- Dense retrieval → retrieval service.
- Minimal Planner → agent baseline.
- Session artifacts → artifact persistence.
- CLI research loop → pipeline.
- `/api/v1/ingest` skeleton → API.
- Loader tests → unit tests.
- Benchmark baseline → docs/eval.

### Verification Commands
```powershell
uv run pytest tests/unit/test_loaders.py
uv run python scripts/ingest_pdfs.py data/pdfs/
uv run python -m src.agents.graph --question "Summarize the indexed evidence"
uv run uvicorn src.main:app --reload
```

### Dependency on Previous Sprint
None.

### Manual / Non-Code Boundary
Excluded: real cloud deployment, demo video, upload, resume finalization, profile updates, and job applications.

### `/goal` Status
Can directly enter `/goal` finalization.

## Sprint 2: Hybrid Retrieval + Context Engineering

### Objective
Upgrade dense-only retrieval into hybrid retrieval plus context engineering and evaluation scaffolding.

### Scope
- BM25 sparse retrieval.
- RRF hybrid fusion.
- Cross-Encoder rerank.
- HyDE.
- Multi-Query.
- Query Decomposition.
- Context Builder.
- Artifact-to-context.
- RAGAS test set and `run_ragas.py`.
- ADR 002 and ADR 003.

### Constraints
- Requires Sprint 1 contracts for loaders, dense index, dense retriever, and artifacts.
- No LangGraph/MCP orchestration yet.
- No fabricated metric claims.
- External model usage must have local fallback or stop for approval.

### Done When
- Dense, sparse, hybrid, rerank, and query-transform modules are locally callable.
- Context Builder returns bounded citation-ready context.
- Evaluation scaffolding exists and can dry-run locally.
- ADR 002 and ADR 003 are recorded.

### Stop If
- Sprint 1 interfaces change or remain unstable.
- RAGAS/Cross-Encoder dependency requires approval.
- Evaluation cannot run without unapproved credentials.

### Checklist Mapping
- BM25 → sparse retrieval.
- RRF → hybrid fusion.
- Cross-Encoder → rerank stage.
- HyDE / Multi-Query / Query Decomposition → query transforms.
- Context Builder / Artifact-to-context → context engineering.
- RAGAS dataset / `run_ragas.py` → evaluation.
- ADR 002 + ADR 003 → architecture records.

### Verification Commands
```powershell
uv run pytest tests/unit/test_retrieval.py tests/unit/test_context_builder.py
uv run python eval/run_ragas.py --dry-run
uv run python scripts/benchmark.py --retrieval dense,hybrid --top-k 5
```

### Dependency on Previous Sprint
Depends on Sprint 1 and must be recalibrated after Sprint 1 execution.

### Manual / Non-Code Boundary
Manual curation of RAGAS examples is allowed. Benchmark claims, deployment, video, resume, and applications are excluded.

### `/goal` Draft Outline
- Read Sprint 1 actual output contracts.
- Implement sparse/hybrid/rerank/query-transform/context modules.
- Add retrieval/context tests and evaluation dry-run.
- Update ADRs and benchmark docs only from measured results.

### `/goal` Status
Must wait for Sprint 1 execution and recalibration.

## Sprint 3: LangGraph Agent Graph + MCP Tool Layer

### Objective
Represent KnowledgeOps as an auditable LangGraph workflow and expose graph-backed capabilities through API and MCP.

### Scope
- LangGraph main graph refactor.
- Planner Node.
- Retrieval Orchestrator.
- Synthesizer.
- Reporter.
- Verifier / Reflection.
- Memory Checkpointer.
- Pydantic structured output.
- Citation enforcement and validation.
- MCP server integration with retrieval services and synthesizer.
- Claude Desktop integration test boundary.
- `/api/v1/query` connected to graph.
- ADR 004 and ADR 007.

### Constraints
- Requires Sprint 1-2 retrieval/context/artifact contracts.
- No Sprint 4 policy/auth/rate-limit/Langfuse/PostgresSaver work yet.
- Claude Desktop setup is manual/local configuration.

### Done When
- Graph executes `plan -> retrieve -> synthesize -> report -> verify`.
- `/api/v1/query` returns graph-backed structured output.
- Citations are validated against evidence metadata.
- MCP retrieval/synthesis tools are locally available.
- ADR 004 and ADR 007 are recorded.

### Stop If
- Sprint 2 Context Builder contract is unstable.
- Citation metadata cannot be traced.
- MCP client setup requires user-only local configuration.

### Checklist Mapping
- LangGraph 主图重构 → graph composition.
- Planner / Retrieval Orchestrator / Synthesizer / Reporter / Verifier → graph nodes.
- Memory Checkpointer → graph state.
- Pydantic structured_output → output contract.
- Citation → evidence validation.
- MCP server → MCP layer.
- Claude Desktop → manual integration validation.
- `/api/v1/query` → API graph entry.
- ADR 004 + ADR 007 → architecture records.

### Verification Commands
```powershell
uv run pytest tests/unit/test_agents.py tests/integration/test_query_api.py tests/integration/test_mcp_server.py
uv run uvicorn src.main:app --reload
uv run python -m src.mcp.server --help
```

### Dependency on Previous Sprint
Depends on Sprint 1-2 and must be recalibrated after Sprint 2 execution.

### Manual / Non-Code Boundary
Claude Desktop setup/testing may require manual local configuration. Public demo, cloud deployment, resume, and applications are excluded.

### `/goal` Draft Outline
- Read final Sprint 1-2 contracts.
- Implement graph nodes/state and API/MCP wiring.
- Add structured output and citation validation.
- Record ADR 004/007.

### `/goal` Status
Must wait for Sprint 1-2 execution and recalibration.

## Sprint 4: Policy Layer + LLMOps + Guardrails

### Objective
Harden the graph-backed system with policy routing, reliability controls, observability, guardrails, persistence, and API protection.

### Scope
- Complexity Classifier.
- Model Router.
- Cache / Retry / Fallback.
- Langfuse self-hosting integration path.
- CallbackHandler injection into graph/retrieval/policy decisions.
- trace_id propagated to API responses.
- Business metrics.
- Injection detection levels.
- Unicode normalization.
- PostgresSaver replacing MemorySaver.
- Rate Limit middleware.
- API Key authentication.
- ADR 005 and ADR 006.

### Constraints
- Requires Sprint 1-3 graph/API/retrieval contracts.
- No secrets committed.
- Local acceptance must not require real cloud services.
- `/api/v1/feedback` boundary conflicts across docs; keep implementation in Sprint 5 unless user explicitly moves it.

### Done When
- Policy routing decisions are testable and observable.
- Cache/retry/fallback behavior is deterministic.
- trace_id appears in API responses.
- Guardrails normalize Unicode and detect injection risk.
- API key auth and rate limiting protect endpoints.
- PostgresSaver is used when configured.
- ADR 005 and ADR 006 are recorded.

### Stop If
- Secrets or real credentials would be required.
- Langfuse/Postgres services cannot be handled as local optional integration.
- Auth/rate-limit rollout conflicts with earlier API skeleton behavior.

### Checklist Mapping
- Complexity Classifier / Model Router → policy.
- Cache / Retry / Fallback → reliability.
- Langfuse / CallbackHandler / trace_id / metrics → observability.
- Injection / Unicode normalization → guardrails.
- PostgresSaver → persistence.
- Rate Limit / API Key → API protection.
- ADR 005 + ADR 006 → architecture records.

### Verification Commands
```powershell
uv run pytest tests/unit/test_policy.py tests/unit/test_guardrails.py tests/integration/test_auth_rate_limit.py
uv run pytest tests/integration/test_observability.py
uv run uvicorn src.main:app --reload
```

### Dependency on Previous Sprint
Depends on Sprint 1-3 and must be recalibrated after Sprint 3 execution.

### Manual / Non-Code Boundary
Langfuse/Postgres service setup may require manual local configuration. Cloud deployment, public demo, resume, and applications are excluded.

### `/goal` Draft Outline
- Read final Sprint 1-3 graph/API contracts.
- Implement policy, observability, guardrails, persistence, auth, and rate limiting.
- Add tests for protected endpoints and trace propagation.
- Record ADR 005/006.

### `/goal` Status
Must wait for Sprint 1-3 execution and recalibration.

## Sprint 5: SSE / Demo / Benchmark / README Finalization

### Objective
Finalize the project as a demonstrable, benchmarked, documented KnowledgeOps system.

### Scope
- SSE endpoint `/api/v1/query/stream`.
- Feedback endpoint `/api/v1/feedback` connected to Langfuse score.
- Streamlit Demo.
- docker-compose full integration.
- Cloud deployment boundary/instructions.
- Locust 100 QPS x 5min pressure test when environment supports it.
- Final evaluation.
- README v2.0.
- 5-10 minute demo video manual deliverable.
- Project 1 resume paragraph manual deliverable.

### Constraints
- Requires Sprint 1-4 complete behavior.
- No fabricated benchmark/RAGAS/latency/cost/QPS values.
- Do not claim cloud deployment, video upload, resume finalization, profile updates, or applications as automated code delivery.
- Public cloud/upload is not required for code acceptance.

### Done When
- SSE endpoint streams graph progress/results locally.
- Feedback endpoint accepts Langfuse-compatible scores when configured.
- Streamlit demo exercises the golden path.
- Docker Compose path is tested or blocked with clear environment reason.
- Evaluation/benchmark results are recorded only if commands ran.
- README v2.0 matches actual behavior.
- Manual deliverables are explicitly listed.

### Stop If
- Docker daemon, cloud account, Langfuse credentials, or public upload is unavailable but required.
- Benchmark environment cannot support the pressure-test target.
- README would need unmeasured metric claims.

### Checklist Mapping
- SSE → streaming API.
- Feedback → observability feedback.
- Streamlit → demo UI.
- docker-compose → integration.
- Cloud deployment → manual deployment boundary.
- Locust → performance benchmark.
- Final evaluation → evaluation.
- README v2.0 → documentation.
- Demo video / resume paragraph → manual delivery.

### Verification Commands
```powershell
uv run pytest tests/integration/test_streaming.py tests/integration/test_feedback.py
uv run streamlit run frontend/app.py
docker compose up -d
uv run locust -f eval/locustfile.py --headless -u 100 -r 10 -t 5m
```

### Dependency on Previous Sprint
Depends on Sprint 1-4 and must be recalibrated after Sprint 4 execution.

### Manual / Non-Code Boundary
Manual actions: real cloud deployment, public demo video recording/upload, resume finalization, LinkedIn/Boss/Niuke updates, and job applications.

### `/goal` Draft Outline
- Read final Sprint 1-4 API/observability contracts.
- Implement SSE, feedback, Streamlit demo, integration checks, and benchmark/docs updates.
- Run available verification commands and document blocked environment/manual steps.
- Update README from measured behavior.

### `/goal` Status
Must wait for Sprint 1-4 execution and recalibration.

## `/goal` Finalization Readiness

| Sprint | Can finalize now? | Reason |
|---|---:|---|
| Sprint 1 | Yes | Foundation Sprint has no prior implementation dependency. |
| Sprint 2 | No | Must consume actual Sprint 1 contracts. |
| Sprint 3 | No | Must consume actual Sprint 1-2 retrieval/context contracts. |
| Sprint 4 | No | Must consume actual Sprint 1-3 graph/API contracts. |
| Sprint 5 | No | Must consume actual Sprint 1-4 final guarded/observable API behavior. |

## First `/goal` to Finalize
Finalize Sprint 1 first.
