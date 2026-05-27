"""重排（Rerank）：用 Cross-Encoder 把粗排的 Top-K 精排。"""
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from langchain_core.documents import Document


@dataclass(frozen=True)
class RerankResult:
    status: str
    documents: list[Document]
    blocked_reason: str | None = None


class CrossEncoderReranker:
    """基于 sentence-transformers CrossEncoder 的 reranker"""

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-v2-m3",
        scorer: Callable[[str, str], float] | None = None,
    ):
        self.model_name = model_name
        self.scorer = scorer
        self._model = None

    def rerank(self, query: str, docs: list[Document], top_k: int = 5) -> RerankResult:
        if top_k <= 0 or not docs:
            return RerankResult(status="ok", documents=[])
        missing_source = [doc for doc in docs if "source" not in doc.metadata]
        if missing_source:
            raise ValueError("Rerank candidates must include source metadata.")

        scorer = self.scorer
        if scorer is None:
            model = self._load_local_model()
            if isinstance(model, str):
                return RerankResult(status="blocked", documents=[], blocked_reason=model)
            pairs = [(query, doc.page_content) for doc in docs]
            scores = [float(score) for score in model.predict(pairs)]
        else:
            scores = [float(scorer(query, doc.page_content)) for doc in docs]

        ranked = sorted(
            zip(docs, scores, range(len(docs)), strict=True),
            key=lambda item: (item[1], -item[2]),
            reverse=True,
        )
        result_docs = []
        for doc, score, _ in ranked[:top_k]:
            metadata = dict(doc.metadata)
            metadata["rerank_score"] = score
            result_docs.append(Document(page_content=doc.page_content, metadata=metadata))
        return RerankResult(status="ok", documents=result_docs)

    def _load_local_model(self):
        if self._model is not None:
            return self._model
        model_path = Path(self.model_name)
        if not model_path.exists():
            return (
                "Local CrossEncoder model unavailable: "
                f"{self.model_name}. Provide a local model path or inject a scorer."
            )
        try:
            from sentence_transformers import CrossEncoder
        except Exception as exc:  # pragma: no cover - depends on optional runtime import
            return f"sentence-transformers CrossEncoder unavailable: {exc}"
        try:
            self._model = CrossEncoder(str(model_path))
        except Exception as exc:  # pragma: no cover - model loading is environment-specific
            return f"Local CrossEncoder model load failed for {self.model_name}: {exc}"
        return self._model
