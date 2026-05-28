# KnowledgeOps Career Materials

Date: 2026-05-28

This document provides safe resume wording, a 5-minute project explanation, and interview FAQ for KnowledgeOps.

## Verified Facts

Use these facts in resumes, interviews, README summaries, and demo scripts.

- Built a FastAPI + LangGraph research-oriented Knowledge Agent for local enterprise-document research workflows.
- Implemented a deterministic pipeline: `plan -> retrieve -> synthesize -> report -> verify`.
- Implemented local ingestion for PDF, Word, and HTML, with source/page metadata for evidence and citations.
- Implemented FAISS dense retrieval, BM25 sparse retrieval, RRF hybrid fusion, query transforms, Context Builder, and artifact persistence.
- Implemented citation extraction/validation and structured answer validation.
- Implemented graph-backed `/api/v1/query`, SSE `/api/v1/query/stream`, local `/api/v1/feedback`, and `/api/v1/ingest`.
- Implemented API key authentication, local in-memory rate limiting, guardrails, Unicode normalization, prompt-injection detection, model routing, cache/retry/fallback primitives, and business metrics.
- Implemented MCP tool/resource layer for local retrieval and summarization services.
- Implemented Streamlit demo that calls the backend API and displays progress, plan, answer, citations, trace/session metadata, and feedback.
- Added explicit dry-run/local fallback boundaries so local tests do not require paid external models, real API keys, real Langfuse, real Redis/Postgres, Docker daemon, or cloud services.
- Verified the current local baseline with `66` passing tests.

## Unsafe Claims Until Measured

Do not use these as completed claims unless later commands produce real evidence.

- Recall@5 >= 85%.
- RAGAS Faithfulness >= 95%.
- Answer Relevancy >= 90%.
- P95 latency < 3s.
- 100 QPS support.
- Single-query cost < CNY 0.05.
- Production cloud deployment completed.
- Docker Compose full integration verified.
- Real Langfuse dashboard traces verified.
- Real Postgres/Redis production persistence verified.
- Demo video uploaded.
- Jobs applied.

## Resume Version

Use this version when one project needs 3-4 lines.

```text
KnowledgeOps - 生产导向研究型 Knowledge Agent 系统
- 基于 FastAPI + LangGraph 构建研究型 Knowledge Agent，将复杂问题拆成 plan -> retrieve -> synthesize -> report -> verify 工作流，避免把检索、引用校验、评估等确定性链路全部 agent 化。
- 实现 PDF/Word/HTML 本地入库、FAISS dense retrieval、BM25 + RRF hybrid retrieval、Context Builder、artifact persistence、citation validation、MCP tool/resource layer，并提供 REST/SSE 查询与 Streamlit demo。
- 加入模型路由、cache/retry/fallback、API key auth、in-memory rate limit、prompt-injection guardrails、Unicode normalization、business metrics 与 Langfuse dry-run-safe 接入边界。
- 使用 pytest 覆盖 ingestion、retrieval、graph/API/MCP、policy、guardrails、observability、streaming、feedback 与 demo helper，当前本地验证 66 tests passed；Recall@5/RAGAS/QPS/P95 等真实指标保留为待标注数据集和压测后更新。
```

## Short Resume Version

Use this version when space is tight.

```text
KnowledgeOps - 研究型 Knowledge Agent：基于 FastAPI + LangGraph 实现 plan -> retrieve -> synthesize -> report -> verify 工作流，集成 hybrid retrieval、Context Builder、citation validation、MCP、SSE streaming、feedback、auth/rate limit、guardrails 和 Streamlit demo；本地 pytest 66 tests passed，指标边界按真实 benchmark/smoke 输出记录。
```

## 5-Minute Project Explanation

### 0:00-0:40 Problem And Positioning

KnowledgeOps 不是普通知识库问答机器人，而是面向企业知识场景的研究型 Knowledge Agent。

传统 RAG 系统通常是 `query -> retrieve -> answer`，复杂问题下会遇到三个问题：

- 问题没有被拆解，检索目标不稳定；
- 模型生成和引用之间缺少可审计证据链；
- 成本、监控、限流、安全和失败边界通常是后补的。

这个项目的核心取舍是：只把高不确定性的认知步骤交给 Agent，确定性链路保持服务化。

### 0:40-1:30 Architecture

系统主链路是：

```text
question -> planner -> retrieval orchestrator -> synthesizer -> reporter -> verifier
```

底层服务包括：

