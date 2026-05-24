"""RAGAS 评估脚本（Sprint 2 末交付）

跑法：uv run python eval/run_ragas.py
读 eval/testset.jsonl 的 (question, ground_truth) → 跑 RAG pipeline → RAGAS 算指标

输出：eval/reports/{timestamp}.json 含 4 个核心指标：
  - faithfulness（答案是否忠于 context）
  - answer_relevancy（答案与问题相关性）
  - context_precision（检索到的 context 是否真的有用）
  - context_recall（检索是否覆盖了 ground truth 需要的信息）
"""

# TODO Sprint 2:
# from ragas import evaluate
# from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
# from datasets import Dataset
# ...

if __name__ == "__main__":
    raise NotImplementedError("Sprint 2 任务")
