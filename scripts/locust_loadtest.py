"""Locust 压测脚本（Sprint 5 任务）

跑法：
  uv run locust -f scripts/locust_loadtest.py --host http://localhost:8000

目标：100 QPS 持续 5 分钟，P95 延迟 < 3s（README 里的指标）
"""
from locust import HttpUser, task, between


class KnowledgeOpsUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def query_qa(self):
        self.client.post("/api/v1/query", json={
            "question": "什么是 RAG？",
            "intent": "qa",
        })

    # TODO Sprint 5: 加更多场景（summary / report / 长尾问题 / 注入攻击）
