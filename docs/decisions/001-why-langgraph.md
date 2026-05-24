# ADR 001：为什么选 LangGraph 而不是 AutoGen / CrewAI

- **日期**：2026-05-24（W1 末）
- **状态**：Accepted
- **作者**：sundewang（项目 1 owner）

## 背景

项目 1 KnowledgeOps 需要 Multi-Agent 架构（QA / Summary / Report 三 Agent 协作）。
2026 年主流的 Agent 编排框架有三个候选：LangGraph、AutoGen（Microsoft）、CrewAI。

## 候选方案对比

| 框架 | 风格 | 优势 | 劣势 |
|---|---|---|---|
| **LangGraph** | 显式图 + State + 边 | 可控、可视化好（mermaid）、生产级、HITL 一等公民 | 写法略繁，要懂 State Schema |
| **AutoGen**（Microsoft） | 对话式 Agent | 对话流畅、agentchat 抽象高 | 调试难、状态不可见 |
| **CrewAI** | 角色扮演 | 简单易写、上手快 | 不够灵活、可控性弱 |

## 决策

**选 LangGraph**。

## 理由

1. **状态机暴露给开发者**：可以 inspect、序列化、HITL 注入、回滚到任意 checkpoint。AutoGen 把这些藏在对话抽象后面，生产环境调试难。

2. **Graph 可视化**：`app.get_graph().draw_ascii()` / `draw_mermaid()` 直接画出执行流程图（Day5 02 已验证）。CrewAI / AutoGen 没有同级别工具。

3. **HITL（Human In The Loop）一等公民**：内容审核 / 金融交易 confirm / 知识库写回 review 等生产场景必备。Chain 写不出，CrewAI 支持但不优雅，AutoGen 用对话流模拟但难控制。

4. **LangChain 1.0 大重构后官方推荐**：1.0 把 Memory（`RunnableWithMessageHistory` deprecated）和 Agent（`langgraph.prebuilt.create_react_agent` → `langchain.agents.create_agent` deprecated）都迁移到 LangGraph 体系。这意味着 LangGraph 是未来 3-5 年的 LangChain 生态首选。

5. **招聘市场最主流**：2026 年 AI 应用开发 JD 里 LangGraph 出现频率 > AutoGen > CrewAI。简历写 LangGraph 是最优解。

6. **跟 LangSmith / Langfuse 集成最深**：每个 Graph 节点都自动成为一个 trace step，可观测性原生。

## 影响

- 全项目 Multi-Agent 都用 LangGraph 实现（`src/agents/graph.py`）
- Memory 用 LangGraph Checkpointer（不用 0.x 的 RunnableWithMessageHistory）
- State Schema 用 TypedDict（W1 速成）→ Sprint 4 上 Pydantic（更严，配合配置中心）

## 后续

- 002：为什么选 bge-m3 嵌入模型？（Sprint 2 写）
- 005：为什么选 Langfuse 自托管？（Sprint 4 写）
