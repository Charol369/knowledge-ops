"""文本分块策略

Sprint 1 baseline：RecursiveCharacterTextSplitter，chunk_size=500 / overlap=50（Day4 验证）
Sprint 2 优化：按文档类型差异化（论文 300 / 叙事 800 / FAQ 一条一块）+ 语义分块（可选）
"""
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_recursive(
    docs: list[Document],
    chunk_size: int = 500,
    overlap: int = 50,
    chunk_overlap: int | None = None,
) -> list[Document]:
    """递归字符分块（baseline）"""
    effective_overlap = overlap if chunk_overlap is None else chunk_overlap
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=effective_overlap,
    )
    return splitter.split_documents(docs)


def split_by_doc_type(docs: list[Document]) -> list[Document]:
    """按文档类型差异化分块，保留 recursive splitter 作为确定性实现。"""
    chunks: list[Document] = []
    for doc in docs:
        source = str(doc.metadata.get("source", "")).lower()
        content = doc.page_content.lower()
        if _looks_like_faq(source, content):
            chunks.append(doc)
        elif source.endswith((".pdf", ".md", ".rst")):
            chunks.extend(split_recursive([doc], chunk_size=400, overlap=50))
        else:
            chunks.extend(split_recursive([doc], chunk_size=800, overlap=80))
    return chunks


def _looks_like_faq(source: str, content: str) -> bool:
    return "faq" in source or "q:" in content or "question:" in content
