# Day 5 笔记 — 5/22 周五

> **目标**：理解"Chain → Graph"的升级 + 用 LangGraph 写出第一个 ReAct Agent + Supervisor Multi-Agent

## ✅ 完成情况

- [x] DLAI「AI Agents in LangGraph」第 1-2 节速过（核心：State Schema + Conditional Edge + Checkpointer）
- [x] LangGraph 官方 Quickstart
- [x] `01_react_agent.py` 跑通：`create_react_agent(llm, tools)` 一行 + 3 工具（calculator / get_weather / search_wiki），ReAct 循环 6 条 message 完整链
- [x] `02_graph_basics.py` 跑通：手撸 StateGraph 两节点（write_draft → polish），含 `draw_ascii()` 终端可视化
- [x] `03_supervisor.py` 跑通：Supervisor 模式 + 条件边路由，数学题→math_agent / 故事题→story_agent
- [x] `uv add grandalf` 装上让 `draw_ascii` 在终端直接渲染
- [x] `target_companies.md` 30 家公司 S/A/B 分级初稿（待 Boss 修订）
- [x] commit 入库

## 🎯 今天 AHA Moment

**一句话**：**LangGraph = 把 Day2 的 `while True` 循环升级成状态机**。

这是今天最深的连接。Day2 我手写：
```python
while True:
    msg = llm(messages)
    if not msg.tool_calls: break
    for call in msg.tool_calls:
        result = TOOLS[call.name](**args)
        messages.append({"role": "tool", "content": result})
```

Day5 一行就够了：
```python
agent = create_react_agent(llm, tools)
result = agent.invoke({"messages": [("user", question)]})
```

一行的背后，LangGraph 把那个 `while` 循环**画成了图**：
```
START → agent 节点 → 有 tool_calls? → 是 → tools 节点 → 回 agent
                                  → 否 → END
```

01 跑出的 6 条 message 链（User → AI/tool_calls(weather) → Tool(25°C) → AI/tool_calls(calc) → Tool(77) → AI 综合）就是这个循环的物理痕迹。**从"写状态机"变成"画状态机"**，可读性和可视化是数量级提升。

**第二个 AHA**：02 跑完 `app.get_graph().draw_ascii()` 直接在终端画出：
```
 +-----------+
 | __start__ |
 +-----------+
        *
+-------------+
| write_draft |
+-------------+
        *
  +--------+
  | polish |
  +--------+
        *
  +---------+
  | __end__ |
  +---------+
```

**Graph 可视化是 LangGraph 比 AutoGen 强的核心卖点**——状态可见、流程可见、问题可定位。AutoGen 把状态藏在对话抽象后面，调试要靠 print log。

**第三个 AHA / 也是最大警报**：跑 01 弹出：
```
LangGraphDeprecatedSinceV10: create_react_agent has been moved to
`langchain.agents`. Please update your import to
`from langchain.agents import create_agent`.
Deprecated in LangGraph V1.0 to be removed in V2.0.
```

这是继 Day3 `RunnableWithMessageHistory deprecated` 之后**第二个 LangChain 1.0 迁移信号**。1.0 在做一场大重构：底层引擎（状态机/持久化）归 LangGraph、高层 API（Agent/Chain 构造器）归 langchain.agents——**各归各位**。求职面试讲 LangChain 演进，这就是金句素材。

## 🔑 核心概念

### Chain vs Graph（**必背差异**）

| 维度 | Chain（LangChain LCEL） | Graph（LangGraph） |
|---|---|---|
| **拓扑** | 线性 A → B → C | 任意 DAG / 含循环 |
| **状态** | 隐式（每步输入输出对接） | **显式 State**（共享内存，所有节点可读写） |
| **分支** | 不支持 | `add_conditional_edges(node, route_fn)` |
| **循环** | 不支持 | 支持（ReAct / Self-Refine） |
| **中断/恢复** | 不支持 | **Checkpointer 持久化** + Time Travel + HITL |
| **适合** | 简单流水线 | Agent / Multi-Agent |

