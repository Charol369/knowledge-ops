"""稠密向量检索（Dense Retrieval）

Sprint 1：用 FAISS 跑通（Day4 验证，langchain-milvus 0.3.3 + pymilvus 2.6
在 milvus-lite 模式下有 ConnectionNotExistException bug，详见 notes/day4/NOTES.md）
Sprint 3：切真正的 Milvus standalone (Docker 模式)，不会遇到那个 bug

W1 末骨架：先放 FAISS 实现的接口签名。
"""
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_community.vectorstores import FAISS


def build_index(docs: list[Document], embedder, index_dir: str | None = None) -> VectorStore:
    """从 Document 列表建索引"""
    if not docs:
        raise ValueError("Cannot build a dense index from an empty document list.")
    vectorstore = FAISS.from_documents(docs, embedding=embedder)
    if index_dir is not None:
        vectorstore.save_local(str(index_dir))
    return vectorstore


def load_index(index_dir: str, embedder) -> VectorStore:
    """从磁盘加载已建好的索引"""
    return FAISS.load_local(
        str(index_dir),
        embeddings=embedder,
        allow_dangerous_deserialization=True,
    )


def search(vectorstore: VectorStore, query: str, k: int = 5) -> list[Document]:
    """向量检索 Top-K"""
    results = vectorstore.similarity_search(query, k=k)
    missing_source = [doc for doc in results if "source" not in doc.metadata]
    if missing_source:
        raise ValueError("Dense retrieval returned evidence without source metadata.")
    return results
