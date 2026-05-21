"""Day3 下午 - LangSmith 追踪

目标：让每次 LLM 调用自动上报 LangSmith，在 dashboard 看到：
  - 完整的 prompt + LLM 响应
  - Token 数 + 成本 + 延迟
  - 整个 Chain 的执行树（哪一步最慢/最贵）

工作机制：
  - LangChain 在 LCEL chain 的每个节点都装了 callback handler
  - 只要环境变量 LANGSMITH_TRACING=true 且 LANGSMITH_API_KEY 已配，
    每次 invoke 自动 POST 到 LangSmith
  - 完全无侵入：业务代码不用改一行

⚠️ 关键约定：load_dotenv() 必须在 import langchain_* 之前调用，
   否则 LangChain 启动时读不到 LANGSMITH_* 环境变量，追踪不会打开。
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

# ⚠️ 注意：先 load_dotenv()，再 import langchain_*
load_dotenv()


# ============== 0. 启动前检查 LangSmith 配置 ==============
TRACING = os.getenv("LANGSMITH_TRACING", "").lower() == "true"
HAS_KEY = bool(os.getenv("LANGSMITH_API_KEY"))
PROJECT = os.getenv("LANGSMITH_PROJECT", "default")

if TRACING and HAS_KEY:
    print(f"✅ LangSmith 追踪已开启，项目：{PROJECT}")
    print(f"   dashboard: https://smith.langchain.com/o/-/projects/p/{PROJECT}")
elif HAS_KEY and not TRACING:
    print("⚠️  LANGSMITH_API_KEY 已配，但 LANGSMITH_TRACING=false。")
    print("    把 .env 里 LANGSMITH_TRACING 改成 true 即可开启追踪。")
else:
    print("⚠️  LangSmith 未启用（缺 API_KEY 或 TRACING=false）。")
    print("    本次只会跑 Chain 验证逻辑，但不会在 LangSmith 看到 trace。")
    print()
    print("    👉 拿 LangSmith key 步骤：")
    print("       1. 打开 https://smith.langchain.com")
    print("       2. 注册/登录 → 右上角头像 → Settings → API Keys")
    print("       3. Create API Key（lsv2_pt_xxx）→ 复制")
    print("       4. 填进 .env 的 LANGSMITH_API_KEY")
    print("       5. 把 .env 的 LANGSMITH_TRACING 改成 true")
    print("       6. 重跑这个脚本")

print()


# ============== 1. 业务代码（和 01_chain_basic.py 几乎一样）==============
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一名旅游顾问。回答简洁，每个景点一行。"),
    ("user", "推荐 3 个适合 {season} 的 {country} 旅游景点。"),
])

chain = prompt | llm | StrOutputParser()


# ============== 2. 调用 Chain（如果追踪开启，这一步会上报 LangSmith）==============
inputs = {"season": "春天", "country": "日本"}
print(f"👤 输入：{inputs}\n")

result = chain.invoke(inputs)
print("💡 回答：")
print(result)


# ============== 3. 提示 Boss 去看 dashboard ==============
print()
if TRACING and HAS_KEY:
    print("=" * 60)
    print("✅ 已上报 LangSmith。现在去 dashboard 看 trace：")
    print(f"   https://smith.langchain.com/o/-/projects/p/{PROJECT}")
    print()
    print("   在最新一条 trace 上能看到：")
    print("   - ChatPromptTemplate 节点：渲染后的 messages")
    print("   - ChatOpenAI 节点：完整 request/response + token 数 + 延迟")
    print("   - StrOutputParser 节点：最终字符串输出")
    print("=" * 60)
else:
    print("（跳过 LangSmith 部分。完成上面的配置步骤后重跑即可看到 trace。）")
