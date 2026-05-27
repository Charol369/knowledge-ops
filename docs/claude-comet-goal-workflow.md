# Claude 对话指令：Comet + goal-prompt-builder + Codex /goal 工作流

本文用于保存后续发给 Claude 的指令模板，目标是把 KnowledgeOps 项目 1 的开发流程固定为：

```text
Comet 生成当前 Sprint 的 spec/plan
        ↓
goal-prompt-builder 生成当前 Sprint 专用 Codex /goal
        ↓
Codex /goal 实际执行代码实现、测试、文档更新
```

## 1. 总说明

把下面内容先发给 Claude，用于统一上下文。

```text
我们现在要把 KnowledgeOps 项目开发流程调整为“Comet 规格计划 + goal-prompt-builder 生成 Codex /goal”的组合流程。

请注意：

1. docs/development.md 里的 5 个 Sprint 拆分仍然是主线：
   - Sprint 1：最小研究闭环 + 证据管线
   - Sprint 2：混合检索 + 上下文工程
   - Sprint 3：LangGraph Agent 图 + MCP 工具层
   - Sprint 4：Policy Layer + LLMOps + Guardrails
   - Sprint 5：SSE / Demo / benchmark / README 定稿

2. Comet 不替代 Codex /goal。
   Comet 的职责是：针对每个 Sprint 先生成 spec/plan，明确需求、边界、文件范围、验收条件、测试命令、停止条件。

3. goal-prompt-builder 的职责是：基于 Comet 生成的 spec/plan，再产出一个 Sprint 专用的 Codex /goal 提示词。

4. Codex /goal 的职责是：实际执行代码修改、测试、文档更新和最终汇报。

5. 每个 Sprint 都必须独立闭环：
   - 先 /comet 生成 spec/plan
   - 再用 goal-prompt-builder 生成该 Sprint 的 /goal
   - 再让 Codex 执行该 /goal
   - Sprint 验收通过后，才进入下一个 Sprint

6. 不要一次性把 Sprint 1-5 全部交给 Codex 实现。
   全量大 goal 只作为总控参考，不作为首选执行方式。

7. 不要把 Comet、goal-prompt-builder 和 Codex /goal 混成一个步骤。
   Comet 只负责当前 Sprint 的 spec/plan；goal-prompt-builder 再把 spec/plan 转成当前 Sprint 专用 /goal；Codex 最后执行这个 /goal。

8. 生成 Codex /goal 时，不要附加 token budget / use limit，避免任务在未完成前因预算上限提前停止。
```

## 2. Sprint 1：让 Claude 用 Comet 生成 spec/plan

如果 Claude Code 已经加载项目级 Comet skill，优先发送下面这条。

```text
/comet "基于当前项目 C:\Users\sundewang\Code\knowledge-ops，为 KnowledgeOps Sprint 1 生成 Comet spec/plan。只覆盖 Sprint 1：最小研究闭环 + 证据管线。读取 docs/development.md、README.md、docs/architecture.md、docs/api.md、docs/benchmark.md、notes/day7/sprint_backlog.md，以及桌面项目资料中的项目1规划文档。不要写代码。spec/plan 必须能后续转换为 Codex /goal，包含 Objective、Scope、Constraints、Done when、Stop if、First action 读文档报 counts、测试命令、验收文件路径、Sprint 1 checklist 映射。Scope 禁止包含 Sprint 2-5。如果 checklist 无法确定，停止并说明缺失信息。"
```

如果 Claude 没有识别 `/comet`，发送下面的普通指令。

