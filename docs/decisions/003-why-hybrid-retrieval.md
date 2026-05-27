# ADR 003：为什么 Hybrid Retrieval 优先于 Dense-only

- **日期**：2026-05-28
- **状态**：Accepted
- **作者**：sundewang（项目 1 owner）

## 背景

Sprint 1 已经完成 FAISS dense retrieval baseline。
Dense retrieval 对语义近似问题有效，但企业知识场景里大量查询依赖精确关键词，例如术语、人名、型号、文件名、协议名、法条号和论文概念。
只依赖 dense retrieval 容易漏掉关键词精确匹配结果。

## 候选方案对比

| 方案 | 优势 | 劣势 |
|---|---|---|
| Dense-only | 架构简单，语义召回好 | 关键词、型号、缩写、精确术语容易漏召回 |
| Sparse-only BM25 | 精确词命中稳定，解释性好 | 语义改写、同义表达和跨语言召回较弱 |
| Dense + BM25 + RRF | 同时保留语义召回与关键词召回，RRF 不依赖不同检索器分数尺度 | 比 dense-only 多一个索引/融合步骤 |
| Dense + BM25 + learned fusion | 可进一步调优融合权重 | 需要标注数据和训练/调参，不适合 Sprint 2 |

## 决策

Sprint 2 采用 Dense + BM25 + RRF 的 hybrid retrieval baseline。
BM25 负责 exact-term 和 keyword-heavy queries；dense retrieval 负责语义候选；RRF 负责融合排名。
Cross-Encoder rerank 作为可选后处理阶段：本地模型可用时执行，不可用时返回明确 blocked reason。

## 理由

1. **覆盖两类高频查询**：BM25 强化精确词匹配，dense retrieval 保留语义匹配，组合比单一路径稳。

2. **RRF 简单可审计**：RRF 只依赖各检索器排名，不依赖 BM25 分数和向量相似度分数的绝对尺度，适合作为第一版混合融合。

3. **符合 deterministic service 原则**：BM25、dense search、RRF、rerank 都是独立服务函数，Sprint 2 不引入 LangGraph 或 MCP 编排。

4. **便于离线评估**：hybrid retrieval 可以通过本地 fixture 和 dry-run benchmark 验证 wiring；真实 Recall@5 需要标注集后再记录。

## 影响

- `src/retrieval/sparse.py` 实现 BM25 sparse retriever。
- `src/retrieval/hybrid.py` 实现 `reciprocal_rank_fusion(...)`。
- `scripts/benchmark.py` 支持 `--retrieval dense,hybrid --top-k 5` 的本地 smoke benchmark。
- `docs/benchmark.md` 只记录已运行 smoke 输出，不把 smoke latency 当作 Recall、RAGAS 或 QPS 指标。

## 后续

- 真实质量评估需要补足带 ground truth 的检索测试集。
- Sprint 3 可以把 hybrid retrieval 接入 Agent graph，但不能回头改变 Sprint 2 的 deterministic service 边界。
