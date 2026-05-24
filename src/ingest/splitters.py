"""文本分块策略

Sprint 1 baseline：RecursiveCharacterTextSplitter，chunk_size=500 / overlap=50（Day4 验证）
Sprint 2 优化：按文档类型差异化（论文 300 / 叙事 800 / FAQ 一条一块）+ 语义分块（可选）
"""
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_recursive(
    docs: list[Document],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[Document]:
    """递归字符分块（baseline）"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_documents(docs)


def split_by_doc_type(docs: list[Document]) -> list[Document]:
    """按文档类型差异化分块（Sprint 2）"""
    # TODO Sprint 2:
    #   - 论文 / 技术文档 → chunk_size 300-500
    #   - 叙事 / 新闻 → chunk_size 800-1500
    #   - FAQ / 结构化 → 一条一块，不切
    raise NotImplementedError
