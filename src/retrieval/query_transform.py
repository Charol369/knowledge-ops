"""查询变换：HyDE / Multi-Query / Query Decomposition

为什么需要：用户的原始 query 往往**口语化**或**信息不足**，直接拿去检索召回率低。
查询变换让 LLM 先"翻译"成更检索友好的 N 个变体。

技术：
  - HyDE (Hypothetical Document Embeddings)：让 LLM 写一段"假答案"，用假答案的
    embedding 去检索（往往比 query 本身更接近真正答案的 embedding）
  - Multi-Query：用 LLM 生成 query 的 3-5 个改写版本，分别检索后融合
  - Decomposition：把复杂多跳问题拆成子问题分别检索

Sprint 2 任务。
"""


def hyde_transform(query: str, llm) -> str:
    """HyDE：让 LLM 生成一段假答案用于检索"""
    # TODO Sprint 2: prompt = "Write a passage that would answer: {query}"
    raise NotImplementedError


def multi_query_expand(query: str, llm, n: int = 3) -> list[str]:
    """生成 N 个查询改写"""
    # TODO Sprint 2: prompt = "Generate {n} different rewrites of: {query}"
    raise NotImplementedError
