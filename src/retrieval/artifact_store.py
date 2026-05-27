"""Artifact Store：研究中间产物持久化。

存储内容：
- plan.json
- evidence.json
- synthesis.json
- final_report.md
"""
from typing import Any


class ArtifactStore:
    def create_session(self, question: str) -> str:
        raise NotImplementedError

    def save_plan(self, session_id: str, plan: list[str]) -> None:
        raise NotImplementedError

    def save_evidence(self, session_id: str, evidence: list[dict[str, Any]]) -> None:
        raise NotImplementedError

    def save_report(self, session_id: str, report: str) -> None:
        raise NotImplementedError