```text
请基于当前项目 C:\Users\sundewang\Code\knowledge-ops，使用 Comet 工作流为 Sprint 1 生成 spec/plan。

项目资料包括：
- C:\Users\sundewang\Code\knowledge-ops\docs\development.md
- C:\Users\sundewang\Code\knowledge-ops\README.md
- C:\Users\sundewang\Code\knowledge-ops\docs\architecture.md
- C:\Users\sundewang\Code\knowledge-ops\docs\api.md
- C:\Users\sundewang\Code\knowledge-ops\docs\benchmark.md
- C:\Users\sundewang\Code\knowledge-ops\notes\day7\sprint_backlog.md
- C:\Users\sundewang\Desktop\MTS_AD\项目\AI应用开发求职冲刺\README.md
- C:\Users\sundewang\Desktop\MTS_AD\项目\AI应用开发求职冲刺\02-7月底冲刺计划-两段式作战.md
- C:\Users\sundewang\Desktop\MTS_AD\项目\AI应用开发求职冲刺\W1-知识速成周\Day7-周日-5月24-项目1顶层设计.md

本次只处理 Sprint 1：最小研究闭环 + 证据管线。

目标：
1. 不写代码。
2. 只生成 Comet spec/plan。
3. spec/plan 必须能后续转换为 Codex /goal。
4. Scope 只能覆盖 Sprint 1 checklist，不能包含 Sprint 2-5。
5. plan 必须明确：
   - Objective
   - Scope
   - Constraints
   - Done when
   - Stop if
   - 需要读取的文件
   - 可修改文件范围
   - 必须运行的验证命令
   - 预期新增/修改的测试
   - 与 Sprint 1 checklist 的映射关系
6. 保留 First action 读文档 + 报 counts + 等确认机制。
7. 如果 Sprint 1 checklist 无法从文档中明确识别，请停止并列出缺失信息，不要猜测。
```

## 3. Sprint 1：基于 spec/plan 生成 Codex /goal

等 Claude 完成 Sprint 1 的 Comet spec/plan 后，再发送下面内容。

```text
确认以上修订结果。现在请基于已修订的 Sprint 1 Comet spec/plan，使用 goal-prompt-builder 为 Codex 生成 Sprint 1 专用 /goal。

严格要求：

1. 只覆盖 Sprint 1：Minimal Research Loop + Evidence Pipeline。
2. 不包含 Sprint 2-5 的任何实现项。
3. Sprint 1 Planner 必须是 2-4 个子任务，不要写 2-5。
4. /api/v1/feedback 不属于 Sprint 1，不要包含。
5. 不实现 hybrid retrieval、BM25、RRF、rerank、HyDE、Multi-Query、Query Decomposition、Context Builder。
6. 不实现 LangGraph 主图、MCP 工具层、/api/v1/query。
7. 不实现 auth、rate limit、observability hardening、Langfuse、PostgresSaver、model router。
8. 不实现 SSE、Streamlit Demo、feedback endpoint、cloud deployment、Demo 视频、简历段落。
9. benchmark 只能记录实际运行过的本地初始技术 baseline，例如 dense retrieval 和 CLI pipeline latency；没有真实运行结果时只能写 pending / placeholder / blocked reason，不能编造指标。
10. 不要添加任何 token budget / use limit。

必须保留 First action：
- 先读取项目核心文档和 Sprint 1 相关 Comet spec/plan。
- 报告 Sprint 1 checklist 数量。
- 报告当前源码中 TODO / NotImplementedError / 501 Not implemented 数量和文件分布。
- 报告当前 tests 数量。
- 报告 Sprint 1 可执行阶段拆分。
- 等我确认后再开始实现。

/goal 必须包含：
- Objective
- Scope
- Constraints
- Done when
- Stop if
- First action
- 可修改文件范围
- 必须运行的验证命令
- 最终 summary 要求

Stop if 必须包含：
   - 需要新增依赖
   - 需要真实 API key
   - 需要外部付费模型
   - 需要云服务或 Docker daemon
   - 当前测试出现 regression
   - diff 超过合理范围且没有阶段性测试记录

输出最终可直接复制到 Codex CLI 的 /goal 文本。
```

## 4. 审查 Claude 生成的 /goal（当前 Sprint 通用）

如果 Claude 已经生成了当前 Sprint 的 `/goal`，继续发下面内容，让它自查并直接修订。

