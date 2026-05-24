# W1 一页纸知识地图

> W1 速成周（5/18-5/24）学过的所有技术，**按"解决什么问题"组织**。
> 这是 Day7 收官产出，未来面试快速回忆用。

## 🧭 全景图

```
                            LLM 应用开发
                                 │
       ┌─────────────────────────┼─────────────────────────┐
       │                         │                         │
    底层调用                  应用框架                   生产化
   ──────────              ──────────                ──────────
    LLM API                LangChain LCEL            FastAPI
    流式输出 (SSE)         LangGraph (状态机)        Docker Compose
    Prompt 工程            LangSmith / Langfuse      Langfuse 自托管
    Function Calling       Memory (Checkpointer)     Guardrails (防护纵深)
                           Multi-Agent (Supervisor)  MCP (跨厂商标准)
                                                     RAGAS 自动评估


       │ ◄─────── 解决"模型不知道"的问题 ────────► │
       │                                            │
                            RAG
                ┌──────────┴──────────┐
              检索                   生成
            ────────              ────────
       Embedding/Vector            Prompt + LLM
       BM25 + Hybrid (RRF)        Citation (防编造来源)
       Rerank (Cross-Encoder)     Guardrails (防注入/防自由发挥)
       HyDE / Multi-Query


       │ ◄─────── 解决"模型不会做"的问题 ────────► │
                            │
                       Multi-Agent
                ┌──────────┴──────────┐
              编排                   协作
            ────────              ────────
       LangGraph                  Supervisor 模式
       ReAct (循环)               Hierarchical 模式
       Memory (Checkpointer)      Network 模式
       HITL (生产关键)


       │ ◄─────── 解决"标准化"的问题 ────────► │
                            │
                           MCP
                "USB-C for LLM Tools"
                Tool / Resource / Prompt
                跨厂商：Claude / Cursor / Cline / 自研 Agent
```

## 📋 技术 → 解决什么问题（速查表）

| 技术 | 解决什么问题 | W1 在哪天学的 | 项目 1 用在哪 |
|---|---|---|---|
| **LLM API + SSE** | "怎么调模型 + 怎么让用户感知低延迟" | Day1 | FastAPI Gateway |
| **Prompt 工程（7 层）** | "怎么让模型听话" | Day2 | 所有 Agent 的 system prompt |
| **Function Calling** | "让模型动手做事" | Day2 | Agent tools.py |
| **LangChain LCEL** | "组件化拼装代替裸调 API" | Day3 | 所有 chain（retrieval / agents） |
| **LangSmith 追踪** | "我的 Agent 在做什么" | Day3 | 开发期调试 |
| **Memory（LangGraph Checkpointer）** | "多轮对话记得前文 + 中断恢复" | Day3/Day5 | agents/memory.py |
| **RAG（embed + 检索 + 生成）** | "模型不知道公司知识库内容" | Day4 | 整个 retrieval + qa_agent |
| **分块策略 + 嵌入选型** | "怎么切文档 + 用什么向量化" | Day4 | ingest/{splitters,embedder}.py |
| **FAISS / Milvus** | "向量库怎么选" | Day4 / Day7 | retrieval/dense.py |
| **LangGraph（Chain → 状态机）** | "Agent 需要循环 + 分支 + HITL" | Day5 | agents/graph.py |
| **ReAct + Multi-Agent** | "复杂任务拆解 + 多角色协作" | Day5 | Supervisor + QA/Summary/Report |
| **MCP 协议** | "工具跨厂商复用" | Day6 | src/mcp/server.py |
| **Langfuse 追踪** | "自托管的 LLM Observability" | Day6 | observability/langfuse_setup.py |
| **Pydantic structured_output** | "强制结构化输出（防自由发挥）" | Day6 | guardrails/output_schema.py |
| **Prompt Injection 防护** | "防止用户搞坏我的系统" | Day6 | guardrails/injection.py |
| **RAG 三阶段演进** | "Naive → Advanced → Modular 的升级路径" | Day4 | 项目 1 Sprint 1→2→3→4 推进 |
| **LLMOps 三支柱** | "追踪 + 评估 + 防护" | Day6 | observability + eval + guardrails |

## 🎯 一句话总结这周学到了什么

```
从"知道 LLM 能做什么" 升级到 "知道怎么把 LLM 包装成生产可用的系统"。

具体讲：
  · 调通（LLM API + 流式）
  · 用好（Prompt + Function Calling）
  · 抽象（LangChain LCEL → LangGraph 状态机）
  · 扩展（RAG 解决知识 + Multi-Agent 解决任务）
  · 生产（Langfuse 追踪 + RAGAS 评估 + Guardrails 防护）
  · 标准化（MCP 跨 Client 复用）

下周 Sprint 1 开始把架构图里的每个方块变成可工作的代码。
```

## ⚠️ W1 收集到的 LangChain 1.0 大重构信号（面试金句库）

| 信号 | 0.x | 1.0+ 新位置 |
|---|---|---|
| **Memory** | `RunnableWithMessageHistory` | `langgraph.checkpoint.MemorySaver` |
| **Agent** | `langgraph.prebuilt.create_react_agent` | `langchain.agents.create_agent` |
| **Langfuse Callback** | `langfuse.callback.CallbackHandler`（v2/v3） | `langfuse.langchain.CallbackHandler`（v4，无参 + OpenTelemetry） |

**金句**：*"2025-2026 是 LLM 框架成熟期的重组之年——底层引擎归 OpenTelemetry / LangGraph，高层 API 归 langchain.agents，各归各位。"*

## 🛠 W1 真实工程教训（面试谈资）

| Day | 教训 | 演化决策 |
|---|---|---|
| Day1 | Windows GBK 控制台编码踩坑 | `sys.stdout.reconfigure(encoding="utf-8")` 全脚本统一 |
| Day1 | 中转站 base_url 必须带 `/v1` | 全项目用 `os.getenv("DEEPSEEK_BASE_URL")`，不硬编码 |
| Day2 | DeepSeek 工具调用 XML 标签泄漏 | calculator 用 try/except 包 eval，未来生产层加正则清洗 |
| Day4 | langchain-milvus 0.3.3 + pymilvus 2.6 milvus-lite 兼容 bug | 务实切 FAISS，W1 速成不陷在版本兼容里；Sprint 3 切真 Milvus standalone |
| Day6 | Langfuse v3→v4 API 大迁移 | 脚本按 4.6 真实 API 写（langfuse.langchain + 无参构造） |
| Day6 | guardrails-ai 依赖重 + 国内慢 | Pydantic structured_output + 手写 injection 检测已足够，Sprint 4 真用时再装 |

**金句**：*"我评估过 X 方案的 Y bug，所以选了 Z，这是工程师做技术选型的真实流程"*——比"我用了 LangChain"权重高 10 倍。
