# 性能基准报告

> Sprint 1-5 只记录已执行命令产生的本地结果。未运行的评测指标保持待测，不编造结果。
> 当前推荐使用 `--output` 保存 JSON 结果到 `eval/results/`，让 benchmark 成为可复跑 artifact。

## Sprint 1 本地基线

测试日期：2026-05-28

测试环境：Windows 本地开发环境，Python 3.11.15，`uv run`，本地样本目录 `data`。

嵌入后端：`hash`，即 `LocalHashEmbeddings` 本地确定性 fallback。该结果用于证明 Sprint 1 本地闭环可运行，不代表 `bge-m3` 真实语义检索质量。

| 命令 | 结果 | 本地输出来源 |
|---|---:|---|
| `uv run python scripts/ingest_pdfs.py data` | `2.846477000042796s` | 输出 `status=ok`，`documents_loaded=15`，`chunks_created=93`，`index_dir=data\\faiss\\sprint1` |
| `uv run python scripts/run_research_loop.py --question "Summarize the indexed evidence"` | `0.11293730000033975s` | 输出 `status=ok`，生成 3-step plan、5 条 evidence、`session_id=20260528T014412Z-8ad8de02` |

未测项：Recall@5、RAGAS Faithfulness、Answer Relevancy、P95 延迟、单 query 成本、最大并发均未在 Sprint 1 运行，保持待测。

## Sprint 2 本地检索 / 评估脚手架基线

测试日期：2026-05-28

测试环境：Windows 本地开发环境，Python 3.11.15，`uv run`，本地样本目录 `data`。

嵌入后端：`hash`，即 `LocalHashEmbeddings` 本地确定性 fallback。该结果只证明 dense / hybrid retrieval wiring 可运行，不代表 `bge-m3` 或 Cross-Encoder rerank 的真实质量。

| 命令 | 结果 | 本地输出来源 |
|---|---:|---|
| `uv run python eval/run_ragas.py --dry-run` | `examples=3` | 输出 `status=ok`，`mode=dry-run`，校验字段 `ground_truth/question`；`faithfulness`、`answer_relevancy`、`context_precision`、`context_recall` 均为 `pending_real_run` |
| `uv run python scripts/benchmark.py --retrieval dense,hybrid --top-k 5` | dense `0.037620099959895015s`; hybrid `0.003779200022108853s` | 输出 `status=ok`，`documents=93`，dense returned `5`，hybrid returned `5`，sources 均来自 `data\\attention_is_all_you_need.pdf` |

未测项：Recall@5、RAGAS Faithfulness、Answer Relevancy、端到端 P95 延迟、单 query 成本、最大并发 / QPS 均未在 Sprint 2 smoke 中计算，保持待测。

## Sprint 3 本地 Graph / API / MCP Smoke

测试日期：2026-05-28

测试环境：Windows 本地开发环境，Python 3.11.15，`uv run`，本地 fixture / tmp 目录。

嵌入后端：`hash`，即 `LocalHashEmbeddings` 本地确定性 fallback。该结果只证明 LangGraph、citation validation、API query 和 MCP tool wiring 可运行，不代表真实语义检索质量。

| 命令 | 结果 | 本地输出来源 |
|---|---:|---|
| `uv run pytest tests/unit/test_agents.py tests/unit/test_citation.py tests/integration/test_query_api.py tests/integration/test_mcp_server.py` | `9 passed, 3 warnings` | 输出 graph/citation/query API/MCP Sprint 3 测试全部通过；warnings 来自 FAISS/SWIG 第三方类型 |
| `uv run pytest tests/unit/test_retrieval.py tests/unit/test_context_builder.py` | `10 passed, 3 warnings` | 输出 Sprint 1-2 retrieval/context 回归测试通过；warnings 来自 FAISS/SWIG 第三方类型 |
| `uv run python -c "from src.main import app; print(app.title)"` | `KnowledgeOps` | FastAPI app import-level smoke |
| `uv run python -c "from src.mcp.server import mcp; print(mcp.name if hasattr(mcp, 'name') else 'knowledge-ops')"` | `knowledge-ops` | MCP server import-level smoke |
| `uv run python -m src.mcp.server --help` | blocked | 当前模块入口会启动 `mcp.run(transport="stdio")`，不是 bounded help/CLI mode，按 Sprint 3 goal 不作为无界 smoke 启动 |

