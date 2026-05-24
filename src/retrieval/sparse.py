"""稀疏检索（BM25）

为什么需要：稠密向量擅长语义匹配，但 **关键词类查询**（人名 / 型号 / 法条号 /
专业术语）稀疏 BM25 反而更准。Hybrid 是 RAG baseline 必备。

Sprint 2 任务。
"""
from langchain_core.documents import Document


class BM25Retriever:
    """BM25 稀疏检索器，基于 rank-bm25 包"""

    def __init__(self, docs: list[Document]):
        # TODO Sprint 2: 用 rank-bm25 的 BM25Okapi 建索引
        # 注意中文需要 jieba 分词，英文用 simple split
        raise NotImplementedError

    def search(self, query: str, k: int = 10) -> list[Document]:
        # TODO Sprint 2: 返回 top-k chunks
        raise NotImplementedError
