# KnowledgeOps · 开发执行文档

> 本文用于把项目 1 的完整代码实现目标落成可执行、可审计的 `/goal` 提示词。  
> 项目定位：生产导向研究型 Knowledge Agent 系统，而不是普通 RAG 问答机器人。

## 适用场景

当需要让 Codex CLI 0.128+ 使用 `/goal` 长跑实现项目 1 时，复制下方命令使用。

这份 goal 的设计重点：

- 先读项目规划文档并回报 counts，避免未读全就开始改代码。
- 用 Sprint 1-5 checklist 约束“完整实现”的边界。
- 把验收条件落到文件、命令、接口和测试结果上。
- 把新增依赖、真实凭据、外部服务阻塞等情况设为停止条件。

## `/goal` Prompt

```text
/goal 严格按照当前仓库 KnowledgeOps 的项目1规划文档，实现可投递成熟版的生产导向研究型 Knowledge Agent 系统；目标是把现有骨架从 TODO/NotImplemented 状态推进到 README、docs/architecture.md、notes/day7/sprint_backlog.md 中定义的 Sprint 1-5 核心能力可运行、可测试、可演示。

First action: 先逐字读取以下文件，然后回报计数，不要修改任何文件：
  - README.md
  - docs/architecture.md
  - docs/api.md
  - docs/benchmark.md
  - notes/day7/sprint_backlog.md
  - C:\Users\sundewang\Desktop\MTS_AD\项目\AI应用开发求职冲刺\README.md
  - C:\Users\sundewang\Desktop\MTS_AD\项目\AI应用开发求职冲刺\02-7月底冲刺计划-两段式作战.md
  - C:\Users\sundewang\Desktop\MTS_AD\项目\AI应用开发求职冲刺\W1-知识速成周\Day7-周日-5月24-项目1顶层设计.md
  - pyproject.toml
  - src/**/*.py
  - tests/**/*.py
报告：
  1. notes/day7/sprint_backlog.md 中 Sprint 1-5 的 checklist 总数，以及按 Sprint 分组的数量；
  2. 当前源码中 NotImplementedError / TODO Sprint / 501 Not implemented 的数量和文件分布；
  3. 当前 tests/ 下实际测试用例数量；
  4. 你识别到的项目硬约束数量；
  5. 你建议本次实现拆成的阶段数。
等我确认后再开始实现。

Scope:
  - 可修改：src/、tests/、scripts/、eval/、docs/api.md、docs/benchmark.md、README.md、.env.example、Dockerfile、docker-compose.yml、pyproject.toml、uv.lock（如确有依赖变动）。
  - 可新增：tests/unit/、tests/integration/、scripts/、eval/、frontend/ 下为完成 Sprint 1-5 必需的文件。
  - 重点实现范围：
    1. Ingest：PDF / Word / HTML loader、splitter、embedder；
    2. Retrieval：dense baseline、BM25、RRF hybrid、rerank、HyDE / multi-query / decomposition、ContextBuilder；
    3. ArtifactStore：plan / evidence / synthesis / final_report 可落盘复盘；
    4. Agents：Planner、RetrievalOrchestrator、Synthesizer、Reporter、Verifier、LangGraph 主图端到端可运行；
    5. Guardrails：prompt injection 检测、structured output、citation enforcement / verification；
    6. Policy：ComplexityClassifier、ModelRouter、Cache / Retry / Fallback 的最小可运行实现；
    7. API：/health、/api/v1/query、/api/v1/ingest、/api/v1/query/stream、/api/v1/feedback；
    8. MCP：search_knowledge、summarize_documents、artifact metadata 相关工具可被 MCP client 调用；
    9. Observability：trace_id、latency、token/cost placeholder、tool success、fallback rate、citation hit rate；
    10. Eval / benchmark：RAGAS 或可替代的本地评估脚本、Locust 或可替代压测脚本、benchmark 文档填入可复现实验命令。
  - 不要求实现：真实云部署、真实 B 站 Demo 上传、真实投递动作、真实生产 API Key 管理平台。
  - 前端如实现，优先 Streamlit 最小 Demo；不要把大量时间花在 Next.js UI 精修。

Constraints:
  - 这是 Python 3.11 + uv + FastAPI + LangChain/LangGraph + MCP 项目；优先使用 pyproject.toml 已声明依赖。
  - 不要默认把所有请求打到最高价模型；必须保留模型分层与成本治理设计。
  - Agent 只负责认知决策；ingest / retrieval / rerank / citation / eval / cache / rate limit 保持 deterministic service，不要把全部逻辑塞进 Agent prompt。
  - 不要引入重型新依赖，除非某个 Sprint checklist 无法用现有依赖完成；如必须新增依赖，先停止并说明依赖名、用途、替代方案。
  - 不要提交 .env、API key、真实凭据、data/ 大文件、模型权重、数据库文件或 artifacts 运行产物。
  - 不要删除 notes/ 下的学习笔记；可以引用它们，但不要重写学习计划。
  - 不要为了让测试通过而跳过测试：禁止新增 pytest skip / xfail，禁止删除测试断言，禁止把失败测试改成空测试。
  - 不要把 README 里的 5 个量化指标写成“已达标”，除非 eval/benchmark 命令真实跑出结果；没有真实结果时写 baseline / placeholder / 待测，并给出复现命令。
  - 代码保持简单可解释，避免过度抽象；新模块要有对应单元测试或集成测试。
  - Windows 路径与 PowerShell 环境要可用；命令优先用 uv run。
  - 如果修改 pyproject.toml，必须同步 lock 文件或明确说明无法同步的原因。

Done when:
  1. notes/day7/sprint_backlog.md 中 Sprint 1-5 的每个与代码实现相关的 checklist 都有对应实现或明确标记为“非代码交付/需人工完成”，最终 summary 用表格列出：Sprint / checklist / 状态 / 对应文件路径。
  2. 源码中所有核心运行路径不再抛出 NotImplementedError：至少覆盖 src/ingest、src/retrieval、src/agents、src/guardrails、src/api、src/mcp、src/policy.py、src/observability；最终 summary 列出剩余 NotImplementedError 数量，必须为 0，除非属于明确非目标范围。
  3. `uv run pytest -q` 退出码 0；粘贴 test summary；skipped / xfailed 新增数量必须为 0。
  4. `uv run ruff check .` 退出码 0；如项目没有 ruff 配置，也必须使用 pyproject.toml 默认规则运行并修复高置信问题。
  5. `uv run mypy src` 退出码 0，或如果第三方库类型缺失导致无法全绿，必须列出仅由第三方 stubs 引起的错误并确保项目自有代码没有明显类型错误。
  6. `uv run uvicorn src.main:app --host 127.0.0.1 --port 8000` 能启动；`GET /health` 返回 200；`POST /api/v1/query` 对一个最小问题返回结构化 QueryResponse，包含 answer / citations 或 evidence / trace_id。
  7. 至少新增覆盖以下模块的测试：loader、splitter、RRF hybrid、ContextBuilder、ArtifactStore、Planner、Reporter citation、API query；每类至少 1 个行为测试。
  8. MCP server 中 search_knowledge 与 summarize_documents 不再是占位异常；至少能在无真实向量库时使用本地 fallback/mockable service 返回确定格式结果，并有测试覆盖。
  9. eval/ 或 scripts/ 下存在可运行的 baseline/evaluation/benchmark 脚本；docs/benchmark.md 记录命令、数据假设、当前 baseline 结果或待测原因，不编造 Recall@5/P95/成本指标。
  10. README.md 和 docs/api.md 与实际接口保持同步：启动命令、API schema、MCP 配置、测试命令、已实现/未实现能力不能互相矛盾。
  11. 最终 `git diff --stat` 和 summary 按文件列出修改内容；说明哪些交付物属于代码完成，哪些仍需要人工动作（Demo 视频、真实云部署、真实投递等）。

Stop if:
  - First action 读取文档后发现 Sprint checklist 数量无法确定，或项目1文档之间对核心目标互相冲突。
  - 实现需要新增依赖、升级 Python 版本、替换核心框架，或需要执行 `uv add` / `pip install` 才能继续。
  - 需要真实 API key、外部付费模型、云服务账号、MCP 客户端 GUI 操作、Docker daemon 或数据库服务才能完成某个验收项；先停下并给出本地 fallback 方案。
  - 现有测试开始失败，这是 regression；不要通过改测试、skip、xfail、删除断言来解决。
  - git status 显示 .env、密钥、data/、artifacts/、模型权重、数据库文件进入待提交范围。
  - 为了实现功能需要大幅重写 notes/ 学习文档，或删除当前架构文档中的核心定位。
  - 单次 diff 超过 3000 行且没有阶段性测试通过记录；先停下汇报拆分方案。
  - uvicorn 服务无法启动且错误不是显式缺少用户私密配置造成的。
  - 发现 README 宣称的能力无法在代码中实现或验证；不要编造结果，标记为未完成并说明原因。

```

## 拆分建议

如果单次 `/goal` 过大，优先按下面顺序拆成 5 个 goal：

1. Sprint 1：最小研究闭环 + 证据管线。
2. Sprint 2：混合检索 + 上下文工程。
3. Sprint 3：LangGraph Agent 图 + MCP 工具层。
4. Sprint 4：Policy Layer + LLMOps + Guardrails。
5. Sprint 5：SSE / Demo / benchmark / README 定稿。

拆分时仍保留相同的 `First action` 读文档机制，但 Scope 和 Done when 只保留对应 Sprint 的 checklist。
