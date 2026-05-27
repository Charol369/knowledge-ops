# ADR 007：为什么采用 MCP 工具层

- **日期**：2026-05-28
- **状态**：Accepted
- **作者**：sundewang（项目 1 owner）

## 背景

KnowledgeOps 的能力不应只暴露给一个 FastAPI 入口。
企业知识场景常见调用方包括 Claude Desktop、Cursor、Cline 和其他本地 Agent 客户端。
Sprint 3 需要提供一个标准化工具边界，让外部客户端可以复用检索、摘要和 artifact metadata 能力。

## 候选方案对比

| 方案 | 优势 | 劣势 |
|---|---|---|
| 只提供 REST API | 通用、易测试 | LLM 客户端工具发现和调用协议不统一 |
| 自定义 function calling schema | 可控、实现简单 | 绑定单个客户端或模型供应商，复用性弱 |
| MCP Server | 工具/资源协议标准化，Claude Desktop/Cursor/Cline 可复用 | 客户端 GUI 配置需要人工边界，stdio server 不能作为无界 smoke 测试 |
| A2A/ANP 级网络协议 | 适合复杂多 Agent 网络 | 对 Sprint 3 过重，偏离本地可测目标 |

## 决策

Sprint 3 采用 MCP Server 作为工具标准化层。
MCP 工具只暴露本地 retrieval/synthesis/artifact metadata 能力，不承担生产鉴权、限流、观测或跨服务网络职责。

## 理由

1. **工具边界清晰**：`search_knowledge` 调本地 Retrieval Orchestrator，`summarize_documents` 调 Synthesizer/Reporter，resources 暴露 collection/session metadata。

2. **复用 deterministic services**：MCP 不直接编造答案，也不绕过 retrieval/context；它只是把已有 KnowledgeOps 能力包装成标准工具接口。

3. **local-first 可测试**：工具函数保持普通 Python 可调用能力，测试可以直接验证本地 docs fixture、index fixture 和 artifact fixture，不需要 Claude Desktop GUI。

4. **手动边界明确**：Claude Desktop 配置属于用户本机客户端操作，Sprint 3 不声称端到端 GUI 集成已自动完成；只提供本地 import/tool 行为验证。

5. **不引入 Sprint 4-5 能力**：MCP 层不实现 auth、rate limit、Langfuse、SSE、Streamlit demo、cloud deployment 或最终 benchmark claims。

## 影响

- `src/mcp/server.py` 暴露 `search_knowledge`、`summarize_documents`、`knowledge://collections/{name}` 和 `knowledge://sessions/{session_id}`。
- Resource 装饰函数保持 MCP URI 参数兼容；本地测试通过 helper 函数注入 fixture 路径。
- MCP smoke 只运行 import-level 检查，不启动无界 stdio server。

## 后续

- 真实 Claude Desktop 集成需要用户在本机 MCP client 配置中指向 `uv run python -m src.mcp.server`。
- Sprint 4/5 如需生产化 MCP，可以在不改变工具语义的前提下加入安全、观测和部署边界。
