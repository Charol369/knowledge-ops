"""稀疏检索（BM25）。"""
import re

from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

QUERY_STOPWORDS = {
    "a",
    "about",
    "all",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "does",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
    "you",
    "your",
}


def _tokenize(text: str) -> list[str]:
    """Small local tokenizer for English terms and CJK characters without new deps."""
    lower = text.lower()
    latin_terms = re.findall(r"[a-z0-9_]+", lower)
    cjk_chars = re.findall(r"[\u4e00-\u9fff]", lower)
    return latin_terms + cjk_chars


def tokenize_query(text: str) -> list[str]:
    """Tokenize user queries without letting prompt boilerplate dominate BM25."""
    tokens = []
    seen: set[str] = set()
    for token in [
        token
        for token in _tokenize(text)
        if len(token) > 1 and token not in QUERY_STOPWORDS
    ]:
        if token in seen:
            continue
        seen.add(token)
        tokens.append(token)
    return tokens or _tokenize(text)


class BM25Retriever:
    """BM25 稀疏检索器，基于 rank-bm25 包"""

    def __init__(self, docs: list[Document]):
        if not docs:
            raise ValueError("Cannot build a BM25 retriever from an empty document list.")
        missing_source = [doc for doc in docs if "source" not in doc.metadata]
        if missing_source:
            raise ValueError("BM25 evidence documents must include source metadata.")
        self.docs = docs
        self.tokenized_docs = [_tokenize(doc.page_content) for doc in docs]
        self.index = BM25Okapi(self.tokenized_docs)

    def search(self, query: str, k: int = 10) -> list[Document]:
        if k <= 0:
            return []
        tokens = tokenize_query(query)
        if not tokens:
            return []
        scores = self.index.get_scores(tokens)
        token_set = set(tokens)
        ranked = sorted(
            enumerate(scores),
            key=lambda item: (
                len(token_set.intersection(self.tokenized_docs[item[0]])),
                float(item[1]),
                -item[0],
            ),
            reverse=True,
        )
        return [self.docs[index] for index, _ in ranked[:k]]
