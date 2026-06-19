"""Sprint 2 local retrieval benchmark smoke runner.

This script validates dense and hybrid retrieval wiring on local documents.
It reports latency and candidate counts only; labeled quality metrics remain
pending until a real evaluation run is configured and executed.
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


def write_json_output(payload: dict[str, Any], output_path: str | Path | None) -> None:
    """Persist benchmark output when the caller wants a reproducible artifact."""
    if output_path is None:
        return
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_retrieval_benchmark(
    docs: list[Document],
    query: str,
    retrieval_modes: list[str],
    top_k: int,
    embedder,
) -> dict[str, Any]:
    if not docs:
        return {
            "status": "blocked",
            "blocked_reason": "No local documents were provided for retrieval benchmark.",
        }
    if top_k <= 0:
        raise ValueError("top_k must be positive.")

    result: dict[str, Any] = {
        "status": "ok",
        "query": query,
        "documents": len(docs),
        "retrieval": {},
        "metrics": {
            "recall_at_5": "pending_labeled_eval",
            "ragas": "pending_real_run",
            "qps": "pending_load_test",
        },
    }

    dense_results: list[Document] | None = None
    sparse_results: list[Document] | None = None
    vectorstore = None

    for mode in retrieval_modes:
        normalized = mode.strip().lower()
        started = time.perf_counter()
        if normalized == "dense":
            if vectorstore is None:
                vectorstore = build_index(docs, embedder)
            dense_results = search(vectorstore, query, k=top_k)
            _record_result(result, "dense", dense_results, top_k, started)
        elif normalized == "sparse":
            sparse_results = BM25Retriever(docs).search(query, k=top_k)
            _record_result(result, "sparse", sparse_results, top_k, started)
        elif normalized == "hybrid":
            if vectorstore is None:
                vectorstore = build_index(docs, embedder)
            if dense_results is None:
                dense_results = search(vectorstore, query, k=top_k)
            if sparse_results is None:
                sparse_results = BM25Retriever(docs).search(query, k=top_k)
            hybrid_results = reciprocal_rank_fusion(
                [dense_results, sparse_results],
                top_n=top_k,
            )
            _record_result(result, "hybrid", hybrid_results, top_k, started)
        else:
            raise ValueError(f"Unsupported retrieval mode: {mode}")
    return result


def _record_result(
    payload: dict[str, Any],
    mode: str,
    documents: list[Document],
    top_k: int,
    started: float,
) -> None:
    payload["retrieval"][mode] = {
        "top_k": top_k,
        "returned": len(documents),
        "latency_seconds": time.perf_counter() - started,
        "sources": [doc.metadata.get("source") for doc in documents],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Sprint 2 local retrieval benchmark smoke test.")
    parser.add_argument("--retrieval", default="dense,hybrid")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--docs-dir", default="data")
    parser.add_argument("--query", default="Summarize the indexed evidence")
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to persist the JSON benchmark result.",
    )
    parser.add_argument(
        "--embedding-backend",
        default="hash",
        choices=["hash", "local", "fake", "huggingface"],
    )
    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    if not docs_dir.exists():
        result = {
            "status": "blocked",
            "blocked_reason": f"Local docs directory does not exist: {docs_dir}",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        write_json_output(result, args.output)
        return 0

    docs = split_recursive(load_directory(docs_dir))
    result = run_retrieval_benchmark(
        docs=docs,
        query=args.query,
        retrieval_modes=[item.strip() for item in args.retrieval.split(",") if item.strip()],
        top_k=args.top_k,
        embedder=get_embedder(backend=args.embedding_backend),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    write_json_output(result, args.output)
    return 0 if result["status"] in {"ok", "blocked"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
