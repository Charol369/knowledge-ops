"""MCP Server：把 KnowledgeOps 的能力暴露为 MCP 标准协议。

MCP 在本项目里的定位是工具标准化层：
- 暴露 retrieval / summarize / artifact metadata 能力
- 供 Claude Desktop / Cursor / Cline 复用
- 不承担 A2A / ANP 级别的网络复杂度
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("knowledge-ops")


@mcp.tool()
def search_knowledge(query: str, top_k: int = 5) -> str:
    """检索企业知识库，返回 Top-K 相关 evidence（Markdown 格式）。"""
    # TODO Sprint 3: 接 retrieval services，而不是让 MCP 直接依赖某个具体 Agent
    raise NotImplementedError


@mcp.tool()
def summarize_documents(query: str) -> str:
    """对检索结果做结构化总结。"""
    # TODO Sprint 3: 接 synthesizer / reporter 的轻量能力
    raise NotImplementedError


@mcp.resource("knowledge://collections/{name}")
def get_collection_info(name: str) -> str:
    """暴露 collection 元信息作为 MCP Resource。"""
    # TODO Sprint 3: 返回文档数 / 大小 / 最后更新时间
    raise NotImplementedError


@mcp.resource("knowledge://sessions/{session_id}")
def get_session_artifact(session_id: str) -> str:
    """暴露研究中间产物（plan / evidence / final report）元信息。"""
    # TODO Sprint 3: 接 ArtifactStore
    raise NotImplementedError


if __name__ == "__main__":
    mcp.run(transport="stdio")
