# Sprint Backlog · GitHub Project 看板源

> Day7 17:00 前完成的 Sprint 1-5 的 issue 草稿。
> Boss 到 GitHub 仓库 → `Projects` → 新建 Board → 5 列 + Backlog/Done，把下面每条复制成一个 Issue。
>
> Issue title 风格：`[模块] 动作`，方便用 GitHub Project Group by Label。

---

## 🎯 Sprint 1（W2 · 5/25-5/31）数据 + 索引 + 基础 RAG

**目标**：CLI 跑通最简单的 PDF 问答（baseline RAG）

- [ ] **[INGEST] PDF Loader 实现** — 用 PyPDFLoader，metadata 必须含 source/page
- [ ] **[INGEST] Word / HTML Loader 实现** — python-docx + bs4
- [ ] **[INGEST] 分块策略实现** — RecursiveCharacterTextSplitter，chunk_size=500/overlap=50
- [ ] **[INGEST] Embedder 封装** — bge-small-en-v1.5 / bge-m3 二选一
- [ ] **[INDEX] FAISS 索引建立 + 持久化** — `FAISS.from_documents` + `save_local`
- [ ] **[RETRIEVAL] 稠密检索接口** — `vectorstore.similarity_search(query, k=5)`
- [ ] **[SCRIPT] `ingest_pdfs.py` 批量入库脚本** — 跑通 `uv run python scripts/ingest_pdfs.py data/pdfs/`
- [ ] **[API] `/api/v1/ingest` 接口骨架** — 暂不鉴权，Sprint 4 加
- [ ] **[TEST] tests/unit/test_loaders.py** — 至少 3 个 case
- [ ] **[DOCS] benchmark.md 填 Sprint 1 baseline** — Recall@5 / 端到端延迟

---

## 🎯 Sprint 2（W3 · 6/1-6/7）混合检索 + Rerank + RAGAS

**目标**：检索质量从 Naive RAG 升级到 Advanced RAG

- [ ] **[RETRIEVAL] BM25 稀疏检索** — rank-bm25 + jieba 中文分词
- [ ] **[RETRIEVAL] RRF 混合融合** — `reciprocal_rank_fusion(dense_ranks, sparse_ranks, k=60)`
- [ ] **[RETRIEVAL] Cross-Encoder Rerank** — bge-reranker-v2-m3
- [ ] **[RETRIEVAL] HyDE 查询重写** — LLM 先写假答案再检索
- [ ] **[RETRIEVAL] Multi-Query 扩展** — 一个 query 生成 3 个改写
- [ ] **[EVAL] RAGAS 测试集准备** — 50-100 条 (question, ground_truth) pair
- [ ] **[EVAL] `run_ragas.py` 实现** — faithfulness / answer_relevancy / context_precision/recall
- [ ] **[EVAL] benchmark.md 写入对比实验结果** — Naive vs Advanced
- [ ] **[DOCS] ADR 002: 嵌入选型** + **ADR 003: 为什么 Hybrid > Dense-only**

---

## 🎯 Sprint 3（W4 · 6/8-6/14）Multi-Agent + MCP

**目标**：从单纯 RAG 升级到 Modular RAG（用 LangGraph 编排）

- [ ] **[AGENT] LangGraph 主图实现** — `src/agents/graph.py` 含 Supervisor + 3 Worker
- [ ] **[AGENT] QA Agent 实现** — 7 层 prompt + Pydantic 结构化输出
- [ ] **[AGENT] Summary Agent 实现** — 三段式摘要
- [ ] **[AGENT] Report Agent 实现** — Markdown 报告 + citation 编号
- [ ] **[AGENT] Memory Checkpointer** — `MemorySaver()` + thread_id 隔离会话
- [ ] **[GUARDRAILS] Pydantic structured_output 接入 QA Agent** — `Answer` schema
- [ ] **[GUARDRAILS] Citation 强制 + 校验** — 抽 `[来源: X, page Y]` + 校验真实指向 context
- [ ] **[MCP] Server 接 Retrieval + QA Agent** — Day6 骨架的生产版
- [ ] **[MCP] Inspector 验证 + Claude Desktop 接入测试** — 视频录屏作简历素材
- [ ] **[API] `/api/v1/query` 接通 Agent graph**
- [ ] **[DOCS] ADR 004: Milvus 索引选型** + **ADR 007: 为什么自研 MCP**