```text
请审查你刚生成的当前 Sprint /goal，按 goal-prompt-builder 标准评估是否可审计。

请逐项检查：
1. Objective 是否单一明确。
2. Scope 是否只覆盖当前 Sprint checklist。
3. Constraints 是否阻止不必要依赖、真实凭据、外部服务和过度抽象。
4. Done when 是否全部可验证。
5. Stop if 是否足以防止任务跑偏。
6. First action 是否要求读文档、报 counts、等确认。
7. 是否明确测试命令和验收文件。
8. 是否存在任何越界到其他 Sprint 的内容。
9. 是否适合 Codex /goal continuation 审计。
10. 如果需要修改前序 Sprint 文件，是否明确限制为与当前 Sprint 集成直接相关的最小兼容改动。

如果发现问题，请直接修订 /goal，不要只给建议。
```

## 5. Sprint 2-5：生成 Comet spec/plan

后续每个 Sprint 使用对应文本块，不需要手动替换占位符。每次只发送一个 Sprint 的指令，等该 Sprint 通过验收后，再进入下一个 Sprint。

### Sprint 2：混合检索 + 上下文工程

```text
请基于当前项目 C:\Users\sundewang\Code\knowledge-ops，使用 Comet 工作流为 Sprint 2 生成 spec/plan。

本次只处理 Sprint 2：混合检索 + 上下文工程。

必须读取：
- docs/development.md
- README.md
- docs/architecture.md
- docs/api.md
- docs/benchmark.md
- notes/day7/sprint_backlog.md
- C:\Users\sundewang\Desktop\MTS_AD\项目\AI应用开发求职冲刺\README.md
- C:\Users\sundewang\Desktop\MTS_AD\项目\AI应用开发求职冲刺\02-7月底冲刺计划-两段式作战.md
- C:\Users\sundewang\Desktop\MTS_AD\项目\AI应用开发求职冲刺\W1-知识速成周\Day7-周日-5月24-项目1顶层设计.md

要求：
1. 不写代码，只生成 Comet spec/plan。
2. Scope 只覆盖 Sprint 2，禁止包含 Sprint 1、Sprint 3、Sprint 4、Sprint 5 的新增实现项。
3. 明确 Objective、Scope、Constraints、Done when、Stop if。
4. 明确需要读取的文件、可修改文件范围、测试命令、验收文件路径。
5. 明确 Sprint 2 checklist 到实现任务的映射关系。
6. 保留 First action 读文档 + 报 counts + 等确认机制。
7. 如果 Sprint 2 依赖 Sprint 1 未完成，请停止并列出依赖，不要跳过。
8. 输出的 spec/plan 必须能后续转换为 Codex /goal。
9. Sprint 2 重点应围绕 BM25、RRF hybrid、rerank、HyDE、multi-query、query decomposition、ContextBuilder、artifact-to-context、RAGAS/eval 准备和相关 ADR。
```

### Sprint 3：LangGraph Agent 图 + MCP 工具层

```text
请基于当前项目 C:\Users\sundewang\Code\knowledge-ops，使用 Comet 工作流为 Sprint 3 生成 spec/plan。

本次只处理 Sprint 3：LangGraph Agent 图 + MCP 工具层。

必须读取：
- docs/development.md
- README.md
- docs/architecture.md
- docs/api.md
- docs/benchmark.md
- notes/day7/sprint_backlog.md
- C:\Users\sundewang\Desktop\MTS_AD\项目\AI应用开发求职冲刺\README.md
- C:\Users\sundewang\Desktop\MTS_AD\项目\AI应用开发求职冲刺\02-7月底冲刺计划-两段式作战.md
- C:\Users\sundewang\Desktop\MTS_AD\项目\AI应用开发求职冲刺\W1-知识速成周\Day7-周日-5月24-项目1顶层设计.md

要求：
1. 不写代码，只生成 Comet spec/plan。
2. Scope 只覆盖 Sprint 3，禁止包含 Sprint 1、Sprint 2、Sprint 4、Sprint 5 的新增实现项。
3. 明确 Objective、Scope、Constraints、Done when、Stop if。
4. 明确需要读取的文件、可修改文件范围、测试命令、验收文件路径。
5. 明确 Sprint 3 checklist 到实现任务的映射关系。
6. 保留 First action 读文档 + 报 counts + 等确认机制。
7. 如果 Sprint 3 依赖 Sprint 1 或 Sprint 2 未完成，请停止并列出依赖，不要跳过。
8. 输出的 spec/plan 必须能后续转换为 Codex /goal。
9. Sprint 3 重点应围绕 LangGraph 主图、Planner / RetrievalOrchestrator / Synthesizer / Reporter / Verifier、artifact state、MCP search_knowledge、MCP summarize_documents、MCP client 配置和图级集成测试。
```

