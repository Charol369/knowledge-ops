"""重排（Rerank）：用 Cross-Encoder 把粗排的 Top-K 精排

为什么需要：Bi-encoder（embedding）独立编码 query / doc 余弦相似度，速度快但精度低；
Cross-encoder 把 (query, doc) pair 一起喂模型，精度高但慢——所以**先粗排再精排**。

经典 pipeline：retriever 召回 20 → rerank 取 top 5 → 喂 LLM

Sprint 2 任务，模型用 BAAI/bge-reranker-v2-m3。
"""
from langchain_core.documents import Document


class CrossEncoderReranker:
    """基于 sentence-transformers CrossEncoder 的 reranker"""

    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        # TODO Sprint 2: 用 sentence_transformers.CrossEncoder 加载
        raise NotImplementedError

    def rerank(self, query: str, docs: list[Document], top_k: int = 5) -> list[Document]:
        # TODO Sprint 2:
        #   1. pairs = [(query, doc.page_content) for doc in docs]
        #   2. scores = self.model.predict(pairs)
        #   3. 按 score 排序，取 top_k
        raise NotImplementedError
