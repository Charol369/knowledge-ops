# 性能基准报告

> Sprint 1-2 只记录本地 smoke baseline。未运行的评测指标保持待测，不编造结果。

## Sprint 1 本地基线

测试日期：2026-05-27

测试环境：Windows 本地开发环境，Python 3.11.15，`uv run`，本地样本目录 `data`。

嵌入后端：`hash`，即 `LocalHashEmbeddings` 本地确定性 fallback。该结果用于证明 Sprint 1 本地闭环可运行，不代表 `bge-m3` 真实语义检索质量。

| 命令 | 结果 | 本地输出来源 |
|---|---:|---|
| `uv run python scripts/ingest_pdfs.py data` | `2.1549639999866486s` | 输出 `status=ok`，`documents_loaded=15`，`chunks_created=93`，`index_dir=data\\faiss\\sprint1` |
| `uv run python scripts/run_research_loop.py --question "Summarize the indexed evidence"` | `0.245924900053069s` | 输出 `status=ok`，生成 3-step plan、5 条 evidence、`session_id=20260527T155014Z-922de924` |

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

## 测试环境（计划）

- 单机 Docker：1 实例 KnowledgeOps + 1 Milvus standalone + 1 Langfuse
- LLM：DeepSeek API
- 嵌入：bge-m3（CPU）
- 测试集：100 条 QA pair（covering FAQ / 知识库 / 闲聊 / 注入攻击）

## 指标

| 指标 | Baseline (Sprint 2 末) | 最终 (Sprint 5 末) | 目标 |
|---|---|---|---|
| 检索 Recall@5 | _待测_ | _待测_ | ≥ 85% |
| Faithfulness | _待测_ | _待测_ | ≥ 95% |
| Answer Relevancy | _待测_ | _待测_ | ≥ 90% |
| 端到端 P95 延迟 | _待测_ | _待测_ | < 3s |
| 单 query 成本 | _待测_ | _待测_ | < ¥0.05 |
| 最大并发 | _待测_ | _待测_ | ≥ 100 QPS |

## 对比实验（Sprint 2-3）

按 `scripts/benchmark.py` 跑：
- 嵌入模型：bge-small-en vs bge-m3 vs OpenAI text-embedding-3-small
- chunk_size：200 / 500 / 1000
- 检索策略：dense-only / hybrid-RRF / hybrid+rerank
- Top-K：3 / 5 / 10 / 20+rerank-5
