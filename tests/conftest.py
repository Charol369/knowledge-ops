"""单元测试占位（Sprint 1+ 任务）

W1 末骨架：先放一个 conftest.py 共享 fixture。
"""
import os

import pytest


os.environ.setdefault("LLM_SYNTHESIS_ENABLED", "false")


@pytest.fixture
def sample_question():
    return "什么是 RAG？"


# TODO Sprint 1: test_loaders / test_splitters / test_embedder
# TODO Sprint 2: test_dense / test_hybrid / test_rerank
# TODO Sprint 3: test_qa_agent / test_graph
# TODO Sprint 4: test_injection / test_citation
