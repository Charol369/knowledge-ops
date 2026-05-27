from pathlib import Path

from src.mcp.server import (
    get_collection_info,
    get_session_artifact,
    inspect_collection,
    inspect_session_artifact,
    search_knowledge,
    summarize_documents,
)
from src.retrieval.artifact_store import ArtifactStore


def test_mcp_search_and_summary_use_local_retrieval_services(tmp_path: Path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "sample.html").write_text(
        "<body><p>MCP retrieval evidence is grounded in local docs.</p></body>",
        encoding="utf-8",
    )

    search_result = search_knowledge(
        "What does MCP retrieval use?",
        top_k=2,
        docs_dir=str(docs_dir),
        index_dir=str(tmp_path / "index"),
    )
    summary = summarize_documents(
        "What does MCP retrieval use?",
        docs_dir=str(docs_dir),
        index_dir=str(tmp_path / "index"),
    )

    assert "sample.html" in search_result
    assert "MCP retrieval evidence" in search_result
    assert "Answer grounded in local evidence" in summary
    assert "sample.html" in summary


def test_mcp_resources_return_collection_and_artifact_metadata(tmp_path: Path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "sample.html").write_text("<body><p>Collection info.</p></body>", encoding="utf-8")
    store = ArtifactStore(root_dir=tmp_path / "artifacts")
    session_id = store.create_session("What was saved?")
    store.save_plan(session_id, ["Retrieve", "Answer"])
    store.save_evidence(session_id, [{"content": "Saved evidence.", "source": "saved.md", "page": 1}])
    store.save_final_answer(session_id, "Saved final answer.")

    collection_info = inspect_collection("fixture", docs_dir=str(docs_dir))
    artifact_info = inspect_session_artifact(session_id, artifact_root=str(tmp_path / "artifacts"))

    assert "fixture" in collection_info
    assert "documents_loaded=1" in collection_info
    assert session_id in artifact_info
    assert "Saved final answer." in artifact_info


def test_mcp_decorated_resources_use_default_local_boundaries():
    assert "collection=default" in get_collection_info("default")
    assert "session_id=missing-session" in get_session_artifact("missing-session")
