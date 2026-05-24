"""Benchmark 脚本：对比不同配置的检索质量（Sprint 2-3 任务）

对比维度：
  - 嵌入模型（bge-small vs bge-m3 vs OpenAI text-embedding-3-small）
  - chunk_size（200 vs 500 vs 1000）
  - 检索策略（dense-only vs hybrid vs hybrid+rerank）
  - Top-K（3 vs 5 vs 10 vs 20+rerank-5）

输出：表格对比 + 推荐配置
"""

# TODO Sprint 2: 实现 + 跑出基线数据填到 docs/benchmark.md
