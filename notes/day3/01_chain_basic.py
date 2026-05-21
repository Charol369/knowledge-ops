"""Day3 上午 - LangChain Chain 基础（LCEL 三件套）

目标：从 Day1/Day2 "裸调 OpenAI SDK" 升级到 LangChain "组件化拼装"。
核心概念：
  - LCEL（LangChain Expression Language）用 `|` 把组件串成 pipeline
  - 三件套：Prompt 模板 → LLM 调用 → Output Parser

DeepSeek 接入要点：DeepSeek 兼容 OpenAI 协议，所以用 ChatOpenAI + base_url 即可。
"""
import os
import sys

# Windows 控制台默认 GBK，强制 UTF-8 才能正常打印中文和 emoji
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()


# ============== 1. LLM：用 ChatOpenAI 接 DeepSeek ==============
# 关键参数：base_url（指向 DeepSeek 兼容端点）+ api_key + model
# temperature=0.7 适合"有点创造性、但不离谱"的回答（0 = 完全确定性，1 = 高随机）
llm = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
    temperature=0.7,
)


# ============== 2. Prompt 模板（带占位变量）==============
# from_messages 支持的角色：system / user / human / assistant / ai / tool / placeholder
# 变量用 {var} 占位，invoke 时传 dict 填进去
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一名 {role}，请用 {style} 的风格回答。"),
    ("user", "{question}"),
])


# ============== 3. Output Parser：把 AIMessage 转成纯字符串 ==============
# llm 默认返回 AIMessage 对象（带 .content / .response_metadata / .usage_metadata 等字段）
# StrOutputParser 只取 .content，方便 print 和后续传递
parser = StrOutputParser()


# ============== 4. LCEL：用 | 把三个组件串成 Chain ==============
# chain = prompt | llm | parser
# 等价于：parser.invoke(llm.invoke(prompt.invoke(input)))
# 即每个组件的 .invoke() 输出当作下一个组件的输入，类似 Unix 管道
chain = prompt | llm | parser


# ============== 5. 调用 Chain ==============
inputs = {
    "role": "高中物理老师",
    "style": "通俗易懂、举生活例子",
    "question": "什么是相对论？",
}

print("👤 输入：", inputs)
print("\n💡 Chain 输出：")
result = chain.invoke(inputs)
print(result)


# ============== 6. [DEBUG] 验证 LCEL 的 | 等价于手动嵌套调用 ==============
# 这段证明验收清单第 1 题：LCEL 的 | 操作符等价于什么 Python 函数调用？
print("\n" + "=" * 60)
print("[DEBUG] 验证 chain.invoke 等价于 parser(llm(prompt(input)))")
print("=" * 60)

# 手动按 pipeline 顺序逐步调用
step1_prompt_value = prompt.invoke(inputs)   # ChatPromptValue（含格式化后的 messages）
step2_llm_msg = llm.invoke(step1_prompt_value)  # AIMessage
step3_parsed = parser.invoke(step2_llm_msg)     # str

print(f"step1 prompt.invoke → {type(step1_prompt_value).__name__}")
print(f"step2 llm.invoke    → {type(step2_llm_msg).__name__}")
print(f"step3 parser.invoke → {type(step3_parsed).__name__}")
print(f"\n手动调用与 chain.invoke 结果是否一致：{step3_parsed[:30] == result[:30]}")
print("（受 temperature=0.7 影响，两次调用 LLM 文本可能不同，只比前 30 字符判断结构等价）")
