"""P0 intent-aware QA regression runner.

This script exercises the local FastAPI query contract with deterministic
assertions over intent, strategy, tool status/results, citations and answer
text. It is not a RAGAS or LLM-as-judge answer-quality evaluation.
"""
import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient  # noqa: E402

from src.config import settings  # noqa: E402
from src.main import app  # noqa: E402


IntentCase = dict[str, Any]


def write_json_output(payload: dict[str, Any], output_path: str | Path | None) -> None:
    if output_path is None:
        return
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_cases(dataset_path: Path) -> list[IntentCase]:
    cases: list[IntentCase] = []
    with dataset_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            case = json.loads(stripped)
            _validate_case(case, line_number)
            cases.append(case)
    if not cases:
        raise ValueError(f"No intent QA cases found in {dataset_path}.")
    return cases


def _validate_case(case: IntentCase, line_number: int) -> None:
    required = {"id", "question", "expected_intent", "expected_strategy"}
    missing = sorted(required - set(case))
    if missing:
        raise ValueError(f"Case line {line_number} is missing fields: {missing}")


def run_intent_qa_eval(
    cases: list[IntentCase],
    *,
    docs_dir: str,
    index_dir: str,
    artifact_root: str | None,
    embedding_backend: str,
) -> dict[str, Any]:
    previous_llm_enabled = settings.llm_synthesis_enabled
    settings.llm_synthesis_enabled = False
    try:
        client = TestClient(app)
        started = time.perf_counter()
        results = [
            run_case(
                client,
                case,
                docs_dir=docs_dir,
                index_dir=index_dir,
                artifact_root=artifact_root,
                embedding_backend=embedding_backend,
            )
            for case in cases
        ]
    finally:
        settings.llm_synthesis_enabled = previous_llm_enabled

    passed = sum(1 for result in results if result["passed"])
    return {
        "status": "ok" if passed == len(results) else "failed",
        "cases_total": len(results),
        "cases_passed": passed,
        "cases_failed": len(results) - passed,
        "latency_seconds": time.perf_counter() - started,
        "docs_dir": docs_dir,
        "index_dir": index_dir,
        "embedding_backend": embedding_backend,
        "notes": [
            "Deterministic P0 intent/workflow regression.",
            "LLM synthesis is disabled for this regression; this is not a RAGAS or answer-quality judge.",
        ],
        "results": results,
    }


def run_case(
    client: TestClient,
    case: IntentCase,
    *,
    docs_dir: str,
    index_dir: str,
    artifact_root: str | None,
    embedding_backend: str,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "question": case["question"],
        "docs_dir": docs_dir,
        "index_dir": index_dir,
        "embedding_backend": embedding_backend,
    }
    if artifact_root:
        payload["artifact_root"] = artifact_root

    response = client.post("/api/v1/query", json=payload)
    if response.status_code != 200:
        return {
            "id": case["id"],
            "passed": False,
            "failures": [f"HTTP status {response.status_code}"],
            "response_text": response.text[:500],
        }
    body = response.json()
    failures = score_response(case, body)
    return {
        "id": case["id"],
        "question": case["question"],
        "passed": not failures,
        "failures": failures,
        "observed": {
            "intent": body.get("intent"),
            "strategy": body.get("strategy"),
            "tool_name": body.get("tool_name"),
            "tool_status": body.get("tool_status"),
            "tool_result": body.get("tool_result"),
            "fallback_reason": body.get("fallback_reason"),
            "synthesis_mode": body.get("synthesis_mode"),
            "synthesis_status": body.get("synthesis_status"),
            "needs_human_review": body.get("needs_human_review"),
            "citations": body.get("citations"),
            "answer_preview": str(body.get("answer", ""))[:500],
        },
    }


def score_response(case: IntentCase, body: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    _expect_equal(failures, body.get("intent"), case.get("expected_intent"), "intent")
    _expect_equal(failures, body.get("strategy"), case.get("expected_strategy"), "strategy")
    if "expected_tool_status" in case:
        _expect_equal(failures, body.get("tool_status"), case["expected_tool_status"], "tool_status")
    if "expected_needs_human_review" in case:
        _expect_equal(
            failures,
            body.get("needs_human_review"),
            case["expected_needs_human_review"],
            "needs_human_review",
        )
    failures.extend(_score_tool_result(case, body.get("tool_result")))
    failures.extend(_score_contains("answer", body.get("answer", ""), case.get("expected_answer_contains", [])))
    failures.extend(
        _score_contains(
            "fallback_reason",
            body.get("fallback_reason", ""),
            case.get("expected_fallback_contains", []),
        )
    )
    failures.extend(_score_sources(case, body.get("citations") or []))
    return failures


def _score_tool_result(case: IntentCase, tool_result: Any) -> list[str]:
    expected = case.get("expected_tool_result")
    if expected is None:
        return []
    if not isinstance(tool_result, dict):
        return ["tool_result is missing or not an object"]
    failures = []
    for key, expected_value in expected.items():
        if tool_result.get(key) != expected_value:
            failures.append(
                f"tool_result.{key}: expected {expected_value!r}, got {tool_result.get(key)!r}"
            )
    return failures


def _score_contains(field: str, value: Any, expected_fragments: list[str]) -> list[str]:
    text = str(value or "").lower()
    return [
        f"{field} missing fragment {fragment!r}"
        for fragment in expected_fragments
        if fragment.lower() not in text
    ]


def _score_sources(case: IntentCase, citations: list[dict[str, Any]]) -> list[str]:
    expected_sources = case.get("expected_sources") or []
    if not expected_sources:
        return []
    normalized_sources = {
        _normalize_path(str(citation.get("source", "")))
        for citation in citations
        if citation.get("source")
    }
    failures = []
    for expected in expected_sources:
        expected_normalized = _normalize_path(expected)
        if not any(
            source == expected_normalized or source.endswith(expected_normalized)
            for source in normalized_sources
        ):
            failures.append(f"citations missing expected source {expected}")
    return failures


def _expect_equal(failures: list[str], actual: Any, expected: Any, field: str) -> None:
    if actual != expected:
        failures.append(f"{field}: expected {expected!r}, got {actual!r}")


def _normalize_path(value: str) -> str:
    return value.replace("\\", "/").lower()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run P0 intent-aware QA regression.")
    parser.add_argument("--dataset", default="eval/intent_qa.jsonl")
    parser.add_argument("--docs-dir", default="data")
    parser.add_argument("--index-dir", default="data/faiss/sprint1")
    parser.add_argument("--artifact-root", default=None)
    parser.add_argument(
        "--embedding-backend",
        default="hash",
        choices=["hash", "local", "fake", "huggingface"],
    )
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    docs_dir = Path(args.docs_dir)
    if not dataset_path.exists():
        result = {
            "status": "blocked",
            "blocked_reason": f"Dataset does not exist: {dataset_path}",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        write_json_output(result, args.output)
        return 0
    if not docs_dir.exists():
        result = {
            "status": "blocked",
            "blocked_reason": f"Local docs directory does not exist: {docs_dir}",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        write_json_output(result, args.output)
        return 0

    result = run_intent_qa_eval(
        load_cases(dataset_path),
        docs_dir=str(docs_dir),
        index_dir=args.index_dir,
        artifact_root=args.artifact_root,
        embedding_backend=args.embedding_backend,
    )
    result["dataset"] = str(dataset_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    write_json_output(result, args.output)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
