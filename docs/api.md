# API 文档

本文档记录当前代码中可本地验证的 FastAPI 合约。详细字段定义以 `src/api/schemas.py` 为准。

## 端点速览

| 端点 | 方法 | 描述 | Sprint | 本地验证 |
|---|---|---|---|---|
| `/health` | GET | 健康检查 | 0 | `tests/integration/test_auth_rate_limit.py` |
| `/api/v1/query` | POST | graph-backed 主问答接口 | 3 | `tests/integration/test_query_api.py` |
| `/api/v1/query/stream` | POST | SSE 流式查询包装，复用 `QueryRequest` 和 graph 查询合约 | 5 | `tests/integration/test_streaming.py` |
| `/api/v1/ingest` | POST | 本地文件/目录 ingest，可选构建 FAISS index | 1 | 单元/脚本 smoke |
| `/api/v1/feedback` | POST | 用户反馈捕获，本地内存记录，Langfuse 安全配置时可提交 score | 5 | `tests/integration/test_feedback.py` |

## 认证与限流

当 `API_AUTH_ENABLED=true` 时，以下路径要求 `X-API-Key`：

- `/api/v1/query`
- `/api/v1/query/stream`
- `/api/v1/feedback`

当 `RATE_LIMIT_ENABLED=true` 时，同一组路径使用本地内存 fixed-window limiter。默认配置来自 `src/config.py`：

| 配置 | 默认值 | 含义 |
|---|---:|---|
| `API_AUTH_ENABLED` | `false` | 是否启用 API key 校验 |
| `API_KEY` | `""` | 期望的 API key |
| `RATE_LIMIT_ENABLED` | `false` | 是否启用本地内存限流 |
| `RATE_LIMIT_REQUESTS` | `60` | 窗口内最大请求数 |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | 限流窗口秒数 |

## `POST /api/v1/query`

请求体复用 `QueryRequest`：

```json
{
  "question": "Summarize the indexed evidence",
  "intent": null,
  "thread_id": "demo-thread",
  "docs_dir": "data",
  "index_dir": "data/faiss/sprint1",
  "artifact_root": null,
  "embedding_backend": "hash"
}
```

响应体为 `QueryResponse`：

```json
{
  "answer": "...",
  "confidence": 0.8,
  "plan": [
    {"step_id": "1", "description": "...", "status": "completed"}
  ],
  "citations": [
    {"source": "data\\attention_is_all_you_need.pdf", "page": 1, "snippet": "..."}
  ],
  "model_tier_used": "tier2",
  "artifact_session_id": "...",
  "trace_id": "demo-thread",
  "needs_human_review": false
}
```

## `POST /api/v1/query/stream`

请求体与 `/api/v1/query` 相同。响应为 `text/event-stream`。当前实现是对既有 graph-backed 查询的有界 SSE 包装：先发送开始事件，graph 完成后发送进度摘要，最后发送完整 `QueryResponse`。

事件顺序：

```text
event: progress
data: {"stage":"started","trace_id":"demo-thread","message":"Query accepted."}

event: progress
data: {"stage":"graph_completed","trace_id":"demo-thread","plan":[...],"citations_count":5,"artifact_session_id":"..."}

event: completion
data: {"answer":"...","confidence":0.8,"plan":[...],"citations":[...],"trace_id":"demo-thread",...}
```

边界：

- 该端点复用后端 graph、artifact、citation 与本地 fallback 行为。
- 当前本地实现不依赖外部 streaming LLM，不要求启动长运行服务器即可通过 `TestClient` 验证。
- 若需要 token-level LLM streaming，应在后续版本扩展 graph/node 层，而不是在前端重写检索或 agent 逻辑。

## `POST /api/v1/feedback`

请求体为 `FeedbackRequest`：

```json
{
  "trace_id": "demo-thread",
  "score": 1,
  "comment": "Useful answer.",
  "source": "streamlit-demo",
  "name": "user_feedback"
}
```

字段约束：

| 字段 | 约束 |
|---|---|
| `trace_id` | 必填，1-256 字符 |
| `score` | 必填，范围 `[-1, 1]` |
| `comment` | 可选，最长 2000 字符 |
| `source` | 可选，最长 128 字符 |
| `name` | 可选，默认 `user_feedback`，最长 128 字符 |

响应体为 `FeedbackResponse`：

```json
{
  "status": "ok",
  "trace_id": "demo-thread",
  "score": 1.0,
  "storage": "local-memory",
  "langfuse_status": "disabled",
  "blocked_reason": null
}
```

Langfuse 边界：

- 默认本地配置 `LANGFUSE_ENABLED=false`，接口仍返回 `status=ok`，并将反馈写入 `BusinessMetricsRecorder` 的内存事件列表。
- 当 `LANGFUSE_ENABLED=true` 且 public/secret key 完整时，接口会尝试提交 Langfuse-compatible score。
- 当 Langfuse 配置不完整或 SDK 调用失败时，接口保留本地捕获，并在 `langfuse_status` / `blocked_reason` 中返回明确状态。

## `POST /api/v1/ingest`

请求体为 `IngestRequest`：

```json
{
  "path": "data",
  "glob": "**/*",
  "build_index": false,
  "index_dir": null,
  "embedding_backend": "hash"
}
```

响应体为 `IngestResponse`。本地路径不存在、文件类型不支持、索引构建失败时返回 `status="blocked"` 和 `blocked_reason`，不伪装为已完成。

## 错误码

| 状态码 | 含义 |
|---:|---|
| 401 | API key 缺失或错误，仅在认证开启且路径受保护时返回 |
| 422 | Pydantic 请求校验失败，例如 `question` 为空或 `score` 超出范围 |
| 429 | 本地 rate limit 超限，仅在限流开启且路径受保护时返回 |
| 500 | 未捕获服务端异常；本地 Sprint 5 测试不依赖真实 Langfuse server |
