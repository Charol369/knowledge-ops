"""Day2 下午 - Function Calling 单工具：计算器

让 LLM 学会"动嘴 + 动手"：
- 用户提问 → LLM 判断要不要调工具 → 调用 → 获取结果 → LLM 综合回答
"""
import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


# ============== 1. 工具的"使用说明书"（给 LLM 看的 JSON Schema）==============
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "进行四则运算，支持加减乘除。当问题涉及精确数值计算时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，例如 '3 + 5 * 2' 或 '(123 + 456) * 2'",
                    }
                },
                "required": ["expression"],
            },
        },
    }
]


# ============== 2. 工具的真实实现（给 Python 跑的）==============
def calculator(expression: str) -> str:
    """安全的 eval（限制 builtins）"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"计算失败：{e}"


# ============== 3. 主循环：让 LLM 决定何时调用工具 ==============
def chat_with_tools(user_question: str):
    print(f"\n👤 用户：{user_question}\n")
    messages = [{"role": "user", "content": user_question}]

    round_idx = 0
    while True:
        round_idx += 1
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
        )
        msg = resp.choices[0].message

        # [DEBUG] 验证笔记卡壳问题：tool_calls 不调工具时是 None 还是 []？
        print(f"[DEBUG Round {round_idx}] tool_calls type={type(msg.tool_calls).__name__} value={msg.tool_calls!r}")

        # 退出条件：LLM 不再调用工具，直接回答
        if not msg.tool_calls:
            print(f"🤖 最终回答：{msg.content}")
            print(f"[DEBUG] 累计 messages={len(messages)} 条，共 {round_idx} 轮 LLM 调用\n")
            return

        # LLM 要求调用工具
        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            print(f"🔧 工具调用：{call.function.name}({args})")
            result = calculator(**args)
            print(f"📤 工具返回：{result}")
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })


if __name__ == "__main__":
    chat_with_tools("帮我算一下 (123 + 456) * 2 - 100 等于多少？")
    chat_with_tools("3 的平方加上 4 的平方再开根号是多少？")
