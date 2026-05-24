"""结构化输出强制（防御纵深之输出格式约束）

底层是 Pydantic with_structured_output → JSON Schema → OpenAI Function Calling。
DeepSeek 兼容 Function Calling 协议，Day6 04 已验证。
"""
from pydantic import BaseModel, Field


class Answer(BaseModel):
    """QA Agent 的标准输出"""
    answer: str = Field(description="对问题的答案")
    confidence: float = Field(ge=0, le=1, description="自信度 0-1")
    citations: list[dict] = Field(default_factory=list, description="引用 [{source, page, snippet}]")
    needs_human_review: bool = Field(default=False, description="是否需要人工审核")


class Summary(BaseModel):
    """Summary Agent 的标准输出"""
    title: str
    key_points: list[str] = Field(description="3-5 个要点")
    contradictions: list[str] = Field(default_factory=list, description="材料中的矛盾点")


class Report(BaseModel):
    """Report Agent 的标准输出（Markdown）"""
    title: str
    markdown: str = Field(description="完整 Markdown 报告")
    references: list[dict] = Field(default_factory=list, description="参考文献列表")
