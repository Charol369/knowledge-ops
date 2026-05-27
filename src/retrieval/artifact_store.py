import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from typing import Any

from src.config import settings


class ArtifactStore:
    def __init__(self, root_dir: str | Path | None = None):
        self.root_dir = Path(root_dir or settings.artifact_root_dir)

    def create_session(self, question: str) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        session_id = f"{timestamp}-{uuid4().hex[:8]}"
        session_dir = self._session_dir(session_id)
        session_dir.mkdir(parents=True, exist_ok=False)
        self._write_json(
            session_dir / "session.json",
            {"session_id": session_id, "question": question, "created_at": timestamp},
        )
        return session_id

    def save_plan(self, session_id: str, plan: list[str]) -> None:
        self._write_json(self._session_dir(session_id) / "plan.json", {"plan": plan})

    def save_evidence(self, session_id: str, evidence: list[dict[str, Any]]) -> None:
        self._write_json(
            self._session_dir(session_id) / "evidence.json",
            {"evidence": evidence},
        )

    def save_final_answer(self, session_id: str, final_answer: str) -> None:
        session_dir = self._session_dir(session_id)
        session_dir.mkdir(parents=True, exist_ok=True)
        (session_dir / "final_answer.md").write_text(final_answer, encoding="utf-8")

    def save_report(self, session_id: str, report: str) -> None:
        self.save_final_answer(session_id, report)

    def _session_dir(self, session_id: str) -> Path:
        return self.root_dir / session_id

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
