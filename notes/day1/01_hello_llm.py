"""Day1 上午 - 第一个 LLM 调用
任务：用 OpenAI SDK 兼容协议调 DeepSeek，返回简洁回答 + 打印 Token 用量
"""
import os
import sys

# Windows 控制台默认 GBK，需强制 UTF-8 才能正常输出 emoji 和中文
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from openai import OpenAI

# 1. 加载 .env 里的环境变量
load_dotenv()

# 2. 初始化 OpenAI Client（base_url 指向 DeepSeek，因此兼容协议生效）
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)

# 3. 发起 Chat Completion 调用
response = client.chat.completions.create(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    messages=[
        {"role": "system", "content": "你是一个简洁的技术助理，每次最多用 50 字回答。"},
        {"role": "user", "content": "用一句话解释什么是 RAG。"},
    ],
)

# 4. 打印结果
print("💡 回答：")
print(response.choices[0].message.content)

print(f"\n📊 Token 用量：prompt={response.usage.prompt_tokens}, "
      f"completion={response.usage.completion_tokens}, "
      f"total={response.usage.total_tokens}")
