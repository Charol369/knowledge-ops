import hashlib
import math
import re

from langchain_core.embeddings import Embeddings

from src.config import settings


class LocalHashEmbeddings(Embeddings):
    """Deterministic local embeddings for Sprint 1 tests and offline smoke runs."""

    def __init__(self, dimensions: int = 64):
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[\w\u4e00-\u9fff]+", text.lower())
        for token in tokens or [text.lower()]:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


def get_embedder(model_name: str | None = None, backend: str = "huggingface") -> Embeddings:
    """统一的 embedder 入口；默认仍优先使用配置中的 bge-m3。"""
    if backend in {"local", "fake", "hash"}:
        return LocalHashEmbeddings()
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(
        model_name=model_name or settings.embed_model,
        encode_kwargs={"normalize_embeddings": True},
    )
