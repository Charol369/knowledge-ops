"""Verifier / Reflection：高价值请求的选择性校验节点。"""
from typing import Any


class Verifier:
    def verify(self, answer: str, citations: list[dict]) -> dict[str, Any]:
        raise NotImplementedError


def verifier_node(state: dict[str, Any]) -> dict[str, Any]:
    # TODO Sprint 3: 只在复杂研究 / 最终报告 / 冲突证据时启用
    raise NotImplementedError
