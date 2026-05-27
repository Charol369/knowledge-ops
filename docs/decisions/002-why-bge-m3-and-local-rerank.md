# ADR 002：为什么选 bge-m3 嵌入模型与本地 rerank 边界

- **日期**：2026-05-28
- **状态**：Accepted
- **作者**：sundewang（项目 1 owner）

## 背景

KnowledgeOps 的知识库场景需要同时处理中文、英文、技术术语、论文片段和企业文档。
Sprint 1 已经用 `LocalHashEmbeddings` 跑通 FAISS dense baseline，但该 fallback 只用于离线 smoke test，不代表真实语义检索质量。
Sprint 2 需要明确真实嵌入与 rerank 的边界，同时保持本地验收不依赖付费 API、云服务或真实模型下载。

## 候选方案对比

| 方案 | 优势 | 劣势 |
|---|---|---|
| OpenAI embedding API | 质量稳定，生态成熟 | 依赖外部付费 API，不符合 local-first 验收 |
| 小型英文 embedding | 下载和运行成本低 | 中文和跨语言企业知识场景不稳 |
| `BAAI/bge-m3` | 多语言、长文本、可本地自托管，适合中英混合知识库 | 首次下载模型较大，本地机器可能不可用 |
| `LocalHashEmbeddings` | 零外部依赖、确定性、适合测试 | 不提供真实语义质量，只能做 smoke baseline |

## 决策

真实语义嵌入优先选 `BAAI/bge-m3`；本地验收和 CI smoke test 使用 `LocalHashEmbeddings` fallback。
Cross-Encoder rerank 优先使用本地模型路径或可注入 scorer；如果本地 rerank 模型不可用，系统返回精确 `blocked_reason`，不伪造 rerank 分数。

## 理由

1. **local-first 与生产可迁移兼容**：`bge-m3` 可以本地部署，符合项目不默认依赖付费 API 的约束；hash fallback 保证无模型下载时仍能验证代码路径。

2. **中英混合知识库更合适**：项目样本文档、中文需求和英文论文并存，`bge-m3` 比纯英文小模型更符合长期目标。

3. **测试与质量声明分离**：hash fallback 只证明 pipeline wiring 可运行；Recall@5、RAGAS、faithfulness 等质量指标必须等真实评估命令运行后再记录。

4. **rerank 不伪造输出**：Cross-Encoder 精排如果没有本地模型，就返回 blocked reason；测试可以注入 scorer 验证排序逻辑，不把测试 scorer 当成真实模型能力。

## 影响

- `src/ingest/embedder.py` 保留 `huggingface` 与 `hash/local/fake` backend。
- `src/retrieval/rerank.py` 支持本地模型路径、注入 scorer 和 `blocked` 结果。
- `docs/benchmark.md` 中所有 hash fallback 结果只能作为 smoke baseline，不能代表真实语义检索质量。

## 后续

- Sprint 2 只完成本地可测边界。
- 真实 `bge-m3` / `bge-reranker-v2-m3` 指标需要在模型可用后单独运行并记录命令输出。