未测项：Claude Desktop GUI 端到端接入、真实 MCP client 手动配置、真实 bge-m3 检索质量、Recall@5、RAGAS Faithfulness、P95 延迟、成本和 QPS 均未在 Sprint 3 smoke 中计算，保持待测或人工边界。

## Sprint 4 Policy / LLMOps / Guardrails Smoke

测试日期：2026-05-28

测试环境：Windows 本地开发环境，Python 3.11.15，`uv run`，本地 fixture / tmp 目录。

Sprint 4 smoke 只验证本地可测试的 policy、guardrails、observability dry-run、MemorySaver/PostgresSaver 可选边界、API key auth 和内存 rate limit。未连接真实 Langfuse、Postgres、Redis、外部付费模型或云服务。

| 命令 | 结果 | 本地输出来源 |
|---|---:|---|
| `uv run pytest tests/unit/test_policy.py` | `5 passed` | Complexity Classifier、Model Router、LocalResponseCache、FallbackPolicy 本地测试通过 |
| `uv run pytest tests/unit/test_guardrails.py` | `6 passed` | Unicode normalization、two-level injection detection、model judge blocked reason、guardrail metrics hook 测试通过 |
| `uv run pytest tests/unit/test_observability.py` | `11 passed` | BusinessMetricsRecorder、Langfuse dry-run disable、SDK env 映射、graph callback hook、policy/citation metrics hook、Langfuse v4 feedback score helper 测试通过 |
| `uv run pytest tests/unit/test_memory.py` | `4 passed` | 默认 MemorySaver、PostgresSaver configured fallback、injected Postgres factory boundary 测试通过 |
| `uv run pytest tests/integration/test_auth_rate_limit.py` | `5 passed` | `/api/v1/query` API key auth、in-memory rate limit、`/health` 不保护测试通过 |
| `uv run pytest tests/unit/test_agents.py tests/integration/test_query_api.py tests/integration/test_mcp_server.py` | `6 passed, 3 warnings` | Sprint 3 graph/API/MCP 回归通过；warnings 来自 FAISS/SWIG 第三方类型 |
| `uv run pytest tests/unit/test_retrieval.py tests/unit/test_context_builder.py` | `11 passed, 3 warnings` | Sprint 2 retrieval/context 回归通过；warnings 来自 FAISS/SWIG 第三方类型 |
| `uv run python -c "from src.main import app; print(app.title)"` | `KnowledgeOps` | FastAPI app import-level smoke |
| `uv run python -c "from src.policy import ComplexityClassifier, ModelRouter, FallbackPolicy; print('policy-import-ok')"` | `policy-import-ok` | Policy import/local smoke |
| `uv run python -c "from src.guardrails.injection import detect_injection; print(detect_injection('hello')[0])"` | `False` | Guardrails import/local smoke |
| `uv run python -c "from src.observability.langfuse_setup import get_langfuse_handler; handler = get_langfuse_handler(); print('langfuse-disabled' if handler is None else 'langfuse-configured')"` | `langfuse-disabled` | Langfuse dry-run smoke；本地默认不构造真实 handler、不要求 Langfuse server |

未测项：真实 Langfuse server trace、真实 PostgresSaver 连接、Redis-backed rate limit、真实 bge-m3 检索质量、Recall@5、RAGAS Faithfulness、P95 延迟、成本和 QPS 均未在 Sprint 4 smoke 中计算，保持待测或显式可选集成边界。

## Sprint 5 Streaming / Feedback / Demo / Benchmark Smoke

测试日期：2026-05-28

测试环境：Windows 本地开发环境，Python 3.11.15，`uv run`，本地样本目录 `data`。未启动 Docker、真实 Langfuse server、云服务或长运行 Streamlit server。

