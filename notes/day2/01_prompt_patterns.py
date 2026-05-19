"""Day2 上午 - 4 种 Prompt 套路对比

通过同一个问题，对比 Zero-shot / CoT / System Prompt / Few-shot 的效果。
这是 Anthropic Prompt Tutorial 章节的浓缩实战版。
"""
import os
import sys

# Day1 踩坑教训：Windows 控制台 GBK，强制 UTF-8 才能输出 emoji
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


def ask(messages, label):
    """统一调用 + 打印"""
    print(f"\n{'=' * 20} {label} {'=' * 20}")
    resp = client.chat.completions.create(model=MODEL, messages=messages)
    print(resp.choices[0].message.content)


QUESTION = "如果 A 比 B 高 10 cm，B 比 C 高 5 cm，C 是 170 cm，A 是多高？"


# 套路 1：Zero-shot（直接问，不给任何引导）
ask(
    [{"role": "user", "content": QUESTION}],
    label="1. Zero-shot 裸问",
)

# 套路 2：CoT（思维链）—— 让 LLM 把推理过程写出来
ask(
    [{"role": "user", "content": QUESTION + "\n请一步一步推理，最后给出答案。"}],
    label="2. CoT 思维链",
)

# 套路 3：System Prompt 角色化 —— 给 LLM 一个身份和回答风格
ask(
    [
        {"role": "system", "content": "你是一名严谨的数学老师，回答时先列方程，再求解。"},
        {"role": "user", "content": QUESTION},
    ],
    label="3. System Prompt 角色化",
)

# 套路 4：Few-shot（示例引导）—— 给两个示例，让 LLM 学会输出格式
ask(
    [
        {"role": "user", "content": "示例 1：X 比 Y 高 3 cm，Y 是 160 cm，X 是多高？"},
        {"role": "assistant", "content": "Y = 160 cm，X = Y + 3 = 163 cm。答案：163 cm。"},
        {"role": "user", "content": "示例 2：M 比 N 高 7 cm，N 是 175 cm，M 是多高？"},
        {"role": "assistant", "content": "N = 175 cm，M = N + 7 = 182 cm。答案：182 cm。"},
        {"role": "user", "content": QUESTION},
    ],
    label="4. Few-shot 示例引导",
)

print("\n" + "=" * 60)
print("💡 观察重点：套路 2/3/4 的回答比 1 更稳定、格式更整齐")
print("=" * 60)
