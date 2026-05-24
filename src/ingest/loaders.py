"""数据加载层：PDF / Word / 网页 → LangChain Document

Sprint 1 任务：实现 PDF / Word / HTML 三种 loader。
统一返回 List[Document]，metadata 至少含 source（文件名 / URL）+ page_no（如适用）。
"""
from pathlib import Path
from langchain_core.documents import Document


def load_pdf(path: str | Path) -> list[Document]:
    """加载 PDF → List[Document]，每页一个 Document"""
    # TODO Sprint 1: 用 PyPDFLoader（Day4 已验证）
    # 注意：metadata 必须含 source + page，方便后续 citation 回溯
    raise NotImplementedError


def load_docx(path: str | Path) -> list[Document]:
    """加载 Word 文档 → List[Document]"""
    # TODO Sprint 1: 用 python-docx 解析段落，每个 heading 段作为一个 Document
    raise NotImplementedError


def load_url(url: str) -> list[Document]:
    """加载网页 → List[Document]"""
    # TODO Sprint 1: requests + beautifulsoup4 抽正文，过滤导航/侧栏/广告
    raise NotImplementedError


def load_directory(directory: str | Path, glob: str = "**/*") -> list[Document]:
    """批量加载一个目录下所有支持的文档"""
    # TODO Sprint 1: 按文件后缀分发到 load_pdf / load_docx；保留目录结构到 metadata
    raise NotImplementedError
