# Sprint 5 交付边界

本文档区分本地代码交付、环境相关验证和人工交付动作。未执行的动作不声明为已完成。

## 本地代码交付

| 项目 | 状态 | 验证方式 |
|---|---|---|
| `/api/v1/query/stream` | 已实现 | `uv run pytest tests/integration/test_streaming.py` |
| `/api/v1/feedback` | 已实现 | `uv run pytest tests/integration/test_feedback.py` |
| Streamlit demo | 已实现 | `uv run pytest tests/integration/test_frontend_demo.py`，`uv run python -m py_compile frontend/app.py` |
| Final benchmark smoke | 已执行 | `uv run python scripts/benchmark.py --retrieval dense,hybrid --top-k 5 --output eval/results/benchmark_latest.json` |
| Small retrieval eval | 已执行 | `uv run python scripts/evaluate_retrieval.py --dataset eval/retrieval_qa.jsonl --docs-dir data --retrieval dense,hybrid --top-k 5 --embedding-backend hash --output eval/results/retrieval_latest.json` |
| Docker Compose full-stack smoke | 已执行 | `docker compose up -d --build`；`app`、Milvus、Langfuse、ClickHouse、Postgres、Redis、MinIO 均启动，见 `docs/docker-compose-smoke.md` |
| Local Langfuse trace / score | 已执行 | API query + feedback 后，ClickHouse `traces` 和 `scores` 同 id 落库 |
| External interface smoke artifact | 已执行 | `uv run python scripts/smoke_external_interfaces.py --strict --include-container-provider --output eval/results/external_smoke_latest.json`；15 个检查通过，旧别名按预期不可用 |
| CI workflow | 已补充，本地等价通过 | `.github/workflows/ci.yml` 已覆盖 ruff、py_compile、FastAPI import smoke、pytest；远端 green 后再加 README badge |
| Demo dry run | 已执行 | Streamlit 本地页面和 health 返回成功；demo SSE query + feedback 路径通过，见 `docs/demo-dry-run.md` |
| README / API / benchmark 文档 | 已更新 | 本文档与 `docs/api.md`、`docs/benchmark.md`、`README.md` |

## 环境相关验证

| 项目 | 当前状态 | 不声明完成的原因 |
|---|---|---|
| Cloud deployment | 手动边界 | 需要云账号、域名、密钥、镜像仓库或目标平台配置 |
| Locust 100 QPS x 5min | 手动待跑 | 本次本地验证未启动长运行 API server 和 headless Locust 压测 |
| OpenAI-compatible DeepSeek 命名模型 | 最小调用已验证 | 当前供应商可列 18 个模型；`deepseek-v4-pro` / `deepseek-v4-flash` 返回 `ok`；`deepseek-chat` / `deepseek-reasoner` 在当前供应商不可用 |
| 真实 bge-m3 Docker runtime | 手动边界 | Docker app 使用 lightweight 依赖和 `hash` embedding；未下载 torch/sentence-transformers 大模型栈 |
| 真实 RAGAS / 生产级 Recall@5 | 待真实数据集 | 当前只有 20 条本地 source/page 标注集；尚未覆盖多文档生产语料和答案质量 |

## Demo Video 手动检查清单

本仓库不能自动录制、上传或发布 demo video。可用于手动录制的本地流程：

1. 启动 API：`uv run uvicorn src.main:app --reload`
2. 启动 demo：`uv run streamlit run frontend/app.py`
3. 在 demo 中提交问题，例如 `Summarize the indexed evidence`
4. 展示 progress、plan、answer、citations、trace/session metadata
5. 提交 Useful / Neutral / Not useful feedback
6. 说明未测指标：Recall@5、RAGAS、P95、成本、100 QPS

已执行的 bounded dry run 见 `docs/demo-dry-run.md`。该记录不等同于已录制或上传 demo video。

## Resume / Job Application 边界

本仓库只提供可引用的项目事实，不自动提交简历、更新公开主页或投递岗位。

可安全引用的事实：

- 构建了 FastAPI + LangGraph 的研究型 Knowledge Agent，本地支持 `plan -> retrieve -> synthesize -> report -> verify`。
- 实现了 REST 查询、SSE streaming 查询、反馈捕获、API key 认证、本地 rate limit 和 Streamlit demo。
- 支持本地 FAISS/hash embedding smoke、MCP server 接入路径、Docker Compose 本地 Langfuse trace/score smoke。
- Sprint 5 本地 benchmark smoke 返回 `status=ok`、`documents=93`，dense / hybrid 均返回 5 条候选，最新输出可保存到 `eval/results/benchmark_latest.json`。
- 20 条本地 source/page 标注集上 dense Hit@5 / Recall@5 为 `0.75`，hybrid Hit@5 / Recall@5 为 `1.0`，最新输出可保存到 `eval/results/retrieval_latest.json`。
- 2026-06-22 本地 Docker Compose 全栈 smoke 通过，Langfuse trace/score 在本地 ClickHouse 同 id 落库。

不可声明为事实，除非后续真实执行并记录输出：

- 已完成公网云部署。
- 已通过 100 QPS x 5min 压测。
- Recall@5 达到 85% 或 RAGAS Faithfulness 达到目标。
- 已上传 demo video、已投递岗位、已被外部平台验证。
- 官方 DeepSeek endpoint、`deepseek-chat` / `deepseek-reasoner` 官方别名或主链路真实付费生成已完成生产验证；当前只验证了 OpenAI-compatible 供应商的 `deepseek-v4-pro` / `deepseek-v4-flash` 最小调用。

## 后续计划边界

当前不优先：

- 不优先上云。
- 不优先接真实付费 LLM。
- 不优先重写 Streamlit 为 Next.js。
- 不优先做 100 QPS。
- 不优先把项目 2 提前开工。
- 不优先把所有模块都 Agent 化。
- 不优先追求“企业级”措辞，而是优先保证每个 claims 有证据。
