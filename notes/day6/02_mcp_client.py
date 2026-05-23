"""Day6 上午 - Python MCP Client 测试自己写的 Server

替代 npx @modelcontextprotocol/inspector（需要 Node.js）。
用 MCP Python SDK 的 Client 直接连本地 server，遍历它暴露的 Tool/Resource/Prompt。

工作原理：
  1. 用 StdioServerParameters 描述"怎么启动 server"
  2. stdio_client 拉起 server 子进程 + 建立 stdio 连接
  3. ClientSession 提供高层 API（list_tools / call_tool / list_resources / read_resource）
  4. 整个过程异步（asyncio），因为 MCP 协议本身是 message-based

这个脚本既是测试工具，也是 Boss 项目 1 未来接 MCP 时的客户端代码模板。
"""
import asyncio
import sys

sys.stdout.reconfigure(encoding="utf-8")

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# ============== 1. 描述如何启动 Server ==============
# 这就是 Claude Desktop config 里 mcpServers 配置的程序化版本
server_params = StdioServerParameters(
    command="uv",
    args=["run", "python", "notes/day6/01_mcp_server.py"],
)


async def main():
    # ============== 2. 拉起 server 子进程 + 建立连接 ==============
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # ============== 3. 握手初始化 ==============
            await session.initialize()
            print("✅ 已连接到 MCP Server\n")

            # ============== 4. 列出 Tools ==============
            print("=" * 60)
            print("📦 Tools（LLM 可调用的函数）")
            print("=" * 60)
            tools_resp = await session.list_tools()
            for t in tools_resp.tools:
                print(f"  🔧 {t.name}")
                print(f"     描述：{t.description}")
                # input schema 可以打印查看，省略
            print()

            # ============== 5. 调用 Tools ==============
            print("=" * 60)
            print("🛠  调用 Tool")
            print("=" * 60)
            for topic in ["RAG", "MCP", "Unknown"]:
                result = await session.call_tool("search_knowledge", {"topic": topic})
                content = result.content[0].text if result.content else "(empty)"
                print(f"  search_knowledge(topic='{topic}'):")
                print(f"    → {content[:100]}...")
                print()

            arch = await session.call_tool("get_arch_diagram", {"project": "knowledge-ops"})
            print(f"  get_arch_diagram(project='knowledge-ops'):")
            print(f"    → {arch.content[0].text[:80]}...")
            print()

            # ============== 6. 列出 Resources ==============
            print("=" * 60)
            print("📚 Resources（LLM 可读取的数据）")
            print("=" * 60)
            resources_resp = await session.list_resource_templates()
            for r in resources_resp.resourceTemplates:
                print(f"  📄 {r.uriTemplate}")
                print(f"     描述：{r.description}")
            print()

            # ============== 7. 读 Resource ==============
            print("=" * 60)
            print("📖 读 Resource")
            print("=" * 60)
            note = await session.read_resource("notes://day6/RAG")
            print(f"  read_resource('notes://day6/RAG'):")
            print(f"    → {note.contents[0].text[:100]}...")
            print()

            # ============== 8. 列出 Prompts ==============
            print("=" * 60)
            print("💬 Prompts（预定义模板）")
            print("=" * 60)
            prompts_resp = await session.list_prompts()
            for p in prompts_resp.prompts:
                print(f"  📝 {p.name}")
                print(f"     描述：{p.description}")
            print()

            # ============== 9. 拉取 Prompt（含变量填充）==============
            print("=" * 60)
            print("📋 拉取 Prompt")
            print("=" * 60)
            prompt = await session.get_prompt("summarize_topic", {"topic": "MCP"})
            print(f"  get_prompt('summarize_topic', topic='MCP'):")
            for msg in prompt.messages:
                content = msg.content.text if hasattr(msg.content, "text") else str(msg.content)
                print(f"    [{msg.role}] {content[:200]}...")


if __name__ == "__main__":
    asyncio.run(main())
