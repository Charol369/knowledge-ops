"""Small labeled retrieval evaluation for KnowledgeOps.

This script computes source/page Hit@K on a local JSONL dataset. It does not
call external models and should not be treated as a full RAGAS or production
quality benchmark.
"""
import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from langchain_core.documents import Document

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.ingest.embedder import get_embedder
from src.ingest.loaders import load_directory
from src.ingest.splitters import split_recursive
from src.retrieval.dense import build_index, search
from src.retrieval.hybrid import reciprocal_rank_fusion
from src.retrieval.sparse import BM25Retriever


RetrievalCase = dict[str, Any]


def write_json_output(payload: dict[str, Any], output_path: str | Path | None) -> None:
    """Persist retrieval evaluation output as a reproducible local artifact."""
    if output_path is None:
        return
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_cases(dataset_path: Path) -> list[RetrievalCase]:
    """Load JSONL retrieval cases."""
    cases: list[RetrievalCase] = []
    with dataset_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            case = json.loads(stripped)
            _validate_case(case, line_number)
            cases.append(case)
    if not cases:
        raise ValueError(f"No retrieval cases found in {dataset_path}.")
    return cases


def _validate_case(case: RetrievalCase, line_number: int) -> None:
    required = {"id", "question", "expected_sources"}
    missing = sorted(required - set(case))
    if missing:
        raise ValueError(f"Case line {line_number} is missing fields: {missing}")
    if not isinstance(case["expected_sources"], list) or not case["expected_sources"]:
        raise ValueError(f"Case line {line_number} must include non-empty expected_sources.")


def run_labeled_retrieval_eval(
    docs: list[Document],
    cases: list[RetrievalCase],
    retrieval_modes: list[str],
    top_k: int,
    embedder,
) -> dict[str, Any]:
    if not docs:
        return {
            "status": "blocked",
            "blocked_reason": "No local documents were provided for retrieval evaluation.",
        }
    if not cases:
        return {
            "status": "blocked",
            "blocked_reason": "No labeled retrieval cases were provided.",
        }
    if top_k <= 0:
        raise ValueError("top_k must be positive.")

    vectorstore = None
    sparse_retriever = BM25Retriever(docs)
    result: dict[str, Any] = {
        "status": "ok",
        "dataset_examples": len(cases),
        "documents": len(docs),
        "top_k": top_k,
        "metrics": {},
        "notes": [
            "Metrics are source/page hit rates on a small local labeled set.",
            "This is not a RAGAS faithfulness or answer quality evaluation.",
        ],
    }

    for mode in retrieval_modes:
        normalized = mode.strip().lower()
        started = time.perf_counter()
        if normalized == "dense" and vectorstore is None:
            vectorstore = build_index(docs, embedder)

        per_case: list[dict[str, Any]] = []
        for case in cases:
            if normalized == "dense":
                assert vectorstore is not None
                retrieved = search(vectorstore, case["question"], k=top_k)
            elif normalized == "sparse":
                retrieved = sparse_retriever.search(case["question"], k=top_k)
            elif normalized == "hybrid":
                if vectorstore is None:
                    vectorstore = build_index(docs, embedder)
                dense_results = search(vectorstore, case["question"], k=top_k)
                sparse_results = sparse_retriever.search(case["question"], k=top_k)
                retrieved = reciprocal_rank_fusion(
                    [dense_results, sparse_results],
                    top_n=top_k,
                )
            else:
                raise ValueError(f"Unsupported retrieval mode: {mode}")
            per_case.append(score_case(case, retrieved))

        result["metrics"][normalized] = summarize_mode(
            per_case=per_case,
            top_k=top_k,
            started=started,
        )
    return result


def score_case(case: RetrievalCase, retrieved: list[Document]) -> dict[str, Any]:
    first_hit_rank: int | None = None
    for rank, doc in enumerate(retrieved, start=1):
        if is_relevant(doc, case):
            first_hit_rank = rank
            break
    return {
        "id": case["id"],
        "hit": first_hit_rank is not None,
        "first_hit_rank": first_hit_rank,
        "expected_sources": case["expected_sources"],
        "expected_pages": case.get("expected_pages", []),
        "returned": [_document_ref(doc) for doc in retrieved],
    }


def summarize_mode(
    per_case: list[dict[str, Any]],
    top_k: int,
    started: float,
) -> dict[str, Any]:
    total = len(per_case)
    hits = sum(1 for item in per_case if item["hit"])
    reciprocal_ranks = [
        1.0 / item["first_hit_rank"] if item["first_hit_rank"] else 0.0
        for item in per_case
    ]
    return {
        "hit_at_k": hits / total,
        "question_recall_at_k": hits / total,
        "mrr_at_k": sum(reciprocal_ranks) / total,
        "hits": hits,
        "total": total,
        "top_k": top_k,
        "latency_seconds": time.perf_counter() - started,
        "misses": [item for item in per_case if not item["hit"]],
    }


def is_relevant(doc: Document, case: RetrievalCase) -> bool:
    expected_sources = [_normalize_path(source) for source in case["expected_sources"]]
    actual_source = _normalize_path(str(doc.metadata.get("source", "")))
    source_hit = any(
        actual_source == expected_source or actual_source.endswith(expected_source)
        for expected_source in expected_sources
    )
    if not source_hit:
        return False

    expected_pages = case.get("expected_pages") or []
    if not expected_pages:
        return True
    try:
        actual_page = int(doc.metadata.get("page"))
    except (TypeError, ValueError):
        return False
    return actual_page in {int(page) for page in expected_pages}


def _document_ref(doc: Document) -> dict[str, Any]:
    return {
        "source": doc.metadata.get("source"),
        "page": doc.metadata.get("page"),
        "snippet": " ".join(doc.page_content.split())[:160],
    }


def _normalize_path(value: str) -> str:
    return value.replace("\\", "/").lower()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run labeled retrieval Hit@K evaluation.")
    parser.add_argument("--dataset", default="eval/retrieval_qa.jsonl")
    parser.add_argument("--docs-dir", default="data")
    parser.add_argument("--retrieval", default="dense,hybrid")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to persist the JSON evaluation result.",
    )
    parser.add_argument(
        "--embedding-backend",
        default="hash",
        choices=["hash", "local", "fake", "huggingface"],
    )
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

    cases = load_cases(dataset_path)
    docs = split_recursive(load_directory(docs_dir))
    result = run_labeled_retrieval_eval(
        docs=docs,
        cases=cases,
        retrieval_modes=[item.strip() for item in args.retrieval.split(",") if item.strip()],
        top_k=args.top_k,
        embedder=get_embedder(backend=args.embedding_backend),
    )
    result["dataset"] = str(dataset_path)
    result["docs_dir"] = str(docs_dir)
    result["embedding_backend"] = args.embedding_backend
    print(json.dumps(result, ensure_ascii=False, indent=2))
    write_json_output(result, args.output)
    return 0 if result["status"] in {"ok", "blocked"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
