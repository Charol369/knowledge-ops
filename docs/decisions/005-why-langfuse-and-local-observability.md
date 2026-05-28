# ADR 005：为什么采用 Langfuse 集成路径与本地观测指标

- **日期**：2026-05-28
- **状态**：Accepted
- **作者**：sundewang（项目 1 owner）

## 背景

Sprint 4 需要在 Sprint 1-3 的本地 ingest、retrieval、artifact、LangGraph、API query 和 MCP 基线上加入生产控制能力。
观测层必须支持 trace_id 透传、policy 决策记录、guardrail 决策记录、fallback 记录和 citation verification 记录。

同时，Sprint 4 本地验收不能依赖真实 Langfuse server、真实云服务、真实 API key、Docker 或外部网络成功。
因此观测设计必须区分两类能力：本地 deterministic 指标记录，以及可选的 Langfuse callback 集成路径。

## 候选方案对比

| 方案 | 优势 | 劣势 |
|---|---|---|
| 只依赖 print/logging | 实现最简单 | 难以按 trace_id、policy、guardrail、citation 维度聚合 |
| 直接强制启用 Langfuse | 生产追踪能力强 | 本地验收依赖外部服务和有效凭据，违反 Sprint 4 约束 |
| Prometheus/OpenTelemetry 先行 | 生产指标标准化 | 需要额外依赖和运行时配置，超出 Sprint 4 local-first 范围 |
| 本地 metrics recorder + 可选 Langfuse callback | 本地可测、无外部依赖，同时保留生产追踪边界 | 不代表真实 Langfuse dashboard 已联通 |

## 决策

Sprint 4 采用本地 `BusinessMetricsRecorder` 记录业务指标，并提供 dry-run safe 的 Langfuse callback 集成路径。
默认 `langfuse_enabled=False`，即使本地 `.env` 中存在 Langfuse key，也不会默认构造真实 `CallbackHandler`。
只有显式启用且配置完整时，系统才尝试构造 Langfuse handler；构造失败时安全返回 `None`，不把认证错误当作通过。

## 理由

1. **符合 local-first 验收**：policy、guardrail、citation 和 fallback 指标可以通过单元测试验证，不需要真实 Langfuse、Prometheus 或 OpenTelemetry 后端。

2. **避免假阳性观测声明**：`langfuse-disabled` 是 Sprint 4 可接受默认输出；`langfuse-configured` 只说明本地显式配置存在，不证明真实 server trace 成功。

3. **保留生产迁移路径**：LangGraph invoke config 支持 callback 注入，后续有真实 Langfuse server 时可以沿同一边界启用追踪。

4. **trace_id 一致性**：graph 使用 `thread_id` 或生成的 UUID 作为 trace_id，并通过 API response 返回；metrics 记录也保留 trace_id 以便本地关联。

5. **不新增外部依赖**：Sprint 4 不引入 OpenTelemetry SDK、Prometheus client、真实 Langfuse server 或 Docker 前置条件。

## 影响

- `src/observability/metrics.py` 提供 `BusinessMetricsRecorder` 和全局 `business_metrics`。
- `src/observability/langfuse_setup.py` 提供 dry-run safe 的 `get_langfuse_handler(...)`。
- `src/agents/graph.py` 在 LangGraph invoke config 中可选注入 callbacks，并保留 `thread_id`/`trace_id`。
- `src/agents/planner.py` 记录 policy decision metrics。
- `src/agents/verifier.py` 记录 citation verification metrics。
- `src/guardrails/injection.py` 记录 guardrail decision metrics。
- `docs/benchmark.md` 只记录本地 smoke 输出，不声称真实 Langfuse dashboard 已接入。

## 后续

- 真实 Langfuse self-hosted server、dashboard trace 验证和 flush 行为需要在有本地服务配置后单独运行并记录命令输出。
- 如后续引入 OpenTelemetry 或 Prometheus，应保持业务代码继续依赖 `BusinessMetricsRecorder` 风格接口，而不是直接绑定具体 SDK。