- ingestion：PDF / Word / HTML loader；
- retrieval：FAISS dense、BM25 sparse、RRF hybrid；
- context：Context Builder 和 artifact store；
- API：FastAPI REST + SSE；
- observability：trace_id、business metrics、Langfuse dry-run-safe path；
- protection：API key、rate limit、guardrails；
- external integration：MCP server。

Agent 层负责规划、证据整合、报告和校验；检索、分块、引用校验、限流、缓存、评估都保持 deterministic service。

### 1:30-2:30 Retrieval And Context

检索不是单一向量召回，而是分阶段设计：

- Sprint 1 先做 FAISS dense baseline；
- Sprint 2 加 BM25 sparse 和 RRF fusion；
- query transform、rerank、Context Builder 都做成独立模块；
- evidence metadata 保留 source/page，供 citation validation 使用。

这样设计的原因是：实际企业知识库中有精确术语、缩写、表格字段和长文档标题，纯向量召回不够稳定。Hybrid retrieval 和 context builder 可以让检索结果更可控，也更容易评估。

### 2:30-3:25 Agent And Verification

LangGraph graph 使用固定研究流程，不是教学式的泛 Agent demo。

每个节点职责明确：

- planner：生成 2-4 个子任务并记录 policy decision；
- orchestrator：复用 retrieval/context 服务；
- synthesizer：基于 evidence 做归纳；
- reporter：生成 answer 和 citations；
- verifier：检查 citations 和 structured output。

这避免了“所有逻辑都塞进 prompt”的问题。失败时可以定位是检索问题、上下文问题、生成问题还是引用校验问题。

### 3:25-4:20 Production Controls

项目从后半段加入生产控制，但没有把本地验收绑定到真实外部服务：

- ComplexityClassifier 和 ModelRouter 支持成本治理；
- LocalResponseCache、FallbackPolicy 支持可靠性边界；
- API key auth 和 in-memory rate limit 保护 query/stream/feedback；
- prompt injection detection 和 Unicode normalization 处理输入风险；
- Langfuse 默认 disabled，不会在无真实配置时触发认证错误；
- Postgres/Redis/Langfuse/Docker/cloud 都是明确的 optional/manual boundary。

这让项目在本地可以稳定验证，同时保留生产扩展路径。

### 4:20-5:00 Demo And Honest Metrics

当前可演示能力包括：

- FastAPI `/api/v1/query`；
- SSE `/api/v1/query/stream`；
- `/api/v1/feedback` 本地捕获；
- Streamlit demo 展示 question、progress、plan、answer、citations、trace/session 和 feedback；
- MCP server 暴露 retrieval/summarization 能力。

当前本地验证是 `66 tests passed`，benchmark smoke 能跑 dense/hybrid retrieval 并返回 top-5 evidence。

但我不会声称 Recall@5、RAGAS、P95、QPS 或成本已经达标，因为这些需要标注 QA 集、真实评估命令和压测环境。下一步会先做 20 条 QA 标注集，补一个可复现的 retrieval Hit@5 / Recall@5。

## Interview FAQ

### Why not make everything an Agent?

Because retrieval, citation validation, rate limiting, caching, metrics, and evaluation are deterministic engineering services. If they are hidden inside prompts, failures become harder to debug and costs become harder to control. This project keeps cognition agentic and execution service-based.

### Why hybrid retrieval?

Dense retrieval handles semantic similarity, while BM25 handles exact terms, names, and document-specific keywords. RRF fusion gives a simple, deterministic way to combine both without requiring another model call.

### What is the role of Context Builder?

Context Builder controls what evidence enters the model context. It deduplicates, sorts, budgets, and formats evidence so answer generation has source-aware context instead of arbitrary retrieved chunks.

### How is hallucination controlled?

The project uses grounded evidence, citation extraction, citation validation, structured output validation, and human-review flags. Full hallucination-rate measurement still requires a labeled evaluation set and real RAGAS or equivalent evaluation.

### How is cost controlled?

The project includes complexity classification, model routing, local cache, retry/fallback policy, and deterministic fallbacks. In local smoke, it avoids paid model calls by default. Real cost measurement is pending real provider usage and Langfuse cost tracking.

### What is MCP used for?

MCP exposes retrieval and summarization capabilities as standard tools/resources so external clients can call the local KnowledgeOps services without coupling to internal Python modules.

### What is actually measured?

Measured:

- local tests: `66 passed`;
- benchmark smoke: dense/hybrid top-5 retrieval returns evidence from local data;
- local API/Streamlit/feedback/streaming smoke.

Pending:

- Recall@5;
- RAGAS metrics;
- P95 latency;
- QPS;
- single-query cost;
- Docker/cloud integration.
