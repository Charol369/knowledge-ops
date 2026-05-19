"""Day2 下午 - Function Calling 多工具调度

让 LLM 在多个工具之间自主选择 + 链式调用：
- 计算器 + 天气查询 → LLM 自己决定先调谁、后调谁
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


# ============== 1. 工具说明书 ==============
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "进行四则运算或数学表达式求值。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，例如 '25 * 1.8 + 32'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询某个城市当前天气和温度。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名，例如 '北京'"}
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_wiki",
            "description": "在维基百科搜索某个概念的简短解释。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"}
                },
                "required": ["query"],
            },
        },
    },
]


# ============== 2. 真实实现（含 mock 数据）==============
def calculator(expression: str) -> str:
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"计算失败：{e}"


def get_weather(city: str) -> str:
    # mock：实际场景对接天气 API
    mock_data = {
        "北京": "晴，25°C，西北风 2 级",
        "上海": "多云，22°C，东南风 3 级",
        "深圳": "雷阵雨，28°C，南风 4 级",
    }
    return mock_data.get(city, f"{city} 天气数据未收录")


def search_wiki(query: str) -> str:
    # mock：实际场景调维基或搜索 API
    return f"[Wiki 搜索] 关于「{query}」：（这里返回模拟的百科条目摘要）"


# 工具名 → 函数 的分发表
TOOL_REGISTRY = {
    "calculator": calculator,
    "get_weather": get_weather,
    "search_wiki": search_wiki,
}


# ============== 3. 多轮工具调用循环 ==============
def chat_with_tools(user_question: str, max_iterations: int = 10):
    print(f"\n{'=' * 60}")
    print(f"👤 用户：{user_question}")
    print(f"{'=' * 60}")

    messages = [{"role": "user", "content": user_question}]

    for i in range(max_iterations):
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
        )
        msg = resp.choices[0].message

        # LLM 不再调工具，结束
        if not msg.tool_calls:
            print(f"\n🤖 最终回答：\n{msg.content}\n")
            return

        # 处理所有 tool_calls（LLM 可能一次返回多个）
        messages.append(msg)
        for call in msg.tool_calls:
            tool_name = call.function.name
            args = json.loads(call.function.arguments)
            print(f"\n🔧 [Round {i+1}] 调用 {tool_name}({args})")

            # 用分发表调用对应函数
            fn = TOOL_REGISTRY.get(tool_name)
            result = fn(**args) if fn else f"未知工具：{tool_name}"
            print(f"📤 返回：{result}")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })

    print("⚠️ 达到最大迭代次数")


if __name__ == "__main__":
    # 测试 1：只用计算器
    chat_with_tools("(123 + 456) * 2 - 100 等于多少？")

    # 测试 2：天气 + 计算器（华氏度换算）
    chat_with_tools("北京今天多少度？把这个温度的 1.8 倍 + 32 算出来（这是华氏度换算公式）")

    # 测试 3：维基 + 计算器
    chat_with_tools("帮我查一下『斐波那契』是什么，然后告诉我第 10 个斐波那契数是多少（用 fib(n)=fib(n-1)+fib(n-2) 算）")
