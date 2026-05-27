"""结构化输出强制。

新的项目架构要求把输出 schema 与研究型流程对齐：
- Planner 输出 plan
- Reporter 输出 final report
- Answer/Report 都要显式支持 citation 与人工审核标记
"""
from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    step_id: str
    description: str


class Plan(BaseModel):
    complexity: str = Field(description="simple/standard/complex")
    model_tier: str = Field(description="tier1/tier2/tier3")
    requires_reflection: bool = False
    steps: list[PlanStep] = Field(default_factory=list)


class Answer(BaseModel):
    answer: str = Field(description="对问题的答案")
    confidence: float = Field(ge=0, le=1, description="自信度 0-1")
    citations: list[dict] = Field(default_factory=list, description="引用 [{source, page, snippet}]")
    needs_human_review: bool = Field(default=False, description="是否需要人工审核")


class Summary(BaseModel):
    title: str
    key_points: list[str] = Field(description="3-5 个要点")
    contradictions: list[str] = Field(default_factory=list, description="材料中的矛盾点")


class Report(BaseModel):
    title: str
    markdown: str = Field(description="完整 Markdown 报告")
    references: list[dict] = Field(default_factory=list, description="参考文献列表")
    needs_human_review: bool = Field(default=False)
