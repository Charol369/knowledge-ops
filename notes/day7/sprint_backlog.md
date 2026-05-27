# Sprint Backlog · GitHub Project 看板源

> 这不是“学完后补工程化”的待办，而是**从第一天就按生产导向研究型 Agent 系统**拆出来的执行清单。
> Boss 到 GitHub 仓库 → `Projects` → 新建 Board → 5 列 + Backlog/Done，把下面每条复制成一个 Issue。
>
> Issue title 风格：`[模块] 动作`。

---

## 🎯 Sprint 1（W2 · 5/25-5/31）最小研究闭环 + 证据管线

**目标**：跑通最小 research pipeline，而不是只做 baseline RAG

- [ ] **[INGEST] PDF Loader 实现** — PyPDFLoader，metadata 必须含 source/page
- [ ] **[INGEST] Word / HTML Loader 实现** — python-docx + bs4
- [ ] **[INGEST] 分块策略实现** — RecursiveCharacterTextSplitter，chunk_size=500/overlap=50
- [ ] **[INGEST] Embedder 封装** — 优先 bge-m3，保留切换配置
- [ ] **[INDEX] FAISS 基线索引建立 + 持久化** — `FAISS.from_documents` + `save_local`
- [ ] **[RETRIEVAL] 稠密检索接口** — `vectorstore.similarity_search(query, k=5)`
- [ ] **[AGENT] 最小 Planner 实现** — 判断是否需要 research + 生成 2-4 个子任务
- [ ] **[ARTIFACT] session artifact 目录结构** — `plan/evidence/final_answer` 落盘
- [ ] **[PIPELINE] CLI research loop** — `question → plan → retrieve → synthesize → answer`
- [ ] **[API] `/api/v1/ingest` 接口骨架** — 暂不鉴权，Sprint 4 加
- [ ] **[TEST] tests/unit/test_loaders.py** — 至少 3 个 case
- [ ] **[DOCS] benchmark.md 填 Sprint 1 baseline** — dense retrieval + CLI pipeline 延迟

---

## 🎯 Sprint 2（W3 · 6/1-6/7）混合检索 + 上下文工程

**目标**：检索质量从 Naive RAG 升级到 Advanced RAG，同时建立 context builder

- [ ] **[RETRIEVAL] BM25 稀疏检索** — rank-bm25 + jieba 中文分词
- [ ] **[RETRIEVAL] RRF 混合融合** — `reciprocal_rank_fusion(...)`
- [ ] **[RETRIEVAL] Cross-Encoder Rerank** — bge-reranker-v2-m3
- [ ] **[RETRIEVAL] HyDE 查询重写** — LLM 先写假答案再检索
- [ ] **[RETRIEVAL] Multi-Query 扩展** — 一个 query 生成 3 个改写
- [ ] **[RETRIEVAL] Query Decomposition** — 多跳问题拆子问题分别检索
- [ ] **[CONTEXT] Context Builder 实现** — system/project/task/evidence/focus recap 分层
- [ ] **[CONTEXT] Artifact-to-context 取回策略** — 中间产物按需回灌，而非全文塞 prompt
- [ ] **[EVAL] RAGAS 测试集准备** — 50-100 条 (question, ground_truth) pair
- [ ] **[EVAL] `run_ragas.py` 实现** — faithfulness / answer_relevancy / context_precision/recall
- [ ] **[DOCS] ADR 002: 嵌入选型** + **ADR 003: 为什么 Hybrid > Dense-only**

---

## 🎯 Sprint 3（W4 · 6/8-6/14）混合范式 Agent 图 + MCP 工具层

**目标**：从“检索系统”升级到“研究型 Agent 系统”

- [ ] **[AGENT] LangGraph 主图重构** — 从 Supervisor 三分法升级为 Planner / Orchestrator / Synthesizer / Reporter / Verifier
- [ ] **[AGENT] Planner Node 实现** — Plan-and-Solve 主线
- [ ] **[AGENT] Retrieval Orchestrator 实现** — 局部 ReAct，必要时重检索 / 改写 query
- [ ] **[AGENT] Synthesizer 实现** — 子任务证据归纳，不直接写华丽答案
- [ ] **[AGENT] Reporter 实现** — Markdown 报告 + citation 编号
- [ ] **[AGENT] Verifier / Reflection 实现** — 复杂场景选择性启用，不全量触发
- [ ] **[AGENT] Memory Checkpointer** — `MemorySaver()` + thread_id 隔离会话
- [ ] **[GUARDRAILS] Pydantic structured_output 接入** — `Answer` / `Report` schema
- [ ] **[GUARDRAILS] Citation 强制 + 校验** — 抽 `[来源: X, page Y]` + 校验真实指向 context
- [ ] **[MCP] Server 接 Retrieval Services + Synthesizer** — 作为标准化工具层，而不是 A2A 替代物
- [ ] **[MCP] Claude Desktop 接入测试** — 视频录屏作简历素材
- [ ] **[API] `/api/v1/query` 接通 Agent graph**
- [ ] **[DOCS] ADR 004: Milvus 索引选型** + **ADR 007: 为什么自研 MCP**

---

