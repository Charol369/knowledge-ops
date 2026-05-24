"""自定义业务指标（Sprint 4 任务）

Langfuse 追踪 LLM 调用的延迟/token/cost，但**业务级指标**需要自己埋：
  - 用户提问的意图分布（qa/summary/report）
  - 检索召回率（每个 query 实际用了多少 chunks）
  - 引用准确率（citation 是否真的指向 context chunk）
  - 用户反馈率（点赞 / 点踩 / 人工审核标记）

Sprint 4 用 Prometheus / OpenTelemetry metrics 上报。
"""

# TODO Sprint 4: from opentelemetry import metrics
# TODO Sprint 4: 定义 Counter / Histogram / Gauge
