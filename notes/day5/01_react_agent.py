"""Day5 上午 - LangGraph ReAct Agent

ReAct = Reasoning + Acting：让 LLM 在"思考"和"调工具"之间循环。
循环：LLM 思考 → 决定调哪个工具 → 执行工具 → 看结果 → 继续思考
     直到 LLM 觉得"任务完成"，输出最终答案。

跟 Day2 的对比（**面试重点**）：
  - Day2 02_function_calling.py：手写 `while True` 循环 + 手动维护 messages 列表
  - Day5 这里：`create_react_agent(llm, tools)` 一行搞定
  这一行的背后，LangGraph 已经把 Day2 那个循环抽象成"图的条件边"：
    LLM 节点 → 有 tool_calls? → 是 → Tool 节点 → 回 LLM 节点
                              → 否 → END
  这就是"线性 Chain 升级成带循环的 Graph"的本质。
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

load_dotenv()


# ============== 1. LLM ==============
llm = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)


# ============== 2. 用 @tool 装饰器定义工具 ==============
# 比 Day2 的纯 JSON Schema 写法简洁——@tool 自动从函数签名 + docstring
# 生成 LLM 看的 schema：
#   - 函数名 → tool name
#   - docstring → tool description（**LLM 凭这个决定何时调用**）
#   - 类型注解 → parameters schema
@tool
def calculator(expression: str) -> str:
    """进行四则运算。expression 例如 '3 + 5 * 2' 或 '(123 + 456) * 2'"""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"计算失败：{e}"


@tool
def get_weather(city: str) -> str:
    """查询某城市当前天气温度（摄氏度）"""
    # mock：真实场景接 OpenWeather / 和风天气 API
    mock_db = {"北京": 25, "上海": 28, "广州": 32, "深圳": 31}
    temp = mock_db.get(city, 20)
    return f"{city} 今天晴，{temp}°C"


@tool
def search_wiki(query: str) -> str:
    """搜索维基百科获取知识"""
    return f"关于「{query}」：这是一个 mock 的搜索结果"


tools = [calculator, get_weather, search_wiki]


# ============== 3. 一行创建 ReAct Agent ==============
# create_react_agent 内部做了什么（**面试可讲**）：
#   1. 把 tools 绑定到 LLM（llm.bind_tools）
#   2. 创建 StateGraph，定义 State（含 messages 列表）
#   3. 加 agent 节点（LLM 调用）+ tools 节点（工具执行）
#   4. 加条件边：agent 输出有 tool_calls → tools 节点；无 → END
#   5. 加边：tools 节点 → 回 agent 节点（循环）
#   6. compile 成可执行的 Runnable
agent = create_react_agent(llm, tools)


# ============== 4. 测试：多工具组合调度 ==============
# 这个问题需要：先调 get_weather 拿温度 → 再调 calculator 算华氏度
# Day2 跑相似的问题要写一个 while 循环。Day5 这里 Agent 自动决策顺序。
question = "北京今天多少度？把这个温度的 1.8 倍 + 32 算出来（华氏度换算）"

print(f"👤 用户：{question}\n")
print("=" * 70)

result = agent.invoke({"messages": [("user", question)]})

# ============== 5. [DEBUG] 打印 Agent 内部的每一步 messages ==============
# Agent 内部走了多少轮 LLM 调用 + 多少次工具调用，全在 messages 链里
print("[DEBUG] Agent 内部 messages 完整链（按时间顺序）：\n")
for i, msg in enumerate(result["messages"], 1):
    role = type(msg).__name__  # HumanMessage / AIMessage / ToolMessage
    print(f"--- [{i}] {role} ---")
    msg.pretty_print()
    print()

print("=" * 70)
print(f"✅ Agent 最终输出：{result['messages'][-1].content}")
print(f"📊 总共 {len(result['messages'])} 条 message（含 user/AI/tool）")
