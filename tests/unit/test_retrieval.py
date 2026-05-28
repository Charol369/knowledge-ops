from pathlib import Path

from fastapi.testclient import TestClient
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from src.main import app
from src.retrieval.artifact_store import ArtifactStore
from src.retrieval.dense import build_index, load_index, search
from src.retrieval.hybrid import reciprocal_rank_fusion
from src.retrieval.query_transform import (
    decompose_query,
    hyde_transform,
    multi_query_expand,
)
from src.retrieval.rerank import CrossEncoderReranker
from src.retrieval.sparse import BM25Retriever


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


def test_ingest_endpoint_build_index_uses_local_hash_embedding_backend_by_default(
    tmp_path: Path,
    monkeypatch,
):
    html_path = tmp_path / "sample.html"
    html_path.write_text("<body><p>Indexed API ingest evidence.</p></body>", encoding="utf-8")
    calls = {}

    def fake_get_embedder(model_name=None, backend="huggingface"):
        calls["backend"] = backend
        return object()

    def fake_build_index(docs, embedder, index_dir=None):
        calls["docs"] = docs
        calls["index_dir"] = index_dir
        return object()

    monkeypatch.setattr("src.ingest.embedder.get_embedder", fake_get_embedder)
    monkeypatch.setattr("src.retrieval.dense.build_index", fake_build_index)
    client = TestClient(app)

    response = client.post(
        "/api/v1/ingest",
        json={
            "path": str(tmp_path),
            "build_index": True,
            "index_dir": str(tmp_path / "index"),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert calls["backend"] == "hash"
    assert calls["index_dir"] == str(tmp_path / "index")
    assert len(calls["docs"]) >= 1


def test_bm25_sparse_retriever_prioritizes_exact_terms_and_preserves_source():
    docs = [
        Document(page_content="Transformer attention uses multi head self attention.", metadata={"source": "paper.md", "page": 1}),
        Document(page_content="Milvus stores vector embeddings for semantic retrieval.", metadata={"source": "vector.md"}),
        Document(page_content="RAG combines retrieval with generation.", metadata={"source": "rag.md"}),
    ]

    results = BM25Retriever(docs).search("multi head attention", k=2)

    assert results[0].metadata["source"] == "paper.md"
    assert results[0].metadata["page"] == 1
    assert len(results) == 2


def test_rrf_fuses_rankings_deduplicates_and_preserves_metadata():
    shared = Document(page_content="shared transformer evidence", metadata={"source": "shared.md", "page": 2})
    dense_only = Document(page_content="dense semantic evidence", metadata={"source": "dense.md"})
    sparse_only = Document(page_content="sparse keyword evidence", metadata={"source": "sparse.md"})

    fused = reciprocal_rank_fusion(
        [[dense_only, shared], [shared, sparse_only]],
        k=10,
        top_n=3,
    )

    assert [doc.metadata["source"] for doc in fused] == ["shared.md", "dense.md", "sparse.md"]
    assert fused[0].metadata["page"] == 2
    assert "rrf_score" in fused[0].metadata


def test_cross_encoder_reranker_can_use_local_scorer_without_model_download():
    docs = [
        Document(page_content="irrelevant cache policy", metadata={"source": "cache.md"}),
        Document(page_content="Transformer attention and encoder decoder architecture", metadata={"source": "transformer.md"}),
    ]
    reranker = CrossEncoderReranker(
        scorer=lambda query, doc: 10.0 if "attention" in doc.lower() else 1.0
    )

    result = reranker.rerank("attention mechanism", docs, top_k=1)

    assert result.status == "ok"
    assert result.documents[0].metadata["source"] == "transformer.md"
    assert result.documents[0].metadata["rerank_score"] == 10.0


def test_cross_encoder_reranker_reports_precise_blocked_reason_without_local_model():
    reranker = CrossEncoderReranker(model_name="local/missing-reranker")

    result = reranker.rerank("query", [Document(page_content="content", metadata={"source": "a.md"})])

    assert result.status == "blocked"
    assert result.documents == []
    assert "local/missing-reranker" in result.blocked_reason


def test_query_transforms_are_independently_callable_without_langgraph():
    query = "Compare RAG and function calling, then explain MCP reuse."

    hyde = hyde_transform(query)
    rewrites = multi_query_expand(query, n=3)
    subquestions = decompose_query(query)

    assert query in hyde
    assert len(rewrites) == 3
    assert rewrites[0] == query
    assert any("RAG" in item for item in subquestions)
    assert any("MCP" in item for item in subquestions)
