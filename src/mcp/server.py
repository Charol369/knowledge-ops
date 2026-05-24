"""MCP Server：把 KnowledgeOps 的检索能力暴露为 MCP 标准协议

让 Claude Desktop / Cursor / Cline 等 MCP Client 能直接调用我们的 RAG，
这是项目 1 的**简历核心卖点**——"自研 MCP Server，跨 Client 复用"。

Day6 01_mcp_server.py 已经做过演示骨架，这里是生产版骨架。

启动：uv run python -m src.mcp.server
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("knowledge-ops")


@mcp.tool()
def search_knowledge(query: str, top_k: int = 5) -> str:
    """检索企业知识库，返回 Top-K 相关 chunks（Markdown 格式）"""
    # TODO Sprint 3: 接 src.retrieval.hybrid + src.agents.qa_agent
    raise NotImplementedError


@mcp.tool()
def summarize_documents(query: str) -> str:
    """对检索结果做结构化总结"""
    # TODO Sprint 3
    raise NotImplementedError


@mcp.resource("knowledge://collections/{name}")
def get_collection_info(name: str) -> str:
    """暴露 collection 元信息作为 MCP Resource"""
    # TODO Sprint 3: 返回该 collection 的文档数 / 大小 / 最后更新时间
    raise NotImplementedError


if __name__ == "__main__":
    mcp.run(transport="stdio")
