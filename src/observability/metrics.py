"""自定义业务指标。

Langfuse 负责模型追踪；这里负责项目级业务指标：
- complexity 分布
- model tier 使用占比
- tool call success rate
- fallback rate
- citation verification hit rate
- user feedback / human review rate
"""

# TODO Sprint 4: from opentelemetry import metrics
# TODO Sprint 4: 定义 Counter / Histogram / Gauge
# TODO Sprint 4: 统一埋点接口，避免业务代码直接依赖具体监控 SDK
