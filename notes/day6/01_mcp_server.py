"""Day6 上午 - 自己的第一个 MCP Server

MCP（Model Context Protocol）= "USB-C for LLM Tools"，Anthropic 2024-2025 推出。
核心思想：把"LLM 工具调用"标准化，一份工具实现可以被所有 MCP Client 复用
（Claude Desktop / Cursor / Cline / 任意自研 Agent）。

MCP Server 暴露三类资源：
  - Tool（工具）：LLM 可调用的函数，类似 Day2 的 Function Calling 但跨厂商
  - Resource（资源）：LLM 可读取的数据（文件、笔记、数据库行）
  - Prompt（提示）：预定义的 prompt 模板

启动方式：
  uv run python notes/day6/01_mcp_server.py
  → 进入 stdio 模式，等待 Client 通过标准输入输出连接

测试方式（任选）：
  A) 同目录 02_mcp_client.py：Python 客户端直接调用（不需要 npx）
  B) npx @modelcontextprotocol/inspector ... ：浏览器 GUI（需要 Node.js）
  C) 接到 Claude Desktop（编辑 claude_desktop_config.json）
"""
from mcp.server.fastmcp import FastMCP

# ============== 1. 创建 MCP Server ==============
# 名字会显示在 Client 的工具列表里
mcp = FastMCP("knowledge-ops-demo")


# ============== 2. 暴露 Tool（LLM 可调用的函数）==============
# @mcp.tool() 装饰器自动生成 MCP schema：
#   - 函数名 → tool name
#   - docstring → tool description（LLM 看这个决定调不调）
#   - 类型注解 → parameters schema
@mcp.tool()
def search_knowledge(topic: str) -> str:
    """搜索知识库（mock 实现，未来对接真实 RAG 检索）"""
    db = {
        "RAG": "RAG 是检索增强生成：让 LLM 学会'开卷考试'，从外部知识库取材回答。",
        "Agent": "Agent 是能自主决策 + 调工具的 LLM 应用，循环 思考→行动→观察。",
        "MCP": "MCP 是 Anthropic 提出的 LLM 工具调用统一协议，被称为 'USB-C for LLM Tools'。",
        "LangGraph": "LangGraph 把 LLM 应用从'函数式管道'升级到'状态机'，支持循环/分支/HITL。",
    }
    return db.get(topic, f"暂无 {topic} 的资料。已收录主题：{list(db.keys())}")


@mcp.tool()
def get_arch_diagram(project: str) -> str:
    """获取项目架构图（返回 mermaid 文本，可贴 mermaid.live 渲染）"""
    # mock：真实场景从文件/数据库读取
    return f"""# {project} 架构（mermaid）

```mermaid
graph LR
    User --> RAGAgent
    RAGAgent --> Retriever
    RAGAgent --> LLM
    Retriever --> VectorDB
    LLM --> User
```
"""


# ============== 3. 暴露 Resource（LLM 可读取的数据）==============
# Resource 用 URI 寻址，{var} 是路径参数
# 这样 Client 可以 read_resource("notes://day6/RAG") 拿到具体笔记内容
@mcp.resource("notes://day6/{topic}")
def get_note(topic: str) -> str:
    """暴露 Day6 笔记作为 MCP Resource（按 topic 路径读取）"""
    notes_db = {
        "RAG": "Day4 笔记：RAG 七步走 + FAISS 替代 Milvus Lite 的工程教训...",
        "MCP": "Day6 笔记：MCP 是 USB-C for LLM Tools，三大概念 Tool/Resource/Prompt...",
    }
    return notes_db.get(topic, f"未找到 {topic} 的笔记")


# ============== 4. 暴露 Prompt（预定义模板）==============
# Prompt 让 Client 能复用你定义好的高质量提示词模板
# 用户在 Claude Desktop 里输入 "/summarize" 就能拉起这个 prompt
@mcp.prompt()
def summarize_topic(topic: str) -> str:
    """生成对某个技术主题的'三段式总结'提示词"""
    return f"""请用三段式总结「{topic}」：

1. 一句话核心定义（不超过 30 字）
2. 主要解决什么问题（用 if-then 句式）
3. 一个面试金句（讲给 IQ 高但没接触过的人）
"""


# ============== 5. 启动 Server ==============
if __name__ == "__main__":
    # stdio 是最简单的传输方式：通过标准输入/输出与 Client 通信
    # 其他选择：
    #   sse：Server-Sent Events（HTTP 长连接，给远程 Client 用）
    #   streamable-http：HTTP streaming（2025 主推，跨网络场景）
    mcp.run(transport="stdio")
