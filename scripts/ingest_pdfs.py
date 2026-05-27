"""Sprint 1 local ingest script for PDF / DOCX / HTML directories."""
import argparse
import json
import sys
import time
from pathlib import Path

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
from src.retrieval.dense import build_index


def run_ingest(
    directory: Path,
    index_dir: Path,
    embedding_backend: str,
) -> dict:
    started = time.perf_counter()
    if not directory.exists():
        return {
            "status": "blocked",
            "blocked_reason": f"Local sample directory does not exist: {directory}",
        }
    docs = load_directory(directory)
    chunks = split_recursive(docs)
    if not chunks:
        return {
            "status": "blocked",
            "documents_loaded": len(docs),
            "chunks_created": 0,
            "blocked_reason": f"No supported local content was loaded from: {directory}",
        }
    build_index(chunks, get_embedder(backend=embedding_backend), index_dir=str(index_dir))
    return {
        "status": "ok",
        "directory": str(directory),
        "index_dir": str(index_dir),
        "documents_loaded": len(docs),
        "chunks_created": len(chunks),
        "latency_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Sprint 1 local FAISS index.")
    parser.add_argument("directory")
    parser.add_argument("--index-dir", default="data/faiss/sprint1")
    parser.add_argument(
        "--embedding-backend",
        default="hash",
        choices=["hash", "local", "fake", "huggingface"],
        help="Use hash/local/fake for offline Sprint 1 smoke tests; huggingface uses configured bge-m3.",
    )
    args = parser.parse_args()
    result = run_ingest(
        directory=Path(args.directory),
        index_dir=Path(args.index_dir),
        embedding_backend=args.embedding_backend,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"ok", "blocked"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
