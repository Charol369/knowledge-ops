"""批量入库脚本（Sprint 1 末交付）

用法：uv run python scripts/ingest_pdfs.py data/pdfs/

流程：
  1. 遍历目录 → 收集所有 .pdf / .docx / .html
  2. 调用 src.ingest.loaders 加载
  3. 调用 src.ingest.splitters 分块
  4. 调用 src.ingest.embedder + src.retrieval.dense 入库
  5. 打印统计：处理了 N 个文件 / M 个 chunks / 耗时 Ts
"""
import sys

# TODO Sprint 1:
# from pathlib import Path
# from src.ingest.loaders import load_directory
# from src.ingest.splitters import split_recursive
# from src.ingest.embedder import get_embedder
# from src.retrieval.dense import build_index

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/ingest_pdfs.py <directory>")
        sys.exit(1)
    raise NotImplementedError("Sprint 1 任务")