### Sprint 4：Policy Layer + LLMOps + Guardrails

```text
请基于当前项目 C:\Users\sundewang\Code\knowledge-ops，使用 Comet 工作流为 Sprint 4 生成 spec/plan。

本次只处理 Sprint 4：Policy Layer + LLMOps + Guardrails。

必须读取：
- docs/development.md
- README.md
- docs/architecture.md
- docs/api.md
- docs/benchmark.md
- notes/day7/sprint_backlog.md
- C:\Users\sundewang\Desktop\MTS_AD\项目\AI应用开发求职冲刺\README.md
- C:\Users\sundewang\Desktop\MTS_AD\项目\AI应用开发求职冲刺\02-7月底冲刺计划-两段式作战.md
- C:\Users\sundewang\Desktop\MTS_AD\项目\AI应用开发求职冲刺\W1-知识速成周\Day7-周日-5月24-项目1顶层设计.md

要求：
1. 不写代码，只生成 Comet spec/plan。
2. Scope 只覆盖 Sprint 4，禁止包含 Sprint 1、Sprint 2、Sprint 3、Sprint 5 的新增实现项。
3. 明确 Objective、Scope、Constraints、Done when、Stop if。
4. 明确需要读取的文件、可修改文件范围、测试命令、验收文件路径。
5. 明确 Sprint 4 checklist 到实现任务的映射关系。
6. 保留 First action 读文档 + 报 counts + 等确认机制。
7. 如果 Sprint 4 依赖 Sprint 1、Sprint 2 或 Sprint 3 未完成，请停止并列出依赖，不要跳过。
8. 输出的 spec/plan 必须能后续转换为 Codex /goal。
9. Sprint 4 重点应围绕 ComplexityClassifier、ModelRouter、Cache / Retry / Fallback、Langfuse 或本地可替代观测方案、trace_id、业务指标、injection 检测、Unicode 归一化、持久化 memory、rate limit 和 API key 鉴权。
```

### Sprint 5：SSE / Demo / benchmark / README 定稿

```text
请基于当前项目 C:\Users\sundewang\Code\knowledge-ops，使用 Comet 工作流为 Sprint 5 生成 spec/plan。

本次只处理 Sprint 5：SSE / Demo / benchmark / README 定稿。

必须读取：
- docs/development.md
- README.md
- docs/architecture.md
- docs/api.md
- docs/benchmark.md
- notes/day7/sprint_backlog.md
- C:\Users\sundewang\Desktop\MTS_AD\项目\AI应用开发求职冲刺\README.md
- C:\Users\sundewang\Desktop\MTS_AD\项目\AI应用开发求职冲刺\02-7月底冲刺计划-两段式作战.md
- C:\Users\sundewang\Desktop\MTS_AD\项目\AI应用开发求职冲刺\W1-知识速成周\Day7-周日-5月24-项目1顶层设计.md

要求：
1. 不写代码，只生成 Comet spec/plan。
2. Scope 只覆盖 Sprint 5，禁止包含 Sprint 1、Sprint 2、Sprint 3、Sprint 4 的新增实现项。
3. 明确 Objective、Scope、Constraints、Done when、Stop if。
4. 明确需要读取的文件、可修改文件范围、测试命令、验收文件路径。
5. 明确 Sprint 5 checklist 到实现任务的映射关系。
6. 保留 First action 读文档 + 报 counts + 等确认机制。
7. 如果 Sprint 5 依赖 Sprint 1、Sprint 2、Sprint 3 或 Sprint 4 未完成，请停止并列出依赖，不要跳过。
8. 输出的 spec/plan 必须能后续转换为 Codex /goal。
9. Sprint 5 重点应围绕 /api/v1/query/stream、/api/v1/feedback、Streamlit Demo、docker-compose 联调、benchmark/Locust 或本地可替代压测、最终 eval、README v2.0、Demo 视频准备说明和简历项目段落。
10. 对真实云部署、真实 B 站上传、真实投递动作，只能标记为人工动作或非代码交付，不要要求 Codex 编造完成结果。
```

