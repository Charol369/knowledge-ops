"""Day6 下午 - Langfuse 监控 LangChain（LLMOps 的"追踪"支柱）

⚠️ Langfuse 4.6 跟 Day6 文档示例（基于 v2/v3）的 API 完全不同：
  - 文档示例：`from langfuse.callback import CallbackHandler`，构造时传 key/host
  - 实际 4.6：`from langfuse.langchain import CallbackHandler`，**构造无参**，自动读环境变量

这是 Langfuse v3→v4 OpenTelemetry 重构。跟 LangChain 1.0 + LangGraph 1.x
是同一波 2025-2026 LLM 框架成熟期的大版本迁移。

LangSmith vs Langfuse 对比（**面试必背**）：
  - LangSmith：LangChain 官方，闭源，云端 SaaS，免费层 5k traces/月
  - Langfuse：开源（MIT），可云端可自托管，企业内网部署友好

W1 速成期：用云端 Langfuse（cloud.langfuse.com 免费层），零 Docker 配置。
W4 项目期 LLMOps：自托管 Docker 版（Langfuse OSS）走完整 LLMOps 流程。
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()


# ============== 0. 启动前检查 Langfuse 配置 ==============
PUBLIC = os.getenv("LANGFUSE_PUBLIC_KEY", "").strip()
SECRET = os.getenv("LANGFUSE_SECRET_KEY", "").strip()
HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com").strip()
HAS_LF = bool(PUBLIC and SECRET)

if HAS_LF:
    print(f"✅ Langfuse 已配置，HOST = {HOST}")
else:
    print("⚠️  Langfuse 未配置（缺 PUBLIC_KEY / SECRET_KEY），将跑 Chain 但不追踪。")
    print()
    print("    👉 拿 Langfuse key 步骤：")
    print("       1. 打开 https://cloud.langfuse.com（免费层）")
    print("       2. 注册/登录 → New Project 'knowledge-ops'")
    print("       3. Settings → API Keys → Create new API key")
    print("       4. 复制 PUBLIC_KEY (pk-lf-xxx) 和 SECRET_KEY (sk-lf-xxx)")
    print("       5. 填进 .env 的 LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY")
    print("       6. 重跑这个脚本")
print()


# ============== 1. 业务代码（标准 LangChain 用法）==============
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个简洁的技术讲解员，每次回答 100 字以内。"),
    ("user", "{question}"),
])

chain = prompt | llm | StrOutputParser()


# ============== 2. Langfuse 4.6 CallbackHandler ==============
# v4 改成无参构造，自动读 LANGFUSE_* 环境变量（OpenTelemetry 风格）
callbacks = []
if HAS_LF:
    from langfuse.langchain import CallbackHandler
    callbacks.append(CallbackHandler())


# ============== 3. 调用 Chain（挂上 Langfuse callback）==============
inputs = {"question": "什么是 RAG？为什么需要它？"}
print(f"👤 输入：{inputs}\n")

result = chain.invoke(inputs, config={"callbacks": callbacks})
print("💡 回答：")
print(result)


# ============== 4. 提示去 dashboard 看 trace ==============
print()
if HAS_LF:
    # Langfuse 4 是异步上报，跑完立刻退出可能丢 trace，建议显式 flush
    if callbacks:
        from langfuse import get_client
        try:
            get_client().flush()
            print("✅ 已 flush trace 到 Langfuse")
        except Exception as e:
            print(f"⚠️  flush 异常（不影响主流程）：{e}")

    print(f"\n→ 打开 {HOST} 查看 trace")
    print("→ 在 knowledge-ops 项目下应该能看到这一次调用")
    print("  能看到：完整 prompt + 回答 + token + latency + chain 执行树")
else:
    print("（跳过 Langfuse 部分。完成上面的配置步骤后重跑即可看到 trace。）")