## 🎯 Sprint 4（W5 · 6/15-6/21）Policy Layer + LLMOps

**目标**：把项目从“能跑”升级到“有生产者视角”

- [ ] **[POLICY] Complexity Classifier** — 区分 FAQ / 普通问答 / 复杂研究 / 高风险报告
- [ ] **[POLICY] Model Router** — 简单任务走廉价模型，复杂任务升级高阶模型
- [ ] **[POLICY] Cache / Retry / Fallback 策略** — Redis 缓存 + 模型降级 + 工具失败回退
- [ ] **[OBS] Langfuse 自托管部署** — `docker compose up langfuse langfuse-postgres`
- [ ] **[OBS] CallbackHandler 注入 graph / retrieval / policy 决策**
- [ ] **[OBS] trace_id 透传到 API 响应** — 前端展示“查看追踪”按钮
- [ ] **[OBS] 业务指标** — 延迟 / token 成本 / 工具成功率 / fallback rate / citation hit rate
- [ ] **[GUARDRAILS] Injection 检测二级化** — 关键词 + 廉价 LLM 判断
- [ ] **[GUARDRAILS] Unicode 归一化** — 防 Unicode 混淆
- [ ] **[MEMORY] PostgresSaver 替代 MemorySaver** — 需要时持久化
- [ ] **[API] Rate Limit 中间件** — Redis-based，按 API Key 限流
- [ ] **[API] API Key 鉴权** — 简单实现，Sprint 5 视情况升级
- [ ] **[DOCS] ADR 005: 为什么 Langfuse 自托管** + **ADR 006: 为什么采用模型路由而不是单模型硬打**

---

## 🎯 Sprint 5（W6 · 6/22-6/30）研究助手 Demo + 上线

**目标**：把项目打磨成真正可投递的作品

- [ ] **[API] SSE 流式响应** — `/api/v1/query/stream`
- [ ] **[API] 反馈接口** — `/api/v1/feedback` 接 Langfuse score
- [ ] **[FRONTEND] Streamlit Demo** — 不只是聊天框，要展示 plan / progress / evidence / final report
- [ ] **[INFRA] docker-compose 全套联调** — 一键 up 全部服务
- [ ] **[INFRA] 部署到云（Render / Railway / 阿里云）** — 国内访问稳定
- [ ] **[PERF] Locust 100 QPS × 5min 压测** — P95 < 3s
- [ ] **[EVAL] 最终评估** — 不只 RAGAS，还要统计 workflow / tool / cost 指标
- [ ] **[DOCS] README v2.0** — 含项目定位、架构、模型路由、成本策略、部署链接、Demo 视频 GIF
- [ ] **[DOCS] 录制 5-10 分钟 Demo 视频** — 简历附链接，bilibili 上传
- [ ] **[RESUME] 项目 1 简历段落定稿** — 含“非全量 agent 化”“token 套利”“研究型 Agent”三大亮点

---

## 📊 Backlog（未排期，看情况捞）

- [ ] [INFRA] CI/CD GitHub Actions（PR 跑 pytest + ruff + mypy）
- [ ] [INFRA] HTTPS / Let's Encrypt
- [ ] [PERF] FAISS → Milvus standalone 切换（若 Sprint 1-2 提前遇到规模瓶颈可前移）
- [ ] [EVAL] 人工标注 200 条测试集（更可信）
- [ ] [FEATURE] 多模态：图表/扫描件 OCR（layoutparser + tesseract）
- [ ] [FEATURE] 知识图谱增强（neo4j + GraphRAG）
- [ ] [FEATURE] 工作流自动化（写邮件 / 建工单）

---

## 🎤 项目 1 面试话术钩子（写在这里，避免后面忘）

- **不是所有东西都该 agent 化。**
- **认知链路 agent 化，执行链路服务化。**
- **简单任务走简单模型，复杂任务才上高级模型。**
- **项目从第一天就把成本、部署、观测、评估写进架构，而不是最后补。**
- **KnowledgeOps 的本质是研究型 Knowledge Agent，而不是普通 RAG 聊天机器人。**

---

## 🧱 对应代码层应该逐步出现的核心对象

- `Planner`
- `RetrievalOrchestrator`
- `Synthesizer`
- `Reporter`
- `Verifier`
- `ContextBuilder`
- `ArtifactStore`
- `ComplexityClassifier`
- `ModelRouter`
- `FallbackPolicy`

这些对象是否显式存在，将决定项目后续是否真的做到“原生生产导向”。

## 📊 Backlog（未排期，看情况捞）

- [ ] [INFRA] CI/CD GitHub Actions（PR 跑 pytest + ruff + mypy）
- [ ] [INFRA] HTTPS / Let's Encrypt
- [ ] [PERF] FAISS → Milvus standalone 切换（Sprint 3 已计划，但若 Sprint 1-2 提早遇到 FAISS 规模瓶颈可提前）
- [ ] [EVAL] 人工标注 200 条测试集（更可信）
- [ ] [FEATURE] 多模态：图表/扫描件 OCR（layoutparser + tesseract）
- [ ] [FEATURE] 知识图谱增强（neo4j + GraphRAG）
- [ ] [FEATURE] 工作流自动化（写邮件 / 建工单）