## 6. Sprint 2-5：基于 spec/plan 生成 Codex /goal

下面 4 段用于在对应 Sprint 的 Comet spec/plan 完成后，继续发给 Claude，让它用 goal-prompt-builder 生成当前 Sprint 专用 `/goal`。每次只发送一个 Sprint 的文本块。

### Sprint 2：基于 spec/plan 生成 Codex /goal

```text
请基于刚才 Comet 生成的 Sprint 2 spec/plan，使用 goal-prompt-builder 为 Codex 生成 Sprint 2 专用 /goal。

要求：
1. 只覆盖 Sprint 2：混合检索 + 上下文工程。
2. 不包含 Sprint 3、Sprint 4、Sprint 5 的实现项。
3. 如果需要修改 Sprint 1 已有文件，只允许做与 Sprint 2 集成直接相关的最小兼容改动，不要回头重做 Sprint 1。
4. 保留 First action：
   - 先读取项目规划文档
   - 报告 Sprint 2 checklist 数量
   - 报告当前 TODO / NotImplementedError / 501 Not implemented 数量，重点标出 retrieval / context / eval 相关分布
   - 报告当前 tests 数量，以及 retrieval / context 相关测试覆盖概况
   - 报告 Sprint 1 已完成能力与 Sprint 2 依赖关系
   - 等我确认后再开始实现
5. Scope 只能包含 Sprint 2 所需文件。
6. Done when 必须是可机械验证的条件，重点落到检索、上下文工程、评测脚本和相关文档同步。
7. Stop if 必须包含：
   - 需要新增依赖
   - 需要真实 API key
   - 需要外部付费模型
   - 需要云服务、Docker daemon 或数据库服务
   - 当前测试出现 regression
   - diff 超过合理范围且没有阶段性测试记录
8. 不要添加任何 token budget / use limit。
9. 输出最终可直接复制到 Codex CLI 的 /goal 文本。
```

### Sprint 3：基于 spec/plan 生成 Codex /goal

```text
请基于刚才 Comet 生成的 Sprint 3 spec/plan，使用 goal-prompt-builder 为 Codex 生成 Sprint 3 专用 /goal。

要求：
1. 只覆盖 Sprint 3：LangGraph Agent 图 + MCP 工具层。
2. 不包含 Sprint 4、Sprint 5 的实现项。
3. 如果需要修改 Sprint 1 或 Sprint 2 已有文件，只允许做与 Sprint 3 集成直接相关的最小兼容改动，不要回头重做前序 Sprint。
4. 保留 First action：
   - 先读取项目规划文档
   - 报告 Sprint 3 checklist 数量
   - 报告当前 TODO / NotImplementedError / 501 Not implemented 数量，重点标出 agents / graph / mcp 相关分布
   - 报告当前 tests 数量，以及 graph / mcp 相关测试覆盖概况
   - 报告 Sprint 1-2 已完成能力与 Sprint 3 依赖关系
   - 等我确认后再开始实现
5. Scope 只能包含 Sprint 3 所需文件。
6. Done when 必须是可机械验证的条件，重点落到 LangGraph 主图、MCP 工具、集成测试和 API / README / docs 同步。
7. Stop if 必须包含：
   - 需要新增依赖
   - 需要真实 API key
   - 需要外部付费模型
   - 需要 MCP 客户端 GUI、云服务、Docker daemon 或数据库服务
   - 当前测试出现 regression
   - diff 超过合理范围且没有阶段性测试记录
8. 不要添加任何 token budget / use limit。
9. 输出最终可直接复制到 Codex CLI 的 /goal 文本。
```

