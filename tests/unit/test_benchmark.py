from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from scripts.benchmark import run_retrieval_benchmark, write_json_output


class KeywordEmbeddings(Embeddings):
    def _embed(self, text: str) -> list[float]:
        lower = text.lower()
        return [
            float("transformer" in lower),
            float("attention" in lower),
            float("rag" in lower),
            1.0,
        ]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


def test_retrieval_benchmark_smoke_reports_dense_and_hybrid_without_metrics():
    docs = [
        Document(
            page_content="Transformer uses multi head attention.",
            metadata={"source": "attention.md", "page": 1},
        ),
        Document(
            page_content="RAG combines retrieval and generation.",
            metadata={"source": "rag.md"},
        ),
    ]

    result = run_retrieval_benchmark(
        docs=docs,
        query="transformer attention",
        retrieval_modes=["dense", "hybrid"],
        top_k=2,
        embedder=KeywordEmbeddings(),
    )

    assert result["status"] == "ok"
    assert result["query"] == "transformer attention"
    assert set(result["retrieval"].keys()) == {"dense", "hybrid"}
    assert result["retrieval"]["dense"]["top_k"] == 2
    assert result["retrieval"]["hybrid"]["top_k"] == 2
    assert result["metrics"]["recall_at_5"] == "pending_labeled_eval"


def test_benchmark_can_persist_json_output(tmp_path):
    output = tmp_path / "results" / "benchmark.json"
    payload = {"status": "ok", "retrieval": {"dense": {"returned": 1}}}

    write_json_output(payload, output)

    assert output.exists()
    assert '"status": "ok"' in output.read_text(encoding="utf-8")
