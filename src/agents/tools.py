"""Function Calling 工具集

Sprint 3 任务。给 Agent 用的工具集，每个用 @tool 装饰器自动生成 schema。
"""
from langchain_core.tools import tool


@tool
def search_kb(query: str, top_k: int = 5) -> str:
    """检索企业知识库，返回 Top-K 相关 chunks"""
    # TODO Sprint 3: 接到 src.retrieval.hybrid
    raise NotImplementedError


@tool
def calculator(expression: str) -> str:
    """安全的数学表达式计算"""
    # 参考 Day2 02_function_calling.py 的实现
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"计算失败：{e}"


@tool
def get_current_date() -> str:
    """返回当前日期（YYYY-MM-DD）"""
    from datetime import date
    return date.today().isoformat()


# TODO Sprint 3+：根据业务需要追加 send_email / create_ticket / query_crm 等
