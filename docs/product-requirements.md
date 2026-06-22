# KnowledgeOps Product Requirements

Date: 2026-06-22

Status: Draft for review

## 1. Product Goal

KnowledgeOps 的下一阶段目标是从单路径 RAG 问答升级为真实企业知识库自然语言问答系统 MVP。

目标定义：

```text
构建一个可本地验证、可逐步部署上线的企业知识库问答系统。
系统必须支持真实文档入库、意图路由、混合检索、结构化文档工具、真实 LLM 生成、引用校验、反馈评测、权限边界和可观测运行。
```

本阶段不是继续优化“demo 展示页”，而是把项目 1 的后端能力和产品边界对齐到企业知识库问答工作流。

## 2. Current Baseline

当前已完成并可安全声明的事实：

| Area | Current status | Evidence |
|---|---|---|
| API | FastAPI `/api/v1/query` 和 `/api/v1/query/stream` 已接入 graph | integration tests |
| LLM synthesis | OpenAI-compatible `deepseek-v4-pro` 已进入主查询 synthesis 链路 | API smoke 返回 `synthesis_mode=llm` / `synthesis_status=ok` |
| Session / trace | 正常 UI 自动生成 `session_id`；API 每次请求自动生成 `trace_id`，并保留 `thread_id` 作为兼容/调试覆盖 | `tests/integration/test_query_api.py` / `tests/integration/test_streaming.py` |
| Intent-aware QA routing | deterministic intent router + graph strategy dispatch 已接入 | `tests/unit/test_intent_router.py` / `tests/unit/test_agents.py` |
| Document tools | reference count、section lookup、table blocked path 已接入 | `tests/unit/test_reference_count_tool.py` / `tests/unit/test_section_lookup_tool.py` |
| API diagnostics | `/api/v1/query` 和 `/api/v1/query/stream` 返回 `intent`、`strategy`、`tool_*`、`fallback_reason` | `tests/integration/test_query_api.py` / `tests/integration/test_streaming.py` |
| Retrieval | FAISS/hash dense + BM25 + RRF hybrid retrieval | unit/integration tests |
| Citation | answer citation extraction + verifier | unit tests |
| Fallback | LLM synthesis 失败时 deterministic fallback | graph state / tests |
| Feedback | `/api/v1/feedback` + 本地 Langfuse score smoke | docs/docker-compose-smoke.md |
| Docker local stack | app + Milvus + Langfuse + ClickHouse + Postgres + Redis + MinIO 本地 smoke | docs/docker-compose-smoke.md |
| CI | GitHub Actions green | README badge / Actions run |
| Tests | 当前本地测试通过 | `107 passed, 3 warnings` |

当前不能声明为已完成：

| Area | Boundary |
|---|---|
| Cloud deployment | 未完成公网部署 |
| 100 QPS | 未完成 Locust 100 QPS x 5min |
| RAGAS production quality | 未完成真实 RAGAS 指标 |
| Production bge-m3 runtime | Docker runtime 未验证真实 bge-m3 |
| Enterprise ACL | 未实现企业用户/组/文档权限隔离 |
| Incremental ingestion | 未实现企业数据源增量同步 |
| Cost dashboard | 未完成 token/cost 聚合 |

## 3. Target Users

| User type | Goal | Required capability |
|---|---|---|
| Employee / knowledge worker | 用自然语言查询企业文档 | grounded answer, citation, no-answer behavior |
| Team lead / manager | 快速总结政策、方案、报告 | summary, comparison, source trace |
| Admin / knowledge owner | 接入文档、查看索引状态 | ingestion, document list, reindex, status |
| Developer / operator | 部署、排障、观测质量 | trace, logs, fallback reason, eval artifacts |
| Interview reviewer | 验证工程能力和 claims | reproducible commands, docs, tests, evidence |

## 4. Core User Scenarios

### 4.1 Definition / Explanation

Example:

```text
What is multi-head attention in Attention Is All You Need?
```

Expected behavior:

```text
intent=definition
strategy=hybrid_retrieval
synthesis_mode=llm
answer has citations
```

Acceptance:

- Answer is natural language, not raw chunk concatenation.
- Every factual claim is supported by citations.
- `synthesis_status=ok` when provider is healthy.

### 4.2 Section Summary

Example:

```text
Summarize section 3.2.
```

Expected behavior:

```text
intent=section_summary
strategy=section_lookup + llm_synthesis
```

Acceptance:

- System locates the requested section before generation.
- Answer cites pages/section evidence.
- If section is missing, system says it cannot locate the section.

### 4.3 Count / Deterministic Document Question

Example:

```text
How many references are in Attention Is All You Need?
```

Expected behavior:

```text
intent=count
strategy=reference_count_tool
tool_result.count = deterministic integer or blocked reason
```

Acceptance:

- LLM must not guess a count.
- A deterministic tool extracts and counts reference entries.
- If references section cannot be located, response returns a precise blocked reason.

### 4.4 List Extraction

Example:

```text
List the datasets used in the experiments.
```

Expected behavior:

```text
intent=list
strategy=targeted_retrieval + extraction + llm_synthesis
```

Acceptance:

- Answer is a list with evidence citations.
- If only partial evidence exists, response says it is partial.

### 4.5 Table Query

Example:

```text
What does Table 2 show?
```

Expected behavior:

```text
intent=table_query
strategy=table_lookup_tool
```

Acceptance:

- Prefer table/parser tool over normal top-k RAG.
- If table structure is unavailable, return blocked reason instead of guessing.

### 4.6 No-answer / Evidence Insufficient

Example:

```text
What was the author's private salary?
```