### Sprint 4：基于 spec/plan 生成 Codex /goal

```text
请基于刚才 Comet 生成的 Sprint 4 spec/plan，使用 goal-prompt-builder 为 Codex 生成 Sprint 4 专用 /goal。

要求：
1. 只覆盖 Sprint 4：Policy Layer + LLMOps + Guardrails。
2. 不包含 Sprint 5 的实现项。
3. 如果需要修改 Sprint 1、Sprint 2 或 Sprint 3 已有文件，只允许做与 Sprint 4 集成直接相关的最小兼容改动，不要回头重做前序 Sprint。
4. 保留 First action：
   - 先读取项目规划文档
   - 报告 Sprint 4 checklist 数量
   - 报告当前 TODO / NotImplementedError / 501 Not implemented 数量，重点标出 policy / observability / guardrails / api 相关分布
   - 报告当前 tests 数量，以及 policy / guardrails 相关测试覆盖概况
   - 报告 Sprint 1-3 已完成能力与 Sprint 4 依赖关系
   - 等我确认后再开始实现
5. Scope 只能包含 Sprint 4 所需文件。
6. Done when 必须是可机械验证的条件，重点落到 model router、fallback、指标观测、guardrails、rate limit、鉴权和相关文档同步。
7. Stop if 必须包含：
   - 需要新增依赖
   - 需要真实 API key
   - 需要外部付费模型
   - 需要 Langfuse、Redis、云服务、Docker daemon 或数据库服务才能完成关键验收项
   - 当前测试出现 regression
   - diff 超过合理范围且没有阶段性测试记录
8. 不要添加任何 token budget / use limit。
9. 输出最终可直接复制到 Codex CLI 的 /goal 文本。
```

### Sprint 5：基于 spec/plan 生成 Codex /goal

```text
请基于刚才 Comet 生成的 Sprint 5 spec/plan，使用 goal-prompt-builder 为 Codex 生成 Sprint 5 专用 /goal。

要求：
1. 只覆盖 Sprint 5：SSE / Demo / benchmark / README 定稿。
2. 不包含新的 Sprint 1-4 扩展实现项；如果需要修改前序 Sprint 文件，只允许做与 Sprint 5 收尾、集成和演示直接相关的最小兼容改动。
3. 对真实云部署、真实 B 站上传、真实投递动作，只能标记为人工动作或非代码交付，不要编造成已完成。
4. 保留 First action：
   - 先读取项目规划文档
   - 报告 Sprint 5 checklist 数量
   - 报告当前 TODO / NotImplementedError / 501 Not implemented 数量，重点标出 api stream / feedback / demo / benchmark / docs 相关分布
   - 报告当前 tests 数量，以及 benchmark / demo / docs 对应的现状
   - 报告 Sprint 1-4 已完成能力与 Sprint 5 依赖关系
   - 等我确认后再开始实现
5. Scope 只能包含 Sprint 5 所需文件。
6. Done when 必须是可机械验证的条件，重点落到 SSE、反馈接口、Demo、benchmark、README/docs 定稿和可复现实验命令。
7. Stop if 必须包含：
   - 需要新增依赖
   - 需要真实 API key
   - 需要外部付费模型
   - 需要真实云服务账号、真实视频上传、真实投递动作、Docker daemon 或数据库服务
   - 当前测试出现 regression
   - diff 超过合理范围且没有阶段性测试记录
8. 不要添加任何 token budget / use limit。
9. 输出最终可直接复制到 Codex CLI 的 /goal 文本。
```

## 7. 每个 Sprint 的固定推进顺序

```text
1. 给 Claude 发送当前 Sprint 的 /comet 指令。
2. 让 Claude 只生成 Comet spec/plan，不写代码。
3. 基于 spec/plan，让 Claude 用 goal-prompt-builder 生成当前 Sprint 专用 /goal。
4. 让 Claude 自查 /goal 是否越界、是否可审计。
5. 把最终 /goal 发给 Codex 执行。
6. Codex 完成并通过当前 Sprint 验收后，再进入下一个 Sprint。
```

## 8. 不要做的事

