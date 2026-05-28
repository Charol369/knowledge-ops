# 性能基准报告

> Sprint 1-5 只记录已执行命令产生的本地结果。未运行的评测指标保持待测，不编造结果。

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
| `uv run python scripts/benchmark.py --retrieval dense,hybrid --top-k 5` | dense `0.06787819997407496s`; hybrid `0.007698599947616458s` | 输出 `status=ok`，`documents=93`，dense returned `5`，hybrid returned `5`，sources 均来自 `data\\attention_is_all_you_need.pdf` |

Sprint 5 未测项：

- Recall@5：脚本输出 `pending_labeled_eval`，缺少已标注 QA 集与真实评估命令。
- RAGAS：脚本输出 `pending_real_run`，未运行真实 RAGAS 指标。
- QPS / P95：脚本输出 `pending_load_test`，未运行 Locust 100 QPS x 5min。
- 单 query 成本：本地 hash embedding / deterministic fallback smoke 不产生真实 LLM 计费数据。
- Docker Compose 全量联调：未在本次本地 Sprint 5 验证中启动，保持手动/环境相关边界。
- Cloud deployment、demo video、resume finalization、job applications：非代码自动化交付，不能声明为已自动完成。

## 测试环境（计划）

- 单机 Docker：1 实例 KnowledgeOps + 1 Milvus standalone + 1 Langfuse
- LLM：DeepSeek API
- 嵌入：bge-m3（CPU）
- 测试集：100 条 QA pair（covering FAQ / 知识库 / 闲聊 / 注入攻击）

## 指标

| 指标 | Baseline (Sprint 2 末) | 最终 (Sprint 5 末) | 目标 |
|---|---|---|---|
| 检索 Recall@5 | _待测_ | `pending_labeled_eval` | ≥ 85% |
| Faithfulness | _待测_ | `pending_real_run` | ≥ 95% |
| Answer Relevancy | _待测_ | `pending_real_run` | ≥ 90% |
| 端到端 P95 延迟 | _待测_ | `pending_load_test` | < 3s |
| 单 query 成本 | _待测_ | _待测，本地 smoke 无真实 LLM 计费_ | < ¥0.05 |
| 最大并发 | _待测_ | `pending_load_test` | ≥ 100 QPS |

## 对比实验（Sprint 2-3）

按 `scripts/benchmark.py` 跑：
- 嵌入模型：bge-small-en vs bge-m3 vs OpenAI text-embedding-3-small
- chunk_size：200 / 500 / 1000
- 检索策略：dense-only / hybrid-RRF / hybrid+rerank
- Top-K：3 / 5 / 10 / 20+rerank-5
