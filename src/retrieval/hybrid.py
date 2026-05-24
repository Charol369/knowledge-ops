"""混合检索（Hybrid）：稠密 + 稀疏融合

融合算法：RRF (Reciprocal Rank Fusion)
  score(d) = sum(1 / (k + rank_i(d)))  for each retriever i
  k 通常取 60，对低排名 chunk 惩罚足够大

为什么用 RRF 而不是分数加权：RRF 不依赖各 retriever 的绝对分数尺度，
更稳健。OpenAI / Anthropic / 阿里通义的 hybrid 都默认 RRF。

Sprint 2 任务。
"""
from langchain_core.documents import Document


def reciprocal_rank_fusion(
    rank_lists: list[list[Document]],
    k: int = 60,
    top_n: int = 10,
) -> list[Document]:
    """RRF 融合多个 retriever 的 ranking"""
    # TODO Sprint 2:
    #   1. 给每个 Document 用 page_content 哈希做 key
    #   2. 累加 RRF score
    #   3. 按累计分数排序返回 top_n
    raise NotImplementedError
