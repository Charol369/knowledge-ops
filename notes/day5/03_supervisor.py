"""Day5 下午 - Supervisor 模式：1 个监督 + N 个工作 Agent

Supervisor 模式是 Multi-Agent 三模式中最常用的（另外两个：Hierarchical / Network）。
流程：
  用户问题 → Supervisor 判断意图 → 路由到合适的 Worker Agent → 返回答案

关键技术：`add_conditional_edges` 条件边
  - 普通 `add_edge(A, B)`：A 跑完一定跳 B
  - 条件边 `add_conditional_edges(A, route_fn)`：A 跑完调 route_fn，
    根据返回值（节点名字符串）跳到对应节点

工程价值（项目 1 直接用到）：
  KnowledgeOps 的 QA / Summary / Report 三个 Agent 就是 Supervisor 模式。
  Supervisor 看用户问题决定走哪条线，比"用户必须选下拉框"体验好得多。
"""
import os
import sys
from typing import TypedDict, Literal

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)


# ============== 1. State：共享内存 ==============
class State(TypedDict):
    question: str
    intent: str    # Supervisor 决定走哪个 Agent（"math" / "story"）
    answer: str    # 最终答案


# ============== 2. Supervisor 节点：判断意图 ==============
def supervisor(state: State) -> dict:
    """Supervisor 看用户问题，输出 intent 字段（math / story）"""
    prompt = f"""判断这个问题属于哪类，只返回一个单词：
- "math"（数学计算、公式、推理）
- "story"（写故事、创意文本、虚构内容）

问题：{state['question']}
类别（只回 math 或 story）：
"""
    resp = llm.invoke(prompt).content.strip().lower()
    # 防御性：LLM 可能多写字（如 "math."）→ 用 substring 判断
    intent = "math" if "math" in resp else "story"
    print(f"  🧭 [supervisor] LLM 回答='{resp}' → intent='{intent}'")
    return {"intent": intent}


# ============== 3. Worker Agents ==============
def math_agent(state: State) -> dict:
    """数学 Agent"""
    print(f"  🔢 [math_agent] 接到任务")
    resp = llm.invoke(f"作为数学老师，用清晰的步骤回答：{state['question']}")
    return {"answer": f"[Math Agent]\n{resp.content}"}


def story_agent(state: State) -> dict:
    """故事 Agent"""
    print(f"  📖 [story_agent] 接到任务")
    resp = llm.invoke(f"作为小说家，用故事形式回答（300 字内）：{state['question']}")
    return {"answer": f"[Story Agent]\n{resp.content}"}


# ============== 4. 路由函数（条件边的核心）==============
# route 返回的字符串必须是 add_node 注册过的节点名
# Literal 类型注解给 IDE 提示 + 让代码意图清晰
def route(state: State) -> Literal["math_agent", "story_agent"]:
    """根据 Supervisor 决定的 intent 选下一个节点"""
    return f"{state['intent']}_agent"


# ============== 5. 组装图（含条件边）==============
graph = StateGraph(State)
graph.add_node("supervisor", supervisor)
graph.add_node("math_agent", math_agent)
graph.add_node("story_agent", story_agent)

graph.add_edge(START, "supervisor")

# 🔑 关键：条件边 add_conditional_edges
# 第 2 参数 route 是路由函数，返回值决定跳哪
graph.add_conditional_edges("supervisor", route)

# 两个 Worker 跑完都到 END
graph.add_edge("math_agent", END)
graph.add_edge("story_agent", END)

app = graph.compile()


# ============== 6. [DEBUG] 看图的拓扑 ==============
print("=" * 60)
print("[DEBUG] Supervisor Graph 拓扑结构：")
print("=" * 60)
try:
    print(app.get_graph().draw_ascii())
except Exception as e:
    print(f"（draw_ascii 不可用：{e}）")
    print(app.get_graph().draw_mermaid())
print()


# ============== 7. 测试：两个不同意图的问题 ==============
questions = [
    "123 * 456 等于多少？请列出竖式过程。",
    "讲一个 200 字的故事：一个失眠的程序员在凌晨 3 点发现了一个奇怪的 bug。",
]

for q in questions:
    print("=" * 70)
    print(f"👤 用户：{q}\n")
    result = app.invoke({"question": q})
    print(f"\n💡 最终答案：\n{result['answer']}\n")
