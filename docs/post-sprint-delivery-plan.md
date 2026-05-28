# KnowledgeOps Post-Sprint Delivery Plan

Date: 2026-05-28

## Current State

KnowledgeOps has completed the Sprint 1-5 local delivery baseline and has been pushed to GitHub.

Latest pushed commit:

```text
9e4a511 feat: complete sprint 5 delivery
```

Verified local baseline:

```text
uv run pytest -q
# 66 passed, 3 warnings
```

Implemented and locally verified:

- Sprint 1: ingestion, loaders, chunking, FAISS dense retrieval, minimal planner, artifact persistence, CLI loop, `/api/v1/ingest`.
- Sprint 2: BM25, RRF hybrid retrieval, rerank boundary, query transforms, Context Builder, RAGAS dry-run scaffold, benchmark smoke.
- Sprint 3: LangGraph research graph, graph-backed `/api/v1/query`, citation validation, structured output validation, MCP tool/resource layer.
- Sprint 4: policy routing, cache/retry/fallback, guardrails, trace_id, business metrics, Langfuse dry-run safe path, auth, rate limit, optional memory boundary.
- Sprint 5: `/api/v1/query/stream`, `/api/v1/feedback`, Streamlit demo, feedback capture, final docs, delivery boundary, benchmark smoke.

Known local worktree issue:

- `docs/development.md` has one pre-existing whitespace-only diff.

Known delivery boundaries:

- Docker Compose full integration has not been run as a verified acceptance result.
- Cloud deployment has not been completed.
- Locust 100 QPS x 5min has not been run.
- Real RAGAS metrics and Recall@5 have not been measured against a labeled QA set.
- Real Langfuse dashboard trace and real Postgres/Redis integration have not been verified.
- Demo video, resume finalization, and job applications are manual actions and have not been completed by the codebase.

## Operating Principle

Do not add new KnowledgeOps features until the project has been converted into a reliable job-search asset.

The next work is not another implementation Sprint. It is delivery hardening:

1. Clean repository state.
2. Produce safe project claims.
3. Create demo material.
4. Add a small real evaluation set.
5. Prepare resume and interview narratives.
6. Then start project 2 in a separate repository.

## Phase 1: Repository Closure

Goal: make the repository clean and reproducible.

Checklist:

- Resolve the whitespace-only `docs/development.md` diff by either committing it with documentation updates or reverting it explicitly.
- Run `git status --short --branch`.
- Run `uv run pytest -q`.
- Run `uv run python -m py_compile frontend/app.py scripts/locust_loadtest.py`.
- Run a FastAPI import smoke:

```powershell
uv run python -c "from src.main import app; print(app.title)"
```

- Confirm `main` is still aligned with `origin/main` after any cleanup commit.

Done when:

- `git status --short --branch` shows no unintended modified files.
- Any committed cleanup is pushed.
- Test result is recorded in the summary.

## Phase 2: Demo Dry Run

Goal: verify the project can be shown locally without relying on fabricated metrics.

Checklist:

- Start API manually:

```powershell
uv run uvicorn src.main:app --reload
```

- Start Streamlit manually:

```powershell
uv run streamlit run frontend/app.py
```

- In the demo, submit:

```text
Summarize the indexed evidence
```

- Confirm the UI shows:
  - question input;
  - progress;
  - plan;
  - evidence or citations;
  - final answer;
  - trace/session metadata;
  - feedback affordance.

- Submit feedback and verify the API returns local success.

Done when:

- Demo path is manually runnable.
- Screenshots or recording source files are saved outside the repository, unless intentionally adding curated documentation assets.
- No claim is made that public deployment or video upload is complete.

## Phase 3: Safe Resume Claim Draft

Goal: create a truthful project description that matches actual evidence.

Safe claims:

- Built a FastAPI + LangGraph research-oriented Knowledge Agent that runs a `plan -> retrieve -> synthesize -> report -> verify` workflow.
- Implemented local document ingestion, FAISS dense retrieval, BM25 + RRF hybrid retrieval, context construction, artifact persistence, citation validation, MCP tools, auth/rate limiting, SSE streaming, feedback capture, and Streamlit demo.
- Added deterministic local fallback paths so smoke tests do not require paid external models or real credentials.
- Maintained explicit delivery boundaries for Docker, cloud deployment, QPS, RAGAS, Recall@5, and cost metrics.
- Verified local behavior with `66` tests passing.

Unsafe claims until measured:

- Recall@5 >= 85%.
- RAGAS faithfulness >= 95%.
- P95 latency < 3s.
- 100 QPS support.
- Single-query cost < ¥0.05.
- Real cloud deployment completed.
- Real Langfuse dashboard trace completed.

Done when:

- A one-page resume bullet draft exists.
- A 5-minute project explanation draft exists.
- The wording distinguishes implemented facts from planned/manual verification.

## Phase 4: Minimal Real Evaluation

Goal: produce one credible measured metric instead of relying only on smoke tests.

Recommended minimum:

- Create a small labeled QA set with 20 questions.
- For each question record:
  - question;
  - expected source document;
  - expected page or chunk identifier where possible;
  - acceptable answer points.

First metric:

- retrieval Recall@5 or hit@5 for dense vs hybrid retrieval.

Do not start with:

- full 100-question dataset;
- production-scale load test;
- cloud deployment;
- expensive LLM judge runs.

Done when:

- A labeled test file exists.
- A script can compute at least one retrieval metric.
- `docs/benchmark.md` is updated only with real command output.

## Phase 5: Delivery Materials

Goal: prepare interview and job-search assets.

Checklist:

- 5-minute demo script.
- 30-60 second short demo recording plan.
- README review from a recruiter/interviewer perspective.
- Resume paragraph.
- Project architecture explanation.
- FAQ for likely interview questions:
  - Why not make every component an Agent?
  - Why use hybrid retrieval?
  - How is cost controlled?
  - How are citations verified?
  - What is actually measured vs pending?
  - How does MCP fit into the system?

Done when:

- Project can be explained in 5 minutes without overstating pending work.
- Demo can be run locally.
- Resume wording is consistent with repository facts.

## Phase 6: Project 2 Preparation

Goal: start `TS-Detect Agent` only after project 1 delivery assets are usable.

Repository path:

```text
C:\Users\sundewang\Code\ts-detect-agent
```

Source asset pools:

- `C:\Users\sundewang\Desktop\MTS_AD\DA-Baselines`
- `C:\Users\sundewang\Desktop\MTS_AD\GDA-TSAD`
- `C:\Users\sundewang\Desktop\MTS_AD\datasets`

Boundary:

- Do not develop directly inside the research asset directories.
- Do not copy all experiments into the new repo.
- Extract only the minimal runnable detector/data/metric path.

First project 2 milestone:

```text
raw time-series data -> detector service -> anomaly events -> diagnostic explanation -> report/demo
```

Done when:

- `ts-detect-agent` repository is created.
- One dataset and one detector path are selected.
- A minimal engineering plan is written before implementation.

## Execution Order

Use this order unless a higher-priority blocker appears:

1. Clean `knowledge-ops` working tree.
2. Run local demo dry run.
3. Draft resume/project explanation safely.
4. Build a 20-question evaluation set.
5. Add retrieval metric script and update benchmark from real output.
6. Prepare demo video script and screenshots.
7. Create `ts-detect-agent` repository and project 2 plan.
