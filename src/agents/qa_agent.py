"""QA Agent：基于检索结果回答用户问题（项目 1 的主力 Agent）

System prompt 的 7 层结构（Day2 Anthropic Ch9）：
  1. 角色：企业知识库问答专家
  2. 任务：基于上下文回答
  3. 规则：找不到说不知道，绝不编造（防幻觉刀 1）
  4. Few-shot：1-2 个示例
  5. CoT 引导：<thinking> 先判断 context 是否足够
  6. 输出格式：JSON {answer, citations, confidence}
  7. XML 包装数据：<context>...</context>

Sprint 3 任务。
"""
from src.agents.graph import AgentState


QA_SYSTEM_PROMPT = """你是企业知识库问答专家。

【铁律】
1. 只基于 <context> 里的内容回答，<context> 没有的信息绝对不要编造
2. 每个事实必须附引用 [来源: doc_name, page X]
3. 找不到答案时直接回答"我不知道"，不要展开

【输出格式】
JSON: {"answer": "...", "citations": [{"source": "...", "page": N}], "confidence": 0.0-1.0}

【思考过程】
请先在 <thinking> 里：(1) 列出 context 提到的相关信息 (2) 判断信息是否足以回答 (3) 不足说我不知道
然后在 <answer> 里给最终回答。
"""


def qa_agent(state: AgentState) -> dict:
    """QA Agent 节点函数"""
    # TODO Sprint 3:
    #   1. 拼 prompt = QA_SYSTEM_PROMPT + <context>{state['context']}</context> + question
    #   2. llm.with_structured_output(Answer).invoke(...)
    #   3. 返回 {"answer": ..., "citations": ...}
    raise NotImplementedError
