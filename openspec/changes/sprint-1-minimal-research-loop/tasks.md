# Sprint 1 Tasks

- [ ] [INGEST] PDF Loader 实现 — PyPDFLoader，metadata 必须含 source/page
- [ ] [INGEST] Word / HTML Loader 实现 — python-docx + bs4
- [ ] [INGEST] 分块策略实现 — RecursiveCharacterTextSplitter，chunk_size=500/overlap=50
- [ ] [INGEST] Embedder 封装 — 优先 bge-m3，保留切换配置
- [ ] [INDEX] FAISS 基线索引建立 + 持久化 — FAISS.from_documents + save_local
- [ ] [RETRIEVAL] 稠密检索接口 — vectorstore.similarity_search(query, k=5)
- [ ] [AGENT] 最小 Planner 实现 — 判断是否需要 research + 生成 2-4 个子任务
- [ ] [ARTIFACT] session artifact 目录结构 — plan/evidence/final_answer 落盘
- [ ] [PIPELINE] CLI research loop — question → plan → retrieve → synthesize → answer
- [ ] [API] /api/v1/ingest 接口骨架 — 暂不鉴权，Sprint 4 加
- [ ] [TEST] tests/unit/test_loaders.py — 至少 3 个 case
- [ ] [DOCS] benchmark.md 填 Sprint 1 baseline — dense retrieval + CLI pipeline 延迟
