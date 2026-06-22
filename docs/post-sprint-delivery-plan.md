# KnowledgeOps Post-Sprint Delivery Plan

Date: 2026-05-28

Updated: 2026-06-22

## Current State

KnowledgeOps has completed the Sprint 1-5 local delivery baseline and has been pushed to GitHub.

Previous pushed verification commit:

```text
278e102 chore: verify docker compose langfuse stack
```

Verified local baseline:

```text
uv run pytest -q
# 77 passed, 3 warnings
```

External interface smoke:

```text
uv run python scripts/smoke_external_interfaces.py --strict --include-container-provider --output eval/results/external_smoke_latest.json
# summary.status=ok, checks_total=15
# current provider exposes deepseek-v4-pro and deepseek-v4-flash
# deepseek-chat and deepseek-reasoner are expected-unavailable on this provider
```

Small local retrieval evaluation:

```text
uv run python scripts/evaluate_retrieval.py --dataset eval/retrieval_qa.jsonl --docs-dir data --retrieval dense,hybrid --top-k 5 --embedding-backend hash --output eval/results/retrieval_latest.json
# dense Hit@5 / Recall@5: 0.75 (15/20)
# hybrid Hit@5 / Recall@5: 1.0 (20/20)
```

Implemented and locally verified:

- Sprint 1: ingestion, loaders, chunking, FAISS dense retrieval, minimal planner, artifact persistence, CLI loop, `/api/v1/ingest`.
- Sprint 2: BM25, RRF hybrid retrieval, rerank boundary, query transforms, Context Builder, RAGAS dry-run scaffold, benchmark smoke.
- Sprint 3: LangGraph research graph, graph-backed `/api/v1/query`, citation validation, structured output validation, MCP tool/resource layer.
- Sprint 4: policy routing, cache/retry/fallback, guardrails, trace_id, business metrics, Langfuse dry-run safe path, auth, rate limit, optional memory boundary.
- Sprint 5: `/api/v1/query/stream`, `/api/v1/feedback`, Streamlit demo, feedback capture, final docs, delivery boundary, benchmark smoke, Docker Compose local stack smoke, local Langfuse trace/score smoke, external interface smoke artifact.
- Portfolio hardening: CI workflow has been supplemented with ruff, py_compile, FastAPI import smoke, and pytest; local equivalent commands passed. README CI badge must only be added after a real GitHub Actions green run.
- Demo dry run: bounded local Streamlit page load, SSE query path, and feedback path passed; see `docs/demo-dry-run.md`.

Known delivery boundaries:

- Docker Compose full integration has been run locally for `app + Milvus + Langfuse web/worker + ClickHouse + Postgres + Redis + MinIO`.
- Cloud deployment has not been completed.
- Locust 100 QPS x 5min has not been run.
- Real RAGAS metrics and production-scale Recall@5 have not been measured against a larger labeled QA set.
- Local Langfuse trace/score landing has been verified in the Docker Compose stack; production Langfuse/Postgres/Redis persistence has not been verified.
- Current OpenAI-compatible provider exposes `deepseek-v4-pro` / `deepseek-v4-flash`; official DeepSeek endpoint aliases `deepseek-chat` / `deepseek-reasoner` remain unavailable on this provider.
- Real `bge-m3` Docker runtime has not been verified.
- Demo video, resume finalization, and job applications are manual actions and have not been completed by the codebase.

## Operating Principle

Do not add new KnowledgeOps features until the project has been converted into a reliable job-search asset.

The next work is not another implementation Sprint. It is portfolio hardening:

1. Keep status documents aligned with real command output: `77 passed`, Docker Compose local Langfuse trace/score smoke, external interface smoke artifact, and 20-case hybrid `1.0` retrieval result.
2. Add implementation-boundary tables to README and architecture docs.
3. Persist benchmark/eval outputs with `--output`.
4. Keep query transform and rerank as optional config-gated enhancements.
5. Add CI and only add a badge after remote CI is actually green.
6. Prepare resume, interview narrative, demo script, and screenshots without overstating pending work.

## Phase 1: Repository Closure

Goal: make the repository clean and reproducible.

Checklist:

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
- GitHub Actions CI is green before adding any README CI badge.

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
- Bounded dry run evidence is recorded in `docs/demo-dry-run.md`.

## Phase 3: Safe Resume Claim Draft

Goal: create a truthful project description that matches actual evidence.

Safe claims:

- Built a FastAPI + LangGraph research-oriented Knowledge Agent that runs a `plan -> retrieve -> synthesize -> report -> verify` workflow.
- Implemented local document ingestion, FAISS dense retrieval, BM25 + RRF hybrid retrieval, context construction, artifact persistence, citation validation, MCP tools, auth/rate limiting, SSE streaming, feedback capture, and Streamlit demo.
- Added deterministic local fallback paths so smoke tests do not require paid external models or real credentials.
- Maintained explicit delivery boundaries for Docker, cloud deployment, QPS, RAGAS, Recall@5, and cost metrics.
- Verified local behavior with `77` tests passing.
- Measured 20 local source/page labeled retrieval cases: dense Hit@5 / Recall@5 `0.75`, hybrid Hit@5 / Recall@5 `1.0`.

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

Current minimum completed:

- `eval/retrieval_qa.jsonl` contains 20 local source/page labeled questions.
- `scripts/evaluate_retrieval.py` computes dense vs hybrid Hit@5 / Recall@5 and MRR@5.
- `--output eval/results/retrieval_latest.json` persists the latest run.

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

1. Keep `knowledge-ops` status and docs aligned with current command output.
2. Persist benchmark and retrieval eval JSON artifacts.
3. Keep optional query transform / rerank behind default-off config flags.
4. Add CI and wait for a real green run before adding badges.
5. Prepare demo video script and screenshots.
6. Only then consider real bge-m3, real RAGAS, Locust, cloud deployment, and production-grade Langfuse/Postgres/Redis hardening.
7. Create `ts-detect-agent` repository and project 2 plan after project 1 assets are usable.

## Explicit Non-Priorities

- Do not prioritize cloud deployment.
- Do not prioritize paid LLM integration.
- Do not rewrite Streamlit as Next.js now.
- Do not prioritize 100 QPS now.
- Do not start project 2 before project 1 assets are coherent.
- Do not make every module agentic.
- Do not chase "enterprise-grade" wording without evidence-backed claims.