**面试金句**：*"LangGraph 把 LLM 应用从'函数式管道'升级成了'状态机'——这就是为什么 LangChain 1.0 把 Memory 和 Agent 都迁移到 LangGraph 体系：Agent 的本质是循环 + 分支 + 状态，用线性 chain 表达不了。"*

### LangGraph 三要素

```python
1. State（TypedDict）       # 图的"共享内存"
2. Node（函数 State → dict） # 节点只返回需要更新的字段，不用全量传 State
3. Edge（边，可有条件）      # 控制流
```

**State 用 TypedDict 还是 Pydantic**：
| | TypedDict（官方默认） | Pydantic |
|---|---|---|
| 类型提示 | ✅ | ✅ |
| Runtime 强校验 | ❌ | ✅ |
| 序列化 | 弱 | 强 |
| 适合 | W1 速成 / 简单图 | 生产 / 跨节点边界传敏感数据 |

**Annotated 字段（带 reducer）**：State 字段需要被多次"追加更新"时用。例：
```python
class State(TypedDict):
    messages: Annotated[list, add]  # 多次调用追加而非覆盖
```
ReAct 循环每轮 LLM 调用都追加新 message，靠 `add`（即 `operator.add`，列表拼接）。今天 01 跑出的 6 条 message 累加就是这个 reducer 的功劳。

### ReAct 模式（**面试必背**）

```
循环：LLM 思考 → 决定调哪个工具 → 执行工具 → 看结果 → 继续思考
直到 LLM 觉得"任务完成"，输出最终答案
```

**`create_react_agent(llm, tools)` 一行的背后**（面试可讲）：
1. `llm.bind_tools(tools)` 把工具 schema 绑到 LLM
2. 创建 StateGraph，State 含 `messages: Annotated[list, add]`
3. 加 `agent` 节点（LLM 调用）+ `tools` 节点（工具执行）
4. 加**条件边**：`agent` 输出有 `tool_calls` → `tools` 节点；无 → END
5. 加边：`tools` → 回 `agent`（循环）
6. compile 成可执行 Runnable

**何时停**：LLM 输出不再有 `tool_calls` 字段。

### `add_edge` vs `add_conditional_edges`

| | `add_edge(A, B)` | `add_conditional_edges(A, route_fn)` |
|---|---|---|
| 行为 | A 跑完一定跳 B | A 跑完调 `route_fn(state)`，返回字符串决定跳哪 |
| 用途 | 固定流程 | 动态分支（Supervisor / ReAct 循环判断都用它） |
| 返回值 | -- | 必须是已注册的节点名字符串（或 `END`） |

### Multi-Agent 三大模式

| 模式 | 描述 | 适合场景 | 工程例子 |
|---|---|---|---|
| **Supervisor**（今天做的） | 1 个监督 Agent + N 个 Worker | 任务可路由 | 项目 1 的 QA / Summary / Report 三 Agent |
| **Hierarchical** | 树状层级（Supervisor 套 Supervisor） | 复杂任务拆解 | AutoGPT / 数据分析 Pipeline |
| **Network** | Agent 互相调用，无中心 | 自由协作 / 辩论 | 红蓝队对抗、Multi-Agent debate |

### LangGraph vs AutoGen vs CrewAI（**面试题**）

| 框架 | 风格 | 优势 | 劣势 |
|---|---|---|---|
| **LangGraph** | 显式图 + State + 边 | **可控、可视化好（mermaid）、生产级**、HITL 一等公民 | 写法略繁，要懂 State Schema |
| **AutoGen**（Microsoft） | 对话式 Agent | 对话流畅、agentchat 抽象高 | **调试难、状态不可见** |
| **CrewAI** | 角色扮演 | 简单易写、上手快 | 不够灵活、可控性弱 |

**项目 1 必须用 LangGraph**（招聘市场最主流 + 可控性最好）。

**面试金句**：*"我们选 LangGraph 而不是 AutoGen，是因为 LangGraph 把状态机暴露给开发者——可以 inspect、序列化、HITL 注入、回滚到任意节点。AutoGen 把这些藏在对话抽象后面，生产环境调试难。"*

### LangChain 1.0 大重构地图（截至 Day5）

