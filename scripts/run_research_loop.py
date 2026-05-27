"""Sprint 1 linear research loop.

This is intentionally not LangGraph orchestration. It runs:
question -> plan -> retrieve -> synthesize -> answer.
"""
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

from src.agents.planner import ResearchPlanner
from src.agents.reporter import Reporter
from src.agents.synthesizer import Synthesizer
from src.config import settings
from src.ingest.embedder import get_embedder
from src.ingest.loaders import load_directory
from src.ingest.splitters import split_recursive
from src.retrieval.artifact_store import ArtifactStore
from src.retrieval.dense import build_index, load_index, search


def _doc_to_evidence(doc) -> dict:
    return {
        "content": doc.page_content,
        "source": doc.metadata.get("source", ""),
        "page": doc.metadata.get("page"),
    }


def run_research_loop(
    question: str,
    docs_dir: Path,
    index_dir: Path,
    artifact_root: Path,
    embedding_backend: str,
) -> dict:
    started = time.perf_counter()
    planner = ResearchPlanner()
    plan = planner.plan(question)
    store = ArtifactStore(root_dir=artifact_root)
    session_id = store.create_session(question)
    store.save_plan(session_id, plan)

    embedder = get_embedder(backend=embedding_backend)
    if index_dir.exists():
        vectorstore = load_index(str(index_dir), embedder)
    else:
        if not docs_dir.exists():
            blocked_reason = f"Local sample directory does not exist: {docs_dir}"
            store.save_evidence(session_id, [])
            store.save_final_answer(session_id, blocked_reason)
            return {
                "status": "blocked",
                "session_id": session_id,
                "plan": plan,
                "evidence": [],
                "final_answer": blocked_reason,
                "blocked_reason": blocked_reason,
                "latency_seconds": time.perf_counter() - started,
            }
        docs = load_directory(docs_dir)
        chunks = split_recursive(docs)
        if not chunks:
            blocked_reason = f"No supported local evidence was loaded from: {docs_dir}"
            store.save_evidence(session_id, [])
            store.save_final_answer(session_id, blocked_reason)
            return {
                "status": "blocked",
                "session_id": session_id,
                "plan": plan,
                "evidence": [],
                "final_answer": blocked_reason,
                "blocked_reason": blocked_reason,
                "latency_seconds": time.perf_counter() - started,
            }
        vectorstore = build_index(chunks, embedder, index_dir=str(index_dir))

    retrieved_docs = search(vectorstore, question, k=5)
    evidence = [_doc_to_evidence(doc) for doc in retrieved_docs]
    store.save_evidence(session_id, evidence)
    synthesis = Synthesizer().synthesize(evidence)
    final_answer = Reporter().render(question, synthesis)
    store.save_final_answer(session_id, final_answer)
    return {
        "status": "ok",
        "session_id": session_id,
        "plan": plan,
        "evidence": evidence,
        "final_answer": final_answer,
        "latency_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Sprint 1 local research loop.")
    parser.add_argument("--question", required=True)
    parser.add_argument("--docs-dir", default="data")
    parser.add_argument("--index-dir", default="data/faiss/sprint1")
    parser.add_argument("--artifact-root", default=settings.artifact_root_dir)
    parser.add_argument(
        "--embedding-backend",
        default="hash",
        choices=["hash", "local", "fake", "huggingface"],
        help="Use hash/local/fake for offline Sprint 1 smoke tests; huggingface uses configured bge-m3.",
    )
    args = parser.parse_args()

    result = run_research_loop(
        question=args.question,
        docs_dir=Path(args.docs_dir),
        index_dir=Path(args.index_dir),
        artifact_root=Path(args.artifact_root),
        embedding_backend=args.embedding_backend,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"ok", "blocked"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