| 命令 | 结果 | 本地输出来源 |
|---|---:|---|
| `uv run pytest tests/integration/test_streaming.py` | `2 passed, 3 warnings` | `/api/v1/query/stream` 返回有序 SSE `progress/progress/completion`，并继承 Sprint 4 API key 保护；warnings 来自 FAISS/SWIG 第三方类型 |
| `uv run pytest tests/integration/test_feedback.py` | `2 passed` | `/api/v1/feedback` 本地捕获 score/comment/source；默认 Langfuse disabled 时返回明确配置状态 |
| `uv run pytest tests/integration/test_frontend_demo.py` | `2 passed` | Streamlit demo 的 SSE parser 与 API key header helper 可导入测试 |
| `uv run python -m py_compile frontend/app.py` | passed | Demo UI 文件语法检查通过 |
| `uv run python -c "import streamlit; print(streamlit.__version__)"` | `1.57.0` | Sprint 5 唯一新增直接依赖可导入 |
| `uv run python scripts/benchmark.py --retrieval dense,hybrid --top-k 5 --output eval/results/benchmark_latest.json` | latest latency 写入 `eval/results/benchmark_latest.json` | 输出 `status=ok`，`documents=93`，dense returned `5`，hybrid returned `5`，sources 均来自 `data\\attention_is_all_you_need.pdf` |

Sprint 5 未测项：

- 大规模 / 生产 Recall@5：当前只完成 20 条本地 source/page 标注集评估，尚未覆盖多文档生产语料。
- RAGAS：脚本输出 `pending_real_run`，未运行真实 RAGAS 指标。
- QPS / P95：脚本输出 `pending_load_test`，未运行 Locust 100 QPS x 5min。
- 单 query 成本：本地 hash embedding / deterministic fallback smoke 不产生真实 LLM 计费数据。
- Docker Compose 全量联调：已在 2026-06-22 单独执行并记录，见下方 Docker Compose + Langfuse smoke 小节。
- Cloud deployment、demo video、resume finalization、job applications：非代码自动化交付，不能声明为已自动完成。

## Sprint 5 小规模 Retrieval Hit@5 / Recall@5

测试日期：2026-05-28

测试环境：Windows 本地开发环境，Python 3.11.15，`uv run`，本地样本目录 `data`，标注集 `eval/retrieval_qa.jsonl`，20 条 question -> expected source/page，embedding backend `hash`。

| 命令 | 结果 | 本地输出来源 |
|---|---:|---|
| `uv run python scripts/evaluate_retrieval.py --dataset eval/retrieval_qa.jsonl --docs-dir data --retrieval dense,hybrid --top-k 5 --embedding-backend hash --output eval/results/retrieval_latest.json` | dense Hit@5 / question Recall@5 `0.75` (`15/20`)，MRR@5 `0.5574999999999999`；hybrid Hit@5 / question Recall@5 `1.0` (`20/20`)，MRR@5 `0.7791666666666667` | 输出 `status=ok`，`dataset_examples=20`，`documents=93`，latest latency 写入 `eval/results/retrieval_latest.json` |

边界：这是 source/page 命中率，不是答案质量评估；只覆盖 `attention_is_all_you_need.pdf` 的 20 条本地标注问题；`hash` embedding 用于本地确定性评估，不代表 `bge-m3` 真实语义检索质量。

## Docker Compose + Local Langfuse Smoke

测试日期：2026-06-22

测试环境：Windows 本地开发环境，Docker `29.4.3`，Docker Desktop `4.73.0`，Docker Compose `v5.1.3`。

| 命令 / 检查 | 结果 | 本地输出来源 |
|---|---:|---|
| `docker compose up -d --build` | passed | `app`、Milvus、Langfuse web/worker、ClickHouse、Postgres、Redis、MinIO 均启动 |
| `docker compose ps` | all required services up | `app`、Milvus、ClickHouse、Postgres、Redis、MinIO 显示 healthy；Langfuse web/worker 显示 up |
| `Invoke-WebRequest http://localhost:8000/health` | `200` | `{"status":"ok","version":"0.0.1"}` |
| `Invoke-WebRequest http://localhost:3000` | `200` | Langfuse web HTML returned |
| `Invoke-WebRequest http://localhost:9092/healthz` | `200` | Milvus health endpoint returned `OK` |
| POST `/api/v1/query` | `200` | 返回 confidence `0.85`、5 条 citations、artifact session `20260622T065008Z-7380c05d` |
| POST `/api/v1/feedback` | `200` | `langfuse_status=recorded` |
| POST `/api/v1/query/stream` | passed | SSE 顺序为 `progress -> progress -> completion`，artifact session `20260622T065503Z-d21505ba` |
| ClickHouse `traces` | trace found | Langfuse trace id `54c7f956ce5e27e7daf5fd007adc051e` |
| ClickHouse `scores` | score found | score trace id 同为 `54c7f956ce5e27e7daf5fd007adc051e`，score value `1` |

