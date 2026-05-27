"""Sprint 2 RAGAS evaluation scaffold.

Dry-run mode validates the local dataset and pipeline wiring without computing
or fabricating RAGAS metrics. Real metric execution is intentionally not the
Sprint 2 local acceptance path because it may require model credentials.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


REQUIRED_FIELDS = {"question", "ground_truth"}


def load_testset(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"RAGAS testset does not exist: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
        missing = REQUIRED_FIELDS - set(row)
        if missing:
            raise ValueError(f"Missing fields at {path}:{line_number}: {sorted(missing)}")
        rows.append(row)
    if not rows:
        raise ValueError(f"RAGAS testset is empty: {path}")
    return rows


def dry_run(testset_path: Path) -> dict[str, Any]:
    rows = load_testset(testset_path)
    return {
        "status": "ok",
        "mode": "dry-run",
        "testset_path": str(testset_path),
        "examples": len(rows),
        "validated_fields": sorted(REQUIRED_FIELDS),
        "metrics": {
            "faithfulness": "pending_real_run",
            "answer_relevancy": "pending_real_run",
            "context_precision": "pending_real_run",
            "context_recall": "pending_real_run",
        },
        "note": "Dry-run validates dataset/wiring only; no RAGAS metric values were computed.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Sprint 2 RAGAS evaluation scaffold.")
    parser.add_argument("--testset", default="eval/testset.jsonl")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.dry_run:
        result = {
            "status": "blocked",
            "blocked_reason": (
                "Real RAGAS metric execution is not configured for Sprint 2 local acceptance. "
                "Run with --dry-run, or configure explicit evaluator models before real metrics."
            ),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    result = dry_run(Path(args.testset))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
