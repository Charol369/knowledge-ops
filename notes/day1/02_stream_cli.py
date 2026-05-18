"""Day1 下午 - 流式输出 CLI 版
任务：让 LLM 一边生成一边输出，像 ChatGPT 那样字符逐个冒出
"""
import os
import sys

# Windows 控制台默认 GBK，需强制 UTF-8 才能正常输出 emoji 和中文
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)

# 关键：stream=True，返回的是迭代器而非完整对象
stream = client.chat.completions.create(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    messages=[
        {"role": "user", "content": "写一首关于程序员的 7 言绝句，每句之后换行。"},
    ],
    stream=True,
)

# 逐 chunk 拼接 + 实时打印
print("✨ 流式输出：\n")
for chunk in stream:
    # 流式最后一个 chunk 可能 choices=[]（只带 usage），需防御
    if not chunk.choices:
        continue
    delta = chunk.choices[0].delta.content
    if delta:
        # flush=True：让字符立刻显示，不等缓冲区
        print(delta, end="", flush=True)
print("\n")  # 收尾换行
