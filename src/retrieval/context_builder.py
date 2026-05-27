"""Context Builder：把检索结果组织成模型真正该看的上下文。

职责：
- 合并 system/project/task/evidence/focus recap 五层上下文
- 避免把全部历史原样塞进 prompt
- 为不同 tier 模型输出不同粒度的上下文
"""
from typing import Any


class ContextBuilder:
    def build(self, question: str, evidence: list[dict], focus_recap: str | None = None) -> dict[str, Any]:
        raise NotImplementedError
