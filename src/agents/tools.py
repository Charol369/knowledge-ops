"""Agent 可调用工具集。

注意：这些工具是认知层调用 deterministic services 的桥梁，
不是把所有业务逻辑都包装成 Agent。
"""
import ast
import operator

from langchain_core.tools import tool

_MAX_EXPRESSION_LENGTH = 120
_MAX_POWER_EXPONENT = 10

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _evaluate_math_expression(node: ast.AST) -> int | float:
    if isinstance(node, ast.Expression):
        return _evaluate_math_expression(node.body)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_evaluate_math_expression(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        left = _evaluate_math_expression(node.left)
        right = _evaluate_math_expression(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > _MAX_POWER_EXPONENT:
            raise ValueError("幂运算指数过大")
        return _ALLOWED_OPERATORS[type(node.op)](left, right)
    raise ValueError("只支持数字和基础四则运算")


@tool
def search_kb(query: str, top_k: int = 5) -> str:
    """检索企业知识库，返回 Top-K 相关 evidence。"""
    # TODO Sprint 3: 接 retrieval services
    raise NotImplementedError


@tool
def summarize_evidence(query: str) -> str:
    """对检索结果做结构化总结。"""
    # TODO Sprint 3: 接 synthesizer / reporter 的轻量路径
    raise NotImplementedError


@tool
def calculator(expression: str) -> str:
    """安全的数学表达式计算。"""
    try:
        if len(expression) > _MAX_EXPRESSION_LENGTH:
            raise ValueError("表达式过长")
        parsed = ast.parse(expression, mode="eval")
        return str(_evaluate_math_expression(parsed))
    except Exception as e:
        return f"计算失败：{e}"


@tool
def get_current_date() -> str:
    """返回当前日期（YYYY-MM-DD）。"""
    from datetime import date

    return date.today().isoformat()


# TODO Sprint 4+: 根据业务需要追加 create_ticket / send_email / query_crm 等
