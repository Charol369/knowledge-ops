"""引用强制（Citation Enforcement）

防幻觉的 4 把刀之一（Day2 Anthropic Ch8）：
  要求 LLM 每个事实必须附 [来源: X]，编造的话没法贴标签。

Sprint 3 任务：实现 citation 提取 + 校验（确保每个 citation 真的指向了 context 里的某个 chunk）。
"""
from src.agents.graph import AgentState


def extract_citations(answer_text: str) -> list[dict]:
    """从答案文本里抽取 [来源: X, page Y] 这种引用标记"""
    # TODO Sprint 3: 正则 r'\[来源:\s*([^,\]]+)(?:,\s*page\s*(\d+))?\]'
    raise NotImplementedError


def verify_citations(citations: list[dict], context_chunks: list) -> tuple[bool, list[str]]:
    """校验每个 citation 是否指向真实的 context chunk。返回 (all_valid, invalid_list)"""
    # TODO Sprint 3: 用 doc.metadata.source / page 匹配
    raise NotImplementedError