| 0.x 的位置 | 1.0 的新位置 | 状态 |
|---|---|---|
| `RunnableWithMessageHistory`（Day3 跑过） | `langgraph.checkpoint.MemorySaver` | ⚠️ Deprecated |
| `langgraph.prebuilt.create_react_agent`（Day5 用的） | `langchain.agents.create_agent` | ⚠️ Deprecated since V1.0 |
| Agent / AgentExecutor（0.x） | `langchain.agents.*`（重写） | 🆕 重新设计 |

**为什么 LangChain 1.0 改这么多**：0.x 把 Agent 写在 LangChain，把状态机写在 LangGraph，两套体系。1.0 想统一——Agent 的核心是状态机，所以 Memory 全迁到 LangGraph；但 Agent 的高层抽象（`create_agent`）放回 langchain.agents 让用户更容易找到。**"底层引擎"和"高层 API"各归各位**。这是 LLM 框架进入成熟期的标志。

### Checkpointer（明天 Day6 不直接用但要知道）

```python
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)
app.invoke({"input": "..."}, config={"configurable": {"thread_id": "user_001"}})
```

每个节点跑完自动存 snapshot。`thread_id` 隔离不同对话。可以：
- **Resume**：从任意检查点恢复执行
- **Time Travel**：回到历史状态分支重跑（项目 1 用户问"如果我那时选另一个路径会怎样"的功能）
- **HITL（Human In The Loop）**：在某个节点中断，等人审核后再继续

## ❓ 卡壳记录 → 🧪 实测答案

| # | 卡壳问题 | 实测答案 | 证据 |
|---|---|---|---|
| Q1 | State 用 TypedDict 还是 Pydantic？ | TypedDict 轻、给提示但不强校验；Pydantic 严、带运行时校验。W1 速成 TypedDict 够，生产用 Pydantic | 02/03 都用 TypedDict 跑通 |
| Q2 | Annotated 字段什么时候用？ | 多次"追加更新"时。ReAct 的 `messages: Annotated[list, add]` 累加新 message 而非覆盖 | 01 跑出 6 条 message 链就是累加结果 |
| Q3 | 怎么持久化 Graph 中间状态？ | Checkpointer，`graph.compile(checkpointer=MemorySaver())`。1.0 把 Memory 迁去 LangGraph 就是为了这个 | LangGraph 官方 Persistence 文档 |
| Q4 | Multi-Agent 怎么共享 Memory？ | 共享 State（同图内天然共享）；跨 Graph 用 Checkpointer + 同 thread_id | 03 三 Agent 读写同一 State 跑通 |
| Q5 | create_react_agent 报 LangGraphDeprecatedSinceV10？ | 1.0 把它迁去 `langchain.agents.create_agent`，V1.x 仍能跑（弹 warning），V2.0 删除 | 01 脚本运行时输出 |
| Q6 | `draw_ascii()` 报 Install grandalf？ | `uv add grandalf` 一行解决。装完 02/03 在终端直接渲染 | 装包后重跑 02 验证 |
| Q7 | `add_conditional_edges` 的 route_fn 返回什么？ | 必须是已注册的节点名字符串（或 `END`）。可用 `Literal["math_agent", "story_agent"]` 给类型提示 | 03 `route` 函数 |
| Q8 | StateGraph 节点函数必须返回 dict 吗？返回什么 dict？ | 返回 dict，**只放需要更新的字段**。LangGraph 自动 merge 进 State，未提及的字段保持原值 | 02 `write_draft` 只返 `{"draft": ...}`，不带 `question` 也不带 `final` |

### 🐞 实测发现的细节

- **LangGraph 1.x 的 `draw_ascii` 输出非常清晰**：节点用 `+----+` 框，边用 `*` 串起来，比 mermaid 文本对终端用户友好。装 grandalf 一行 ROI 极高。
- **`create_react_agent` 默认无 system prompt**：如果想给 Agent 设定角色（"你是数学老师"），需要传 `system_message` 或 `state_modifier` 参数（V1.x 改了多次，看具体版本）。
- **DeepSeek 走 OpenAI 协议跑 ReAct 完全 work**：6 条 message 链里的 `tool_calls` 字段格式跟 OpenAI 一模一样（`Call ID: chatcmpl-tool-xxx`），LangGraph 解析无障碍。
- **03 Supervisor 的 route_fn 返回字符串拼接**：`return f"{state['intent']}_agent"`——只要 intent 是 "math" 或 "story"，自动映射到 `math_agent` 或 `story_agent` 节点名。这种"约定优于配置"的写法在 Multi-Agent 里很常见。

