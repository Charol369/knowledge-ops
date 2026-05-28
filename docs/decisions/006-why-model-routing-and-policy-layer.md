# ADR 006：为什么采用本地 Policy Layer 与模型路由

- **日期**：2026-05-28
- **状态**：Accepted
- **作者**：sundewang（项目 1 owner）

## 背景

Sprint 1-3 已经完成本地证据链路：ingest、dense/hybrid retrieval、context builder、artifact persistence、LangGraph research graph、citation validation、`/api/v1/query` 和 MCP tool layer。
Sprint 4 的目标是在这些能力之上加入生产控制层，使问题复杂度、模型层级、缓存命中、retry/fallback 和观测指标有明确边界。

该层不能依赖真实付费模型或外部 API key。
模型路由在 Sprint 4 中只选择抽象 tier，例如 `tier1`、`tier2`、`tier3`，不直接调用真实模型。

## 候选方案对比

| 方案 | 优势 | 劣势 |
|---|---|---|
| 在 graph 节点中硬编码 complexity/model_tier | 实现快 | 不可复用，难测试，无法统一记录观测指标 |
| 用 LLM 判断复杂度 | 更灵活 | 依赖真实模型/API key，违反 Sprint 4 local-first 约束 |
| 直接按 endpoint 固定模型 | 简单稳定 | 无法区分闲聊、普通问答和复杂研究请求 |
| 本地 deterministic policy layer | 可测试、可审计、无外部依赖，便于埋点 | 启发式规则不等于最终智能调度策略 |

## 决策

Sprint 4 采用本地 deterministic Policy Layer：

- `ComplexityClassifier` 用透明启发式规则把问题分为 `simple`、`standard`、`complex`。
- `ModelRouter` 把复杂度映射到抽象模型层级：`simple -> tier1`、`standard -> tier2`、`complex -> tier3`。
- `LocalResponseCache` 提供本地 TTL cache primitive。
- `FallbackPolicy` 提供 transient retry 判断和 tier fallback 规则。
- `decide_policy(...)` 汇总 classifier/router/cache_hit，供 graph planner 边界使用。

## 理由

1. **不依赖付费模型**：复杂度判断和模型路由完全本地执行，单元测试不需要 DeepSeek、Claude、OpenAI 或任何外部 API key。

2. **成本控制前置**：graph state 显式保留 `complexity` 和 `model_tier`，避免后续节点各自临时决定模型层级。

3. **可观测性更清楚**：planner 调用 policy 后记录 complexity、model tier、cache hit 和 trace_id，后续可以按请求类型分析成本与风险。

4. **可靠性策略可测试**：retry/fallback 只对 timeout、429、5xx、unavailable 等 transient failure 生效；401、403、validation、404 等 permanent failure 不被隐藏。

5. **保留后续替换空间**：Sprint 4 使用启发式规则是为了本地验收；未来可替换为更复杂 classifier，但外部接口和测试合同保持稳定。

## 影响

- `src/policy.py` 成为 Complexity Classifier、Model Router、Cache / Retry / Fallback 的统一入口。
- `src/agents/planner.py` 不再硬编码 `standard`，而是调用 `decide_policy(...)` 并写回 `complexity`、`model_tier`。
- `/api/v1/query` response 中的 `model_tier_used` 来自 graph state，不要求真实模型访问。
- `tests/unit/test_policy.py` 覆盖本地 policy primitives。
- `tests/unit/test_observability.py` 覆盖 planner policy metrics hook。

## 后续

- 如果未来引入真实模型调用，应保持 model tier 与具体 provider/model name 解耦。
- 如果要将 cache 从本地内存升级到 Redis，必须新增明确配置、测试和 blocked reason，不应让 Sprint 4 本地验收依赖 Redis。
