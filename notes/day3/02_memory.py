"""Day3 下午 - 带记忆的对话 Bot

目标：让 Chain 在多轮对话中"记住"前面的内容。

核心机制：
  1. ChatMessageHistory：一个简单的容器，存这个 session 的全部消息历史
  2. MessagesPlaceholder("history")：在 prompt 里挖一个"插槽"，让 history 自动插进去
  3. RunnableWithMessageHistory：自动维护历史的 Chain 包装器
     - 每次 invoke 自动把 history 注入 prompt
     - 自动把新一轮的 input + LLM output 追加到 history

验收清单第 4 题：为什么需要 MessagesPlaceholder？它和直接写 ("user", "{history}") 区别？
答：history 是一个 List[BaseMessage]（每条消息有自己的 role），不是单纯字符串。
   MessagesPlaceholder 会把它"展开"成多条 message 注入到 prompt 里，每条保留原 role。
   而 ("user", "{history}") 会把整个列表 str 化塞成一段 user 文本，丢失了 role 区分。
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

load_dotenv()


# ============== 1. LLM ==============
llm = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)


# ============== 2. Prompt（含 history 插槽）==============
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个友好的助手。回答尽量简洁。"),
    MessagesPlaceholder(variable_name="history"),  # 历史消息会被展开成多条 message
    ("user", "{input}"),
])

chain = prompt | llm


# ============== 3. Session 存储：内存 dict（生产环境会换成 Redis / DB）==============
session_store: dict[str, ChatMessageHistory] = {}


def get_history(session_id: str) -> ChatMessageHistory:
    """RunnableWithMessageHistory 会用这个函数按 session_id 取/建历史容器"""
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]


# ============== 4. 自动维护历史的 Chain ==============
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_history,
    input_messages_key="input",       # prompt 里用户输入的变量名
    history_messages_key="history",   # prompt 里历史消息的变量名
)


# ============== 5. 模拟多轮对话 ==============
config = {"configurable": {"session_id": "user_001"}}

turns = [
    "我叫王晟",
    "我是 2027 届 CS 硕士",
    "我叫什么？我什么时候毕业？",  # 验证 Bot 是否记得前两轮
]

for turn in turns:
    print(f"\n👤 User: {turn}")
    resp = chain_with_history.invoke({"input": turn}, config=config)
    print(f"🤖 Bot:  {resp.content}")


# ============== 6. [DEBUG] 看看 session_store 里到底存了什么 ==============
print("\n" + "=" * 60)
print(f"[DEBUG] session_store['user_001'] 里现在有 {len(session_store['user_001'].messages)} 条消息")
print("=" * 60)
for i, msg in enumerate(session_store["user_001"].messages, 1):
    role = type(msg).__name__  # HumanMessage / AIMessage
    preview = msg.content[:40].replace("\n", " ")
    print(f"  [{i}] {role:15s} | {preview}...")