Expected behavior:

```text
intent=unknown or no_answer
answer says evidence is insufficient
needs_human_review may be true
```

Acceptance:

- No unsupported claims.
- No external facts unless explicitly allowed.

## 5. Functional Requirements

### P0 Requirements

Implementation design and task breakdown:

```text
Step 6 technical design: docs/p0-intent-routing-design.md
Step 7 task breakdown: docs/p0-implementation-plan.md
```

| ID | Requirement | Acceptance |
|---|---|---|
| P0-R1 | Query Intent Router | 已完成：deterministic router classifies `definition`, `count`, `section_summary`, `list`, `compare`, `table_query`, `no_answer`, `unknown` |
| P0-R2 | Intent-aware graph routing | 已完成：graph dispatches hybrid retrieval / reference count / section lookup / table blocked / blocked strategy |
| P0-R3 | Reference count tool | 已完成：counts references deterministically or returns precise blocked reason |
| P0-R4 | Section lookup tool | 已完成：locates numbered section evidence or returns precise blocked reason |
| P0-R5 | Automatic session/trace | 已完成：normal UI 自动生成 `session_id`；API 自动生成单次请求 `trace_id`；旧 `thread_id` 仅作为调试覆盖 |
| P0-R6 | API diagnostics | 已完成 API/SSE response fields；Streamlit diagnostics display 留到 Task 7 |
| P0-R7 | LLM synthesis stability | structured output + local citation rendering; fallback reason surfaced |
| P0-R8 | Regression tests | Task 1-5 unit/integration tests 已补；P0 eval artifact 留到 Task 8 |

### P1 Requirements

| ID | Requirement | Acceptance |
|---|---|---|
| P1-R1 | Production embedding path | bge-m3 or embedding API verified outside hash backend |
| P1-R2 | Rerank path | rerank enabled/configured and covered by eval |
| P1-R3 | Document/chunk schema | stable `document_id`, `version_hash`, `chunk_id`, `section_path` |
| P1-R4 | Metadata filtering | document type/source/page/section filters in retrieval |
| P1-R5 | Product QA eval set | 50-100 regression questions across intents |
| P1-R6 | Cost and latency trace | token usage, model, latency and fallback reason recorded |

### P2 Requirements

| ID | Requirement | Acceptance |
|---|---|---|
| P2-R1 | Tenant/user/group ACL | retrieval filters unauthorized documents before LLM |
| P2-R2 | Incremental ingestion | changed documents are reindexed, deleted documents are removed |
| P2-R3 | Postgres metadata store | documents/jobs/traces/feedback persist beyond process memory |
| P2-R4 | Worker queue | ingestion/eval jobs run async |
| P2-R5 | Deployable stack | fresh Docker build and `docker compose up` reproduce local stack |
| P2-R6 | Load and quality eval | Locust/RAGAS/custom judge artifacts saved |

## 6. Non-goals

These are explicitly not first-priority for the next implementation phase:

| Non-goal | Reason |
|---|---|
| Rewriting Streamlit to Next.js | Back-end workflow correctness is the bottleneck |
| 100 QPS optimization | Correctness, citations, and workflow routing come first |
| Starting project 2 | Project 1 still needs product hardening |
| Turning all modules into agents | Retrieval, ACL, counting, citation and eval must stay deterministic |
| Complex cloud deployment | Deploy after workflow, indexing, eval and Docker build are reliable |
| Claiming enterprise-grade production | Only claim what is verified by tests/artifacts/smoke outputs |

## 7. Success Metrics

### Functional Metrics

| Metric | Target for next phase |
|---|---|
| Intent classification coverage | core 6 intents covered by tests |
| LLM synthesis success | repeated known queries return `synthesis_mode=llm` under healthy provider |
| Citation validity | verifier passes on supported answers |
| No-answer correctness | no unsupported answer for evidence-insufficient cases |
| Reference count tool | deterministic result or precise blocked reason |

### Evaluation Metrics

| Metric | Target |
|---|---|
| Retrieval Hit@5 / Recall@5 | improve over current dense baseline |
| Citation accuracy | target >= 95% on regression set |
| Answer faithfulness | target >= 95% after RAGAS/custom judge exists |
| P95 latency | measured before claiming target |
| Cost per query | measured before claiming target |

## 8. Review Questions

These questions must be answered before P1/P2 implementation, but do not block P0:

1. Which first real enterprise connector should be supported: local upload, Confluence, SharePoint, Feishu, Notion, or Git?
2. Should the next embedding path be local `bge-m3` or an external embedding API?
3. Should Postgres metadata store be introduced before or after query intent routing?
4. What is the first realistic permission model: single-tenant API key, user/group ACL, or full tenant isolation?
5. Which eval set should become the source of truth for product regression?

## 9. P0 Acceptance Checklist

P0 is complete only when all are true:

- `docs/product-requirements.md`, `docs/product-workflows.md`, `docs/product-api-contract.md`, and `docs/product-data-model.md` are present.
- Query intent and strategy are returned by `/api/v1/query`.
- `definition` and `count` workflows are implemented and tested.
- Normal UI does not require manual trace ID entry. 已完成；手动 trace/thread 覆盖只保留在高级调试设置。
- LLM answer path returns `synthesis_mode=llm` under a healthy provider.
- Fallback path returns a visible `fallback_reason`.
- Regression tests pass locally.
- README/status docs are updated with evidence-backed claims only.

Current P0 boundary:

```text
Task 1-5 are implemented and tested.
Task 6-10 remain pending: deterministic tool-result answer pinning, UI diagnostics display, intent eval artifact, final status sync, commit/push.
```
