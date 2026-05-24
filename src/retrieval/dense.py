"""稠密向量检索（Dense Retrieval）

Sprint 1：用 FAISS 跑通（Day4 验证，langchain-milvus 0.3.3 + pymilvus 2.6
在 milvus-lite 模式下有 ConnectionNotExistException bug，详见 notes/day4/NOTES.md）
Sprint 3：切真正的 Milvus standalone (Docker 模式)，不会遇到那个 bug

W1 末骨架：先放 FAISS 实现的接口签名。
"""
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore


def build_index(docs: list[Document], embedder) -> VectorStore:
    """从 Document 列表建索引"""
    # TODO Sprint 1: FAISS.from_documents → save_local 持久化
    # TODO Sprint 3: 切 Milvus standalone（docker compose 起服务）
    raise NotImplementedError


def load_index(index_dir: str, embedder) -> VectorStore:
    """从磁盘加载已建好的索引"""
    # TODO Sprint 1: FAISS.load_local(index_dir, embedder, allow_dangerous_deserialization=True)
    raise NotImplementedError


def search(vectorstore: VectorStore, query: str, k: int = 5) -> list[Document]:
    """向量检索 Top-K"""
    # TODO Sprint 1: vectorstore.similarity_search(query, k=k)
    raise NotImplementedError
