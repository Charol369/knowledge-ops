# Day 7 笔记 — 5/24 周日（W1 收官战）

> **目标**：把 W1 学的所有东西用项目 1 串起来——架构图 + 目录骨架 + README + 任务看板。
> **本质**：从"学技术"到"做工程"的范式转换。

## ✅ 完成情况

- [x] 装 Sprint 1-3 生产依赖：rank-bm25 / python-docx / beautifulsoup4 / redis / ragas 0.4.3 / pydantic-settings
- [x] 装 dev 组：pytest 9.0 / pytest-asyncio / locust / ruff / mypy
- [x] 建完整目录结构：docs/{decisions} + src/{ingest,retrieval,agents,guardrails,api,mcp,observability} + eval/{reports} + tests/{unit,integration} + scripts + frontend + notes/day7
- [x] **17 个 src/* 骨架文件**全部就位（接口签名 + Sprint X 标注的 TODO），import 验证通过
- [x] **docs/architecture.md** 含 mermaid 全景架构图 + 8 模块详细说明 + 7 项关键选型理由表
- [x] **docs/decisions/001-why-langgraph.md** 第一个 ADR（含 LangGraph vs AutoGen vs CrewAI 三方对比）
- [x] **docs/api.md + benchmark.md** 占位文档
- [x] **docker-compose.yml**（Milvus standalone + Langfuse + Postgres + App 四服务）
- [x] **Dockerfile**（uv 多阶段构建，节省 50%+ 镜像体积）
- [x] **.env.example** 完整版（覆盖现有 minimal，含所有 W1 用过的环境变量 + 注释引导）
- [x] **README.md** 重写：mermaid 架构图 + 5 指标占位 + Sprint 1-5 进度表 + Quick Start + MCP 接 Claude Desktop 用法 + 完整目录树
- [x] **notes/knowledge_map.md** W1 一页纸知识地图
- [x] **notes/day7/sprint_backlog.md** 5 个 Sprint 的 issue 草稿（Boss 自己上 GitHub Project 复制建卡）
- [x] Desktop Day7 文档：一句话总结 / 验收清单 13 项 / 今日交付物全部填好打勾
- [x] commit 入库 + 打 tag `v0.0.1-w1-complete`

## 🎯 今天 AHA Moment（W1 收官 + 范式转换）

**一句话**：今天最大的认知更新是 **"从学技术 → 做工程"**。Day1-Day6 都在跑 Hello World——每天都是新概念 + 一个最小可用例子。Day7 第一次回头看，把这 22 个脚本背后的**架构思想**用 17 个 src 模块串起来。

**第二个 AHA**：写完 `docs/architecture.md` 的 mermaid 全景图后才真正"看见"项目 1。**架构图不是装饰，是认知工具**：
- 没画图前：W1 学了 6 天，知识在我脑子里是松散的"技术清单"
- 画图后：每个技术都找到了**它在系统里的位置**——`bge-m3` 是 Embedder 节点的实现选项，`langgraph` 是 Multi-Agent Layer 的编排框架，`Pydantic structured_output` 是 Guardrails 的输出约束
- **从"我学过什么"升级到"我能搭什么"**

**第三个 AHA**：W1 收集到的**3 个 LangChain 1.0 大重构信号**（Memory / Agent / Langfuse Callback）今天在写 `src/agents/memory.py` 注释时彻底清晰——**这不是 3 个独立的 deprecation，是同一个设计哲学**：
- 底层引擎归 LangGraph / OpenTelemetry（状态机 + 可观测性原生）
- 高层 API 归 langchain.agents（声明式构造器）
- 各归各位

面试金句：*"我亲眼跑过 3 个 deprecation warning，明白这是 LLM 框架成熟期的统一抽象 —— 不是单点重构，是整体范式重组。"*

**第四个 AHA**：Day7 文档里给的目录结构看起来"很复杂"（17+ 子目录），但写完发现**每个模块都直接对应 W1 学过的一个技术**：
- ingest/embedder.py = Day4 学的 bge-m3
- retrieval/hybrid.py = Day4 的 RAG + Day7 教程加的 BM25/RRF
- agents/graph.py = Day5 的 LangGraph
- mcp/server.py = Day6 的 MCP
- ...

**架构不是凭空想出来的，是"把学过的技术放到合适的位置"**。这就是工程师的核心能力。

## 🔑 核心产出

### 1. 项目 1 完整架构（10 层）

```
User → Frontend → FastAPI Gateway
       │
       ├── Guardrails（Injection / Pydantic / Citation）
       │
       ├── LangGraph Multi-Agent
       │     └── Supervisor → QA / Summary / Report Agent
       │
       ├── Retrieval（HyDE → BM25 + Dense → RRF → Rerank）
       │     └── Index（Milvus + ElasticSearch）
       │            └── Ingest（Loader / Splitter / Embedder）
       │
       └── 跨层观测：Langfuse + RAGAS + 业务指标
       │
       └── MCP Server（暴露为标准协议）
```

详见 `docs/architecture.md`。

### 2. 17 个 src 模块骨架（接口签名 + Sprint 标注）

| 模块 | 文件数 | Sprint |
|---|---|---|
| `config.py` + `main.py` | 2 | 0/已 |
| `ingest/` | 3 | 1 |
| `retrieval/` | 5 | 1+2 |
| `agents/` | 6 | 3 |
| `guardrails/` | 3 | 3+4 |
| `api/` | 2 | 3 |
| `mcp/` | 1 | 3 |
| `observability/` | 2 | 4 |

每个 .py 都含：docstring 说明 + 接口签名 + `# TODO Sprint X` 标记 + 关键设计注释。**Import 验证通过**：`from src... import *` 全过。

### 3. 完整部署 stack

- `docker-compose.yml`：Milvus standalone + Langfuse + Postgres + App
- `Dockerfile`：uv 多阶段构建
- `.env.example`：所有环境变量含注释引导

### 4. W1 收官产出

- `README.md`：mermaid 架构图 + 5 指标占位 + Sprint 进度看板（GitHub 上能直接渲染图）
- `docs/architecture.md`：8 模块详细说明 + 7 项选型理由（含跨 Day 引用工程教训）
- `docs/decisions/001-why-langgraph.md`：第一个 ADR
- `notes/knowledge_map.md`：W1 一页纸知识地图（17 技术 → 解决什么 → 项目 1 用在哪）
- `notes/day7/sprint_backlog.md`：5 Sprint × ~10 issue 草稿

## 💭 W1 全周复盘（重点）

### W1 真正的产出物（不是 22 个脚本，是这 6 件）

1. **整个 LLM 应用开发栈的"地图"**：从 API → Prompt → Chain → Graph → RAG → Multi-Agent → LLMOps → MCP，知道每一层解决什么问题（详见 knowledge_map.md）
2. **一套"用代码验证概念"的学习方式**：Day1 验证流式协议 / Day3 验证 LCEL 等价性 / Day4 验证防幻觉 / Day6 验证 Pydantic structured_output 底层 = Function Calling
3. **6 个真实工程教训**（见 knowledge_map.md "工程教训" 表）：Windows GBK 编码 / 中转站 /v1 / DeepSeek XML 泄漏 / Milvus 兼容 bug / Langfuse v4 迁移 / guardrails-ai 依赖重 —— **这些都是面试金句**
4. **项目 1 完整骨架**：架构图 + 17 模块占位 + Sprint 5 周路线图
5. **30 家目标公司清单 + 投递时间表**（target_companies.md）
6. **3 个 LangChain 1.0 大重构信号收集**（Memory / Agent / Langfuse Callback）

### W1 时间盘点

| 日 | 计划 | 实际 | 备注 |
|---|---|---|---|
| Day1 5/18 | 6h | 2h | 暖身日，建信心 |
| Day2 5/19 | 6h | 6h | Prompt 9 章 + Function Calling 闭环（信息密度最高） |
| Day3 5/20（补做） | 6h | 4h | LangChain + LangSmith |
| Day4 5/21（补做） | 7h | 4h | RAG 7 步 + Milvus→FAISS 切换决策 |
| Day5 5/22 | 6h | 3.5h | LangGraph + Multi-Agent + 求职动作 |
| Day6 5/23 | 6h | 3h | MCP + Langfuse + Guardrails，云端 Langfuse + Python MCP Client 省时 |
| Day7 5/24 | 6h | ~ | W1 收官战，大量并行写骨架 |

**总投入**：~30h（比文档预估 40h 少 10h）。**省时核心**：装包合批 + 务实选型（FAISS 替 Milvus / 云端替 Docker / Python client 替 npx Inspector）。

### W1 决策回顾（验证过的判断）

| 决策 | 结果 | 复盘 |
|---|---|---|
| 用 DeepSeek 不用 GPT-4 | ✅ 跑完一周成本 < ¥10 | 国内访问稳，OpenAI 协议兼容意味着随时可换 |
| Day3-Day4 补做 + Day5-Day7 准时 | ✅ 进度追平 | 装包合批降低重启成本 |
| FAISS 替代 Milvus Lite（Day4） | ✅ 跑通 RAG | Sprint 3 切真 Milvus（Docker），抽象层让切换零成本 |
| 云端 Langfuse 替本地 Docker（Day6） | ✅ 跑通 trace | Sprint 4 LLMOps 真正自托管 |
| Python MCP Client 替 npx Inspector（Day6） | ✅ 验证 server | 没装 Node.js 也能验证，且是 W4 客户端代码模板 |
| AI 起 target_companies 初稿（Day5） | ✅ Boss 验收过 | 公司名单需 Boss 用搜索引擎 verify 招聘状态 |
| 笔记区 AI 代写（Day3-Day7） | ✅ Boss 验收过 | 补做日时间紧时合理；常态 Boss 自己写更建立肌肉记忆 |

### W1 不该做的事 / 复盘改进

- ❌ Day4 在 langchain-milvus 0.3.3 + pymilvus 2.6 兼容 bug 上花了 30+ 分钟才决定换 FAISS。**应更早果断切换**——版本兼容是确定性失败，不是技术挑战。
- ❌ Day7 文档示例的 `pyproject.toml` 用了旧版 LangChain 0.3.x，实际装的是 1.x。**应在 Day3 装包时就发现并 surface 给 Boss**，而不是等到 Day7。

## 🎯 W1 → W2 衔接

### 周一早上不要懵的清单

打开 `knowledge-ops/`，按这个顺序：

1. **Day7 笔记复盘**（5 min）：看一遍 `notes/day7/NOTES.md`，把"今天 AHA Moment"记住
2. **`notes/day7/sprint_backlog.md`**（10 min）：把 Sprint 1 的 issues 复制到 GitHub Project（如果还没建看板）
3. **`src/ingest/loaders.py`**（开工！）：从 `load_pdf` 函数开始，用 Day4 已验证的 `PyPDFLoader`，注意 metadata 加 source + page

### Sprint 1 验收条件（W2 末 5/31）

CLI 跑通：
```powershell
uv run python scripts/ingest_pdfs.py data/pdfs/   # 入库
curl -X POST localhost:8000/api/v1/query -d '{"question": "..."}'   # 问答
```

**最简版本能跑通就行**——hybrid / rerank / Multi-Agent 都是后面 Sprint 加的。

## 🏁 W1 收官的一句话

```
W1 不是"学会了 22 个技术"——是"知道了这 22 个技术如何配合成一个生产系统"。
下周 5 个 Sprint，把架构图里的每个方块变成可工作的代码。
6/30 项目 1 成熟版交付，第一战役开打。
```

## 🔧 最后操作（Boss 验收后执行）

```powershell
# Step 1: 把 Day7 全部 commit push
git push origin main

# Step 2: 打 W1 收官 tag
git tag -a v0.0.1-w1-complete -m "W1 knowledge sprint done, project skeleton ready for Sprint 1"
git push origin v0.0.1-w1-complete

# Step 3: 上 GitHub Project 建看板（复制 notes/day7/sprint_backlog.md 里的 issue）

# Step 4: 周一早上 9:00，开工！
```
