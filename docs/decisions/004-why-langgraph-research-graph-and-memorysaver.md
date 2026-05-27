# ADR 004：为什么采用 LangGraph 研究图与 MemorySaver

- **日期**：2026-05-28
- **状态**：Accepted
- **作者**：sundewang（项目 1 owner）

## 背景

Sprint 1-2 已经建立了本地 ingest、dense/hybrid retrieval、context builder 和 artifact persistence。
Sprint 3 的目标不是再写一个线性 RAG 脚本，而是把 KnowledgeOps 的认知链路表达成可审计的研究型 Agent 图：

```text
plan -> retrieve -> synthesize -> report -> verify
```

该图必须复用 Sprint 1-2 的 deterministic services，并保持 local-first 验收，不要求数据库、Docker、云服务、API key 或付费模型。

## 候选方案对比

| 方案 | 优势 | 劣势 |
|---|---|---|
| 继续使用线性 Python 函数 | 最简单，调试成本低 | 难表达状态、节点顺序、校验节点和后续可恢复执行 |
| 全部塞进一个 Agent prompt | 代码少，看似灵活 | 不可审计，容易绕过检索/引用校验，成本和行为不可控 |
| LangGraph + MemorySaver | 显式状态、节点边界清晰、本地 checkpointer 可用 | 比线性函数多一点状态 schema 和配置 |
| LangGraph + PostgresSaver | 更适合生产持久化 | 需要数据库服务，属于 Sprint 4 以后范围 |

## 决策

Sprint 3 使用 LangGraph 表达研究流程，并在本地验收中使用 `MemorySaver` checkpointer。
Graph 节点只编排认知链路；检索、上下文构建、引用校验和 artifact 写入继续保持 deterministic service 边界。

## 理由

1. **流程可审计**：`planner`、`retrieval_orchestrator`、`synthesizer`、`reporter`、`verifier` 是显式节点，测试可以验证执行路径是 `plan -> retrieve -> synthesize -> report -> verify`。

2. **状态边界清楚**：graph state 保留 `plan`、`evidence`、`context`、`answer`、`citations`、`verification`、`artifact_session_id` 和 `trace_id`，便于 API、MCP 和测试复用同一结构。

3. **不引入 Sprint 4 依赖**：`MemorySaver` 满足 Sprint 3 本地 checkpoint 需求；`PostgresSaver` 需要数据库服务，明确留到后续生产持久化阶段。

4. **复用 Sprint 1-2 合同**：Retrieval Orchestrator 调用已有 loader/splitter/dense/BM25/RRF/ContextBuilder，而不是在 Agent 内重新实现检索逻辑。

5. **结构化输出可验证**：Reporter 抽取 citation，Verifier 使用 citation guardrail 和 Pydantic `Answer` schema 校验输出，避免把“生成了文本”误当成“答案可信”。

## 影响

- `src/agents/graph.py` 提供 `build_graph()` 和 `run_research_graph(...)`。
- `src/agents/orchestrator.py` 负责把 Sprint 2 retrieval/context services 接入 graph state。
- `src/agents/verifier.py` 负责 citation validation 和 structured output validation。
- `/api/v1/query` 以同步本地方式调用 graph，不引入 auth、rate limit、SSE 或 model router。

## 后续

- Sprint 4 可以在保留 graph contract 的前提下加入 policy routing、observability、auth/rate limit 和持久化 checkpointer。
- 真实生产环境如需跨进程恢复，再评估 PostgresSaver 或其他持久化 checkpointer。