```text
不要一次性让 Claude 或 Codex 实现 Sprint 1-5。
不要把 Comet 的 spec/plan 当成最终 /goal。
不要让 goal-prompt-builder 跳过 Comet spec/plan 直接写全量大目标。
不要删除 First action 读文档 + 报 counts + 等确认机制。
不要把 Sprint 2-5 的 Scope 混进 Sprint 1。
不要在没有真实验证命令输出时写“已达标”。
```

## 9. 先全局规划，再逐 Sprint 定稿执行

如果你的目标是先和 Claude 讨论并形成一套完整开发文档，再让 Codex 按开发流程逐 Sprint 执行，那么不要一开始就让 Claude 产出 5 个最终版 `/goal`。更稳的做法是：

```text
先让 Claude 一次性产出 Sprint 1-5 的完整开发规划
        ↓
你确认整体范围、依赖顺序和验收边界
        ↓
再让 Claude 只定稿当前 Sprint 的 /goal
        ↓
把当前 Sprint 的 /goal 发给 Codex 执行
        ↓
根据最新仓库状态进入下一个 Sprint
```

### 9.1 适用场景

```text
适用于你想先把项目 1 的完整开发路线、Sprint 划分、依赖关系、测试命令、人工动作边界全部讨论清楚，再启动 Codex /goal 执行的情况。
```

### 9.2 发给 Claude 的全局规划指令

新开 Claude 对话时，优先发送下面这段。它的目标是让 Claude 一次性完成 Sprint 1-5 的规划文档，但不直接产出 5 个最终版 `/goal`。

```text
请读取并遵循 C:\Users\sundewang\Code\knowledge-ops\docs\claude-comet-goal-workflow.md。

先理解第 1 节总说明。

本轮目标不是写代码，也不是一次性生成 5 个最终版 Codex /goal。

本轮只做“完整开发规划”：

1. 为 Sprint 1-5 分别生成 Comet spec/plan。
2. 把 5 个 Sprint 的 spec/plan 组织成一套完整开发文档。
3. 明确每个 Sprint 的：
   - Objective
   - Scope
   - Constraints
   - Done when
   - Stop if
   - checklist 映射
   - 验证命令
   - 依赖前序 Sprint 的关系
   - 人工动作与非代码交付边界
4. 不写代码。
5. 不生成 5 个最终版 Codex /goal。
6. 可以额外附上 Sprint 2-5 的 /goal 草案提纲，但不要定稿。
7. 如果某个 Sprint 的 checklist、依赖关系或边界无法从项目文档中明确识别，请停止并列出缺失信息，不要猜测。
8. 完成后停止，等待我下一步指令。

输出只包含：
1. 生成了哪些 spec/plan 文件。
2. Sprint 1-5 的依赖顺序和范围摘要。
3. 哪些 Sprint 可以直接进入 /goal 定稿。
4. 哪些 Sprint 必须等前序 Sprint 执行后再重新校准。
5. 下一步我应该先让你定稿哪个 Sprint 的 /goal。
```

### 9.3 全局规划完成后的推进顺序

拿到 Claude 生成的完整开发规划后，按下面顺序推进：

```text
1. 先检查 Sprint 1-5 的依赖顺序是否合理。
2. 先让 Claude 定稿 Sprint 1 的 /goal，不要一次性定稿 Sprint 2-5。
3. 用 Codex 执行 Sprint 1 /goal。
4. Sprint 1 完成后，把最新仓库状态交给 Claude。
5. 再让 Claude 定稿 Sprint 2 的 /goal。
6. 重复同样流程，直到 Sprint 5。
```

### 9.4 为什么不要一次性定稿 5 个 /goal

```text
因为 Sprint 2-5 的最终 /goal 会依赖 Sprint 1 实际落地结果：
- 文件范围会变
- 测试基线会变
- TODO / NotImplementedError 分布会变
- 已实现接口与目录结构会变
- Stop if 和 Done when 也需要基于最新仓库状态重算

所以可以一次性规划 5 个 Sprint，但不要一次性定稿 5 个最终版 /goal。
```
