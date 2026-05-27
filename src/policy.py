"""Policy Layer：复杂度判定、模型路由、回退策略。

这是项目从“技术 demo”升级为“生产导向系统”的关键一层。
"""
from typing import Literal


Complexity = Literal["simple", "standard", "complex"]
ModelTier = Literal["tier0", "tier1", "tier2", "tier3"]


class ComplexityClassifier:
    def classify(self, question: str) -> Complexity:
        raise NotImplementedError


class ModelRouter:
    def route(self, complexity: Complexity) -> ModelTier:
        raise NotImplementedError


class FallbackPolicy:
    def should_retry(self, error_message: str) -> bool:
        raise NotImplementedError
