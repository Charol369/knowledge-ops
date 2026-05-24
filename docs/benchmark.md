# 性能基准报告

> 占位文档。Sprint 2 末跑出基线，Sprint 5 末跑出最终成绩。

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
