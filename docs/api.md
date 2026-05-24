# API 文档

> 占位文档。Sprint 3 把 FastAPI 路由跑通后用 `app.openapi()` 自动生成。

## 端点速览（计划）

| 端点 | 方法 | 描述 | Sprint |
|---|---|---|---|
| `/health` | GET | 健康检查 | 0（已有） |
| `/api/v1/query` | POST | 主问答接口（含 intent 路由） | 3 |
| `/api/v1/query/stream` | POST | SSE 流式响应 | 5 |
| `/api/v1/ingest` | POST | 批量入库（admin） | 1 |
| `/api/v1/feedback` | POST | 用户反馈（点赞/点踩） | 4 |

## 认证（Sprint 4 加）

- API Key（`X-API-Key` header）
- Rate limit（每 key 100 QPS）

## 错误码

- 400：请求格式错误（Pydantic 校验失败）
- 401：缺少 / 错误的 API Key
- 422：业务校验失败（如 question 超长）
- 429：超出 rate limit
- 500：服务端错误（具体见 Langfuse trace）

详细 schema 见 `src/api/schemas.py`。
