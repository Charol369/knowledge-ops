"""Locust load-test entrypoint for manual Sprint 5 performance validation.

跑法：
  uv run locust -f scripts/locust_loadtest.py --host http://localhost:8000

目标：100 QPS 持续 5 分钟，P95 延迟 < 3s。
本脚本不会自动证明目标达成；必须在真实运行后记录 Locust 输出。
"""
from locust import HttpUser, task, between


class KnowledgeOpsUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def query(self):
        self.client.post(
            "/api/v1/query",
            json={
                "question": "Summarize the indexed evidence",
                "thread_id": "locust-query",
            },
        )

    @task
    def query_stream(self):
        self.client.post(
            "/api/v1/query/stream",
            json={
                "question": "Summarize the indexed evidence",
                "thread_id": "locust-stream",
            },
        )

    @task
    def feedback(self):
        self.client.post(
            "/api/v1/feedback",
            json={
                "trace_id": "locust-feedback",
                "score": 1,
                "source": "locust-loadtest",
            },
        )