## 💭 自由发挥

- **Day2 → Day5 的范式连续性令人惊喜**：Day2 我手写 100 多行 while 循环来实现"工具调度+状态维护"，Day5 一行 `create_react_agent` 搞定。LangGraph 把状态机抽象成可视化的图，**从"写状态机"变成"画状态机"**——这就是为什么 1.0 重构后大量逻辑从 LangChain 迁到 LangGraph。
- **Multi-Agent = 多套 system prompt + 路由器**：Day2 笔记里我就写过这句话。今天 03 Supervisor 跑完后有了完整画面：math_agent / story_agent 是多套 system prompt；supervisor + `add_conditional_edges` 是路由器；State 是共享上下文。项目 1 的 KnowledgeOps 三 Agent（QA / Summary / Report）就是 03 的扩展版。
- **LangChain 1.0 重构的设计哲学值得深挖**：底层引擎归 LangGraph、高层 API 归 langchain.agents、Chain 构造器归 LangChain core——**模块边界清晰**。这种"统一抽象+各归各位"是软件工程成熟的标志，跟 React 把状态管理从 class component 迁到 hooks 是同一类范式跃迁。面试讲框架演进必备金句。
- **Graph 可视化是 LangGraph 的核心卖点**：今天装 grandalf 后 02/03 的图直接在终端画出来。AutoGen 的"对话式 Agent"看着炫，但代价是状态不可见、调试要靠 print log。LangGraph 把状态机显式暴露给开发者，可 inspect、可序列化、可 HITL 注入、可 mermaid 导出贴 PR。**这是为什么招聘市场倒向 LangGraph**。
- **HITL（Human In The Loop）是 LangGraph 比 Chain 的杀手锏**：Checkpointer + 中断节点让 Agent 可以"等待人类审核再继续"。生产场景：内容审核、金融交易 Agent 触发风控人工 confirm、知识库写回 Agent 改前要 review。Chain 写不出这种流程。
- **求职动作初体验**：今天第一次有"📌 求职动作"环节。30 家公司 S/A/B 分级初稿我用 30 分钟起完，但 Boss 验收时建议用 BOSS 直聘/小红书/知乎 verify 招聘状态——AI 给的清单是 starting point，不是 ground truth。**学长姐内推是真正的高 ROI 通道**，比海投强 10 倍。
- **6 小时的活我 3.5 小时**：Day3-Day5 节奏明显比 Day1-Day2 顺——一方面是 LangChain 抽象层让代码量小，另一方面是 Day3/4 装包时附赠了 langgraph，省了装包步骤。**速成期的复利在第二周开始显现**。
- **明天 Day6 心态**：MCP 是 2025-2026 最热协议（Anthropic 推），Langfuse 是 LangSmith 的开源对应物。明天会装 `mcp + langfuse`，应该跟今天一样顺。

## 📅 明日预告

**Day 6 - MCP 协议 + LLMOps 速览**

明天进入 W1 最"新潮"的部分：
- **MCP（Model Context Protocol）**：Anthropic 2024-2025 推出的协议，让 LLM 工具能跨平台复用（一个工具同时给 Claude / ChatGPT / Cursor 用）。**面试金问点：你了解 MCP 吗？**
- **Langfuse**：开源自托管的 LLM 监控，相当于 LangSmith 的免费版（自己跑 Docker），适合企业内网部署
- **Guardrails AI**：LLM 输出防护（防注入、防有害内容、强制 schema）

**明天会装**：
```powershell
uv add mcp langfuse
```

Day 7 是项目 1 顶层架构设计（GitHub 仓库初始化 + 架构图），W1 收尾。
