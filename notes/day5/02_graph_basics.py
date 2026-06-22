"""Day5 上午 - 手撸 LangGraph 两节点图（理解原理）

不用 prebuilt，自己组装最简的 StateGraph，看清楚三要素：
  1. State（TypedDict）：图的"共享内存"，所有节点都能读写
  2. Node（函数）：State → 部分 State 更新（dict）
  3. Edge（边）：控制流，可有条件 / 可成环

本图是"写初稿 → 润色"两节点的线性流程。是为了让你看清楚 LangGraph 最小可用单元，
明白了这个，03 的条件分支和 ReAct 的循环都是这套机制的扩展。
"""
import os
import sys
from typing import TypedDict

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)


# ============== 1. 定义 State（图的共享内存）==============
# TypedDict 给字段类型提示，runtime 不强制校验
# 每个节点只更新自己负责的字段，不用全量传 State
# State 也可以用 Pydantic（更严，带校验），但 TypedDict 是官方默认推荐
class State(TypedDict):
    question: str
    draft: str
    final: str


# ============== 2. 定义节点（function: State -> dict 部分更新）==============
def write_draft(state: State) -> dict:
    """节点 1：基于问题写一段初稿"""
    print(f"  🟦 [write_draft] 读到 question = {state['question'][:30]}...")
    resp = llm.invoke(f"请用 50 字回答：{state['question']}")
    return {"draft": resp.content}  # 只返回需要更新的字段


def polish(state: State) -> dict:
    """节点 2：把初稿润色得更生动"""
    print(f"  🟩 [polish] 读到 draft = {state['draft'][:30]}...")
    resp = llm.invoke(f"把下面这段话改写得更生动、富有画面感：\n{state['draft']}")
    return {"final": resp.content}


# ============== 3. 组装图（StateGraph + Node + Edge）==============
graph = StateGraph(State)

# 加节点
graph.add_node("write_draft", write_draft)
graph.add_node("polish", polish)

# 加边：START → write_draft → polish → END
graph.add_edge(START, "write_draft")
graph.add_edge("write_draft", "polish")
graph.add_edge("polish", END)

# compile：把图编译成可执行的 Runnable（跟 LCEL 的 chain 同接口）
app = graph.compile()


# ============== 4. [DEBUG] 可视化图的拓扑结构 ==============
# get_graph().draw_ascii() 在控制台打印 ASCII 图（不需要任何额外依赖）
# 也可以用 .draw_mermaid() 输出 mermaid 文本贴到 notion / mermaid live editor 看
print("=" * 60)
print("[DEBUG] Graph 拓扑结构：")
print("=" * 60)
try:
    print(app.get_graph().draw_ascii())
except Exception as e:
    # ASCII 渲染需要 grandalf 包，没有就退化到 mermaid 文本
    print(f"（draw_ascii 不可用：{e}）")
    print("Mermaid 文本表示（贴到 https://mermaid.live 渲染）：\n")
    print(app.get_graph().draw_mermaid())
print()


# ============== 5. 调用图 ==============
print("=" * 60)
print("[运行图]")
print("=" * 60)
result = app.invoke({"question": "什么是黑洞？"})

print("\n📝 初稿：")
print(result["draft"])
print("\n✨ 润色：")
print(result["final"])