本次 Docker smoke 修复了 4 个环境集成问题：

- `ENCRYPTION_KEY` 必须以字符串传给 Langfuse v3 worker，否则会被拒绝。
- Windows bind mount 会导致 ClickHouse `Permission denied`，ClickHouse 数据和日志改为 Docker named volumes。
- Docker app 镜像使用 lightweight 依赖和 lazy HuggingFace import，避免默认安装 Torch/CUDA 大包。
- Langfuse callback trace id 与 feedback score trace id 已通过 deterministic 32-hex mapping 对齐。

详细证据见 `docs/docker-compose-smoke.md`。

## Paid API Smoke

测试日期：2026-06-22

当前 `.env` 中 OpenAI-compatible API key/base URL 可被 Docker app 读取，外部 endpoint 可返回模型列表。最新可复跑命令：

```powershell
uv run python scripts/smoke_external_interfaces.py --strict --include-container-provider --output eval/results/external_smoke_latest.json
```

结论如下：

| 检查 | 结果 |
|---|---|
| `/models` | passed，返回 18 个模型，其中 DeepSeek 命名模型 2 个 |
| `deepseek-v4-pro` | passed，最小请求返回 `ok` |
| `deepseek-v4-flash` | passed，最小请求返回 `ok` |
| Docker app container provider call | passed，容器内按 `.env` 配置调用 `deepseek-v4-pro` 返回 `ok` |
| `/api/v1/query` LLM synthesis | passed，`synthesis_mode=llm`、`synthesis_status=ok`、`synthesis_model=deepseek-v4-pro` |
| `deepseek-chat` | expected unavailable，当前供应商返回 `model_not_found` |
| `deepseek-reasoner` | expected unavailable，当前供应商返回 `model_not_found` |

该命令本轮输出 `summary.status=ok`、`checks_total=15`，并将完整结果写入 `eval/results/external_smoke_latest.json`。

边界：这证明当前 OpenAI-compatible 供应商暴露的 `deepseek-v4-pro` / `deepseek-v4-flash` 可做 Chat Completions 调用，且 `deepseek-v4-pro` 已接入 `/api/v1/query` synthesis 主链路；不证明官方 DeepSeek endpoint、`deepseek-chat` / `deepseek-reasoner` 官方别名、成本统计、RAGAS 答案质量或生产负载已经完成验证。

## 测试环境（计划）

- 单机 Docker：1 实例 KnowledgeOps + 1 Milvus standalone + 1 Langfuse
- LLM：当前 OpenAI-compatible 供应商的 `deepseek-v4-pro` / `deepseek-v4-flash` 最小调用已验证；`deepseek-v4-pro` 已接入主查询 synthesis，失败或无 key 时回退 deterministic fallback；成本/QPS/答案质量待真实评测
- 嵌入：bge-m3（CPU）
- 测试集：100 条 QA pair（covering FAQ / 知识库 / 闲聊 / 注入攻击）

## 指标

| 指标 | Baseline (Sprint 2 末) | 最终 (Sprint 5 末) | 目标 |
|---|---|---|---|
| 检索 Recall@5 | _待测_ | local 20-case source/page Hit@5：dense `0.75`，hybrid `1.0`；大规模标注集待测 | ≥ 85% |
| Faithfulness | _待测_ | `pending_real_run` | ≥ 95% |
| Answer Relevancy | _待测_ | `pending_real_run` | ≥ 90% |
| 端到端 P95 延迟 | _待测_ | `pending_load_test` | < 3s |
| 单 query 成本 | _待测_ | _待测，主链路已接真实 LLM 但未完成成本统计_ | < ¥0.05 |
| 最大并发 | _待测_ | `pending_load_test` | ≥ 100 QPS |

## 对比实验（Sprint 2-3）

按 `scripts/benchmark.py` 跑：
- 嵌入模型：bge-small-en vs bge-m3 vs OpenAI text-embedding-3-small
- chunk_size：200 / 500 / 1000
- 检索策略：dense-only / hybrid-RRF / hybrid+rerank
- Top-K：3 / 5 / 10 / 20+rerank-5
