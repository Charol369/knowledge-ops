# Sprint 5 交付边界

本文档区分本地代码交付、环境相关验证和人工交付动作。未执行的动作不声明为已完成。

## 本地代码交付

| 项目 | 状态 | 验证方式 |
|---|---|---|
| `/api/v1/query/stream` | 已实现 | `uv run pytest tests/integration/test_streaming.py` |
| `/api/v1/feedback` | 已实现 | `uv run pytest tests/integration/test_feedback.py` |
| Streamlit demo | 已实现 | `uv run pytest tests/integration/test_frontend_demo.py`，`uv run python -m py_compile frontend/app.py` |
| Final benchmark smoke | 已执行 | `uv run python scripts/benchmark.py --retrieval dense,hybrid --top-k 5` |
| README / API / benchmark 文档 | 已更新 | 本文档与 `docs/api.md`、`docs/benchmark.md`、`README.md` |

## 环境相关验证

| 项目 | 当前状态 | 不声明完成的原因 |
|---|---|---|
| Docker Compose 全量联调 | 手动待跑 | 本次 Sprint 5 验证未启动 Docker/Milvus/Langfuse 容器 |
| Cloud deployment | 手动边界 | 需要云账号、域名、密钥、镜像仓库或目标平台配置 |
| Locust 100 QPS x 5min | 手动待跑 | 本次本地验证未启动长运行 API server 和 headless Locust 压测 |
| 真实 Langfuse feedback score | 配置后可尝试 | 默认 `LANGFUSE_ENABLED=false`，未使用真实 Langfuse 凭证 |
| 真实 RAGAS / Recall@5 | 待真实数据集 | 缺少已标注 QA 集和真实评估命令输出 |

## Demo Video 手动检查清单

本仓库不能自动录制、上传或发布 demo video。可用于手动录制的本地流程：

1. 启动 API：`uv run uvicorn src.main:app --reload`
2. 启动 demo：`uv run streamlit run frontend/app.py`
3. 在 demo 中提交问题，例如 `Summarize the indexed evidence`
4. 展示 progress、plan、answer、citations、trace/session metadata
5. 提交 Useful / Neutral / Not useful feedback
6. 说明未测指标：Recall@5、RAGAS、P95、成本、100 QPS

## Resume / Job Application 边界

本仓库只提供可引用的项目事实，不自动提交简历、更新公开主页或投递岗位。

可安全引用的事实：

- 构建了 FastAPI + LangGraph 的研究型 Knowledge Agent，本地支持 `plan -> retrieve -> synthesize -> report -> verify`。
- 实现了 REST 查询、SSE streaming 查询、反馈捕获、API key 认证、本地 rate limit 和 Streamlit demo。
- 支持本地 FAISS/hash embedding smoke、MCP server 接入路径、Langfuse dry-run / 可配置 feedback score。
- Sprint 5 本地 benchmark smoke 测得 dense `0.06787819997407496s`、hybrid `0.007698599947616458s`，均返回 5 条候选，样本为 `data` 下 93 个 chunks。

不可声明为事实，除非后续真实执行并记录输出：

- 已完成公网云部署。
- 已通过 100 QPS x 5min 压测。
- Recall@5 达到 85% 或 RAGAS Faithfulness 达到目标。
- 已上传 demo video、已投递岗位、已被外部平台验证。