---

## 🎯 Sprint 4（W5 · 6/15-6/21）LLMOps 工程化

**目标**：把项目从"能跑"升级到"可观测、可防护、可评估"

- [ ] **[OBS] Langfuse 自托管部署** — `docker compose up langfuse langfuse-postgres`
- [ ] **[OBS] CallbackHandler 注入所有 chain 调用** — config 加全局开关
- [ ] **[OBS] trace_id 透传到 API 响应** — 前端展示"查看追踪"按钮
- [ ] **[OBS] 业务自定义指标** — 意图分布 / 引用准确率 / 用户反馈率（Prometheus）
- [ ] **[GUARDRAILS] Injection 检测加 LLM-as-judge 二级** — 关键词 + 廉价 LLM 判断
- [ ] **[GUARDRAILS] Unicode 归一化** — 防 Unicode 走私混淆
- [ ] **[GUARDRAILS] guardrails-ai 包正式装 + 接入** — Sprint 1-3 用 Pydantic 替代，此 Sprint 切真包
- [ ] **[MEMORY] PostgresSaver 替代 MemorySaver** — 复用 docker-compose 的 langfuse-postgres
- [ ] **[API] Rate Limit 中间件** — Redis-based，按 API Key 限流
- [ ] **[API] API Key 鉴权** — 简单实现，Sprint 5 视情况升级
- [ ] **[DOCS] ADR 005: 为什么 Langfuse 自托管** + **ADR 006: 为什么 DeepSeek**

---

## 🎯 Sprint 5（W6 · 6/22-6/30）上线 + Demo

**目标**：可投递的简历项目

- [ ] **[API] SSE 流式响应** — `/api/v1/query/stream` 用 `StreamingResponse`
- [ ] **[API] 反馈接口** — `/api/v1/feedback` 接 Langfuse score
- [ ] **[FRONTEND] Streamlit Demo** — 含问答 + 看 trace + 反馈
- [ ] **[INFRA] docker-compose 全套联调** — 一键 up 全部服务
- [ ] **[INFRA] 部署到云（Render / Railway / 阿里云）** — 国内访问稳定
- [ ] **[PERF] Locust 100 QPS × 5min 压测** — P95 < 3s
- [ ] **[EVAL] 跑最终 RAGAS** — 写入 README 5 项指标
- [ ] **[DOCS] README v2.0** — 含完整指标 + 部署链接 + Demo 视频 GIF
- [ ] **[DOCS] 录制 5-10 分钟 Demo 视频** — 简历附链接，bilibili 上传
- [ ] **[RESUME] 项目 1 简历段落定稿** — 含 5 个量化指标 + MCP 卖点 + LangGraph + LLMOps 三支柱

---

## 📊 Backlog（未排期，看情况捞）

- [ ] [INFRA] CI/CD GitHub Actions（PR 跑 pytest + ruff + mypy）
- [ ] [INFRA] HTTPS / Let's Encrypt
- [ ] [PERF] FAISS → Milvus standalone 切换（Sprint 3 已计划，但若 Sprint 1-2 提早遇到 FAISS 规模瓶颈可提前）
- [ ] [EVAL] 人工标注 200 条测试集（更可信）
- [ ] [FEATURE] 多模态：图表/扫描件 OCR（layoutparser + tesseract）
- [ ] [FEATURE] 知识图谱增强（neo4j + GraphRAG）
- [ ] [FEATURE] 工作流自动化（写邮件 / 建工单）
