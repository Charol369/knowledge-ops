from pathlib import Path

from fastapi.testclient import TestClient
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from src.main import app
from src.retrieval.artifact_store import ArtifactStore
from src.retrieval.dense import build_index, load_index, search


class KeywordEmbeddings(Embeddings):
    def _embed(self, text: str) -> list[float]:
        lower = text.lower()
        return [
            float("alpha" in lower),
            float("beta" in lower),
            float("gamma" in lower),
            1.0,
        ]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


def test_build_load_and_search_faiss_index_preserves_source_metadata(tmp_path: Path):
    docs = [
        Document(page_content="alpha evidence", metadata={"source": "alpha.md"}),
        Document(page_content="beta evidence", metadata={"source": "beta.md"}),
    ]
    index_dir = tmp_path / "index"
    embedder = KeywordEmbeddings()

    vectorstore = build_index(docs, embedder, index_dir=index_dir)
    loaded = load_index(index_dir, embedder)
    results = search(loaded, "alpha", k=5)

    assert index_dir.exists()
    assert vectorstore is not None
    assert len(results) <= 5
    assert results[0].metadata["source"] == "alpha.md"


def test_artifact_store_persists_plan_evidence_and_final_answer(tmp_path: Path):
    store = ArtifactStore(root_dir=tmp_path)
    session_id = store.create_session("What is Sprint 1?")

    store.save_plan(session_id, ["Find evidence", "Answer from evidence"])
    store.save_evidence(session_id, [{"source": "alpha.md", "content": "alpha evidence"}])
    store.save_final_answer(session_id, "Sprint 1 is the minimal research loop.")

    session_dir = tmp_path / session_id
    assert (session_dir / "plan.json").exists()
    assert (session_dir / "evidence.json").exists()
    assert (session_dir / "final_answer.md").read_text(encoding="utf-8").startswith("Sprint 1")


def test_ingest_endpoint_validates_request_and_no_longer_returns_501(tmp_path: Path):
    html_path = tmp_path / "sample.html"
    html_path.write_text("<body><p>API ingest evidence.</p></body>", encoding="utf-8")
    client = TestClient(app)

    invalid = client.post("/api/v1/ingest", json={})
    valid = client.post(
        "/api/v1/ingest",
        json={"path": str(tmp_path), "build_index": False},
    )

    assert invalid.status_code == 422
    assert valid.status_code != 501
    assert valid.status_code == 200
    body = valid.json()
    assert body["status"] == "ok"
    assert body["documents_loaded"] == 1
    assert body["chunks_created"] >= 1
