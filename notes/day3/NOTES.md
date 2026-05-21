# Day 3 笔记 — 5/20 周三

> **目标**：从"裸调 OpenAI SDK"升级到 LangChain "组件化拼装"，并接入 LangSmith 看清每一步

## ✅ 完成情况

- [x] `uv add langchain langchain-openai langchain-community langchain-core langsmith` 装齐全家桶
- [x] 验证 LangChain 1.3.1 / langchain-core 1.4.0 / langchain-openai 1.2.1 等版本就位
- [x] `.env` 补 LangSmith 三字段（`TRACING` / `API_KEY` / `PROJECT=knowledge-ops-w1`）
- [x] `01_chain_basic.py` 跑通：LCEL `prompt | llm | parser` + 等价性 DEBUG 验证
- [x] `02_memory.py` 跑通：3 轮对话，最后一轮 Bot 答出 "王晟 / 2027 年毕业"，DEBUG 输出 session_store 里 6 条消息
- [x] `03_langsmith.py` 跑通：先用无 key 走 graceful 降级，再补 key 后开启 TRACING 看 dashboard
- [x] LangSmith 注册 + 拿 API Key + dashboard 验证（截图：`W1-知识速成周/LangSmith dashboard 截图.png`）
- [x] commit 入库（`b34fc15`）

## 🎯 今天 AHA Moment

**一句话**：LCEL 的 `|` 不是语法糖，而是 `Runnable` 接口上的代数运算——`prompt | llm | parser` 等于 `parser.invoke(llm.invoke(prompt.invoke(x)))`，底层是 `Runnable.__or__` 重载返回 `RunnableSequence`。我在 01 脚本里特地埋了 DEBUG 输出对比手动三步嵌套 vs `chain.invoke`，type 链条 `ChatPromptValue → AIMessage → TextAccessor` 完全一致——**用代码验证概念比看视频强一个数量级**。

**第二个 AHA**：LangSmith 一打开就看到完整 chain 执行树（`RunnableSequence` 套着 `VectorStoreRetriever` 套着 `ChatOpenAI`），从此 `print` 调试可以下岗。`.env` 里 `TRACING=true` **一行配置**，Day3 旅游 chain + Day4 RAG chain **全部自动上报**——LangChain 抽象层的非侵入价值在这里彻底落地。

**第三个 AHA**：LangChain 1.x 是大版本变动。`RunnableWithMessageHistory` 跑 02 时弹 `DeprecationWarning: Use LangGraph's built-in persistence instead`——0.x 的 Memory wrapper 已经被官方推到 LangGraph 的 `MemorySaver` / `Checkpointer` 体系，Agent 也跟着搬家。这就是周五要学 LangGraph 的根本原因。

## 🔑 核心概念

### LCEL（LangChain Expression Language）

```python
chain = prompt | llm | parser
chain.invoke(x)
# 等价于：
parser.invoke(llm.invoke(prompt.invoke(x)))
```

| 属性 | 解释 |
|---|---|
| 实现机制 | `Runnable.__or__` 重载返回 `RunnableSequence` |
| 统一接口 | `.invoke()` / `.batch()` / `.stream()` / `.ainvoke()` |
| 组件来源 | Prompt / LLM / Parser / Retriever / Tool 全部继承 `Runnable` |
| 类比 | Unix 管道（`cat file \| grep foo \| wc -l`） |

**面试金句**：*"LCEL 是用 Python 的 `|` 操作符做的 monadic pipeline DSL，让 LLM 应用的组合方式从命令式回调升级到声明式管道，同时统一了 `invoke / batch / stream / ainvoke` 四个接口。"*

### 三大核心组件

| 组件 | 作用 | 常用类 |
|---|---|---|
| **Prompt** | 模板化输入 | `ChatPromptTemplate` |
| **LLM** | 语言模型 | `ChatOpenAI`（含 DeepSeek 等 OpenAI 兼容协议） |
| **Output Parser** | 解析输出 | `StrOutputParser` / `JsonOutputParser` / `PydanticOutputParser` |

⚠️ LangChain 1.x 细节：`StrOutputParser.invoke()` 返回 `TextAccessor`（`str` 子类），不是裸 `str`——能正常 `print` 和后续传递，但 `isinstance(x, str)` 仍 True。

### DeepSeek 接入 LangChain

用 `ChatOpenAI`（**不是** `ChatDeepSeek`），关键参数 `base_url`：

```python
llm = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),  # 关键
)
```

**原理**：DeepSeek 完全兼容 OpenAI Chat Completions 协议。同一套 `ChatOpenAI` 能接 **Moonshot / 智谱 / 通义 / 豆包**——只要对方实现了 OpenAI 协议。

**面试金句**：*"我们用 ChatOpenAI 当统一抽象层接多家国产模型，切换模型时只改 base_url + model name，业务代码零修改。"*

### `from_messages` 接受的角色

- `"system"` — 系统设定
- `"user"` / `"human"` — 用户消息（两个等价）
- `"assistant"` / `"ai"` — 模型回复
- `"tool"` — 工具调用结果
- `"placeholder"` — 等价于 `MessagesPlaceholder`，挖一个消息列表插槽

也可以直接传 `BaseMessage` 实例（`HumanMessage(...)`）或 `MessagesPlaceholder(...)` 对象。

### MessagesPlaceholder vs `("user", "{history}")`（**重点**）

`history` 是 `List[BaseMessage]`，每条带自己的 role（HumanMessage / AIMessage）。

| 写法 | 注入到 prompt 的样子 | 效果 |
|---|---|---|
| `MessagesPlaceholder("history")` | 展开成 N 条独立 message，**保留 role** | LLM 看到的是真正的 multi-turn 对话 |
| `("user", "{history}")` | 整个列表 str 化，变成 `[HumanMessage(content='我叫王晟'), ...]` 这种字符串 | LLM 看到的是一坨 user 文本，**role 信息丢失** |

**为什么这重要**：LLM 训练时见的就是 multi-turn role-tagged 的 ChatML 协议数据，role 是模型做 turn-taking 的关键信号。丢了 role，模型可能把"自己说过的话"当成"用户提的新需求"。

### Memory 的三种主流策略

| 类型 | 原理 | Token 成本 | 信息保真度 |
|---|---|---|---|
| `ChatMessageHistory`（Buffer） | 全保留 | **每轮翻倍** | 100% |
| `ConversationSummaryMemory` | LLM 总结历史 | 低（固定） | 损失细节 |
| `ConversationBufferWindowMemory` | 保留最近 N 轮 | 中（封顶） | 损失早期上下文 |

**生产**：常用 **Summary + Window 组合**——早期对话总结成摘要，最近 N 轮原样保留。

### LangSmith 的价值

- 看到每次 LLM 调用的完整输入输出
- Token 成本归因（哪条 Chain 烧钱）
- 延迟瓶颈定位（哪一步最慢）
- 测试集回归（同一组输入，对比不同 Prompt 的效果）

dashboard 看 Token：
- **Run Details → Run Info**：Total / Prompt / Completion Tokens
- **Stats 面板**：cost ($) + latency (ms) + token 时序图
- **Project 总览**：按 Total Tokens 列排序，一眼找出"最烧钱的 chain"

**面试常考**：*"你用过什么 LLM 监控工具？"*——答 LangSmith（生产）+ Langfuse（自托管开源版，周六会学）。

### LangChain 1.x 的关键变化（**重点 - 大版本迁移**）

`RunnableWithMessageHistory` 在 1.x 里 **deprecated**，官方推荐 **LangGraph 的 `MemorySaver` / `Checkpointer`**：

| 0.x | 1.x |
|---|---|
| Memory 是 chain wrapper（外面包一层） | Memory 是 LangGraph 状态机的 first-class 字段 |
| 难以扩展中断恢复、分支、HITL | 原生支持持久化、回滚、Time Travel、HITL |
| `RunnableWithMessageHistory(...)` | `langgraph.checkpoint.MemorySaver()` + `Graph.compile(checkpointer=...)` |

**W1 怎么处理**：不重构。Day3 跑通就行，明天 Day5 学 LangGraph 时自然过渡到新写法。

**面试金句**：*"LangChain 1.x 把 Memory 和 Agent 都迁移到 LangGraph 体系，因为状态机比线性 chain 更适合表达 Agent 的循环、分支和持久化。"*

## ❓ 卡壳记录 → 🧪 实测答案

| # | 卡壳问题 | 实测答案 | 证据 |
|---|---|---|---|
| Q1 | LCEL 的 `\|` 操作符等价于什么 Python 调用？ | `chain.invoke(x)` ≡ `parser.invoke(llm.invoke(prompt.invoke(x)))` | 01 脚本 DEBUG 输出 type 链条 `ChatPromptValue → AIMessage → TextAccessor` |
| Q2 | `RunnablePassthrough` 是干嘛的？ | 把 `invoke` 的输入原样塞进 chain 的字典字段（占位 passthrough） | Day4 RAG chain `{"context": retriever \| format_docs, "question": RunnablePassthrough()}` |
| Q3 | `ChatPromptTemplate` 和 `PromptTemplate` 区别？ | 前者输出 `ChatPromptValue`（多条 role-tagged messages），后者输出 `StringPromptValue`（单段字符串） | 主流 chat model 用前者，老式 completion model 用后者 |
| Q4 | `tool_calls` 不调工具时是 `None` 还是 `[]`？（Day2 卡壳） | `None`（NoneType） | Day2 02_function_calling.py 实测 |
| Q5 | LangSmith 5k traces 超了怎么办？ | (1) 关 staging/test trace；(2) Developer $39/月 = 100k；(3) 自托管 OSS 版无限 trace | 官方定价页 |
| Q6 | LangChain 1.x 跑 `RunnableWithMessageHistory` 报 DeprecationWarning？ | 官方推荐迁 LangGraph `MemorySaver`，旧 API 仍可用 | 02 脚本运行时输出 |
| Q7 | 为什么 `load_dotenv()` 必须在 import langchain_* 之前？ | LangChain 启动时读 `LANGSMITH_*` 环境变量，晚 load 读不到 → trace 不会打开 | 03 脚本顶部注释 |

### 🐞 实测发现的细节

- **LangChain 1.x 装包附赠**：`uv add langchain` 自动拉了 `langgraph 1.2.0` + `langgraph-checkpoint 4.1.0` + `langgraph-prebuilt 1.1.0`——周五学 LangGraph 不用再装包。
- **`StrOutputParser` 返回 `TextAccessor`**：1.x 新行为，不是裸 `str`。
- **`02_memory.py` 的 session_store dict**：3 轮对话后存 6 条 message（3 HumanMessage + 3 AIMessage）——证明 `RunnableWithMessageHistory` 自动追加双向消息。

## 💭 自由发挥

- **DeepSeek 中转端点接入 LangChain 的踩坑**：`.env` 里 `DEEPSEEK_BASE_URL=https://api.zhenhaoji.qzz.io/v1`（**必须显式带 `/v1`**，Day1 已踩过），LangChain 1.x 的 `ChatOpenAI` 直接复用这个 base_url，零额外配置。一次配置 Day3-Day4 所有 chain 都用，**这就是抽象层的复利**。
- **LangSmith 截图的意外彩蛋**：原本只想验证 Day3 的 03 旅游 chain，结果 dashboard 同时记录了 Day4 跑的 PDF RAG（3 个问题 + `I don't know` 防幻觉记录）——证明 `TRACING=true` 是全局开关，业务代码零修改即可监控。这种"一开关全 chain 接入"才是 LLMOps 工程真正的价值。
- **Memory 三种策略本质是 Token / 保真度的权衡**：W1 速成期用 Buffer（短对话）够，但项目 1 客服场景必须上 Summary（长对话会烧 token）。**面试一问就要能讲清楚这个 trade-off**，而不是背"三种 Memory"。
- **LCEL 让我对 Day2 Function Calling 的 `while True` 重新审视**：Day2 是手写 `while not msg.tool_calls` 循环。LangGraph 把这个循环升级成"图的条件边"——条件不满足就回到 LLM 节点。明天就会看到这种"线性 chain 升级成状态图"的范式跃迁。
- **6 小时的活我大概用了 4 小时**：跟 Day1（2/6）、Day2（6/6）相比，Day3 LangChain 概念多但都是组装，跑通门槛低；真正费时的是装包（torch 拖下来 108MB）和 LangSmith 注册等账号事务。

## 📅 明日预告

**Day 4 - RAG 全套速览（重头戏）**

通读 all-in-rag 教程 1-4 章 4 小时，建立"什么是 RAG / 怎么搭 RAG / 怎么优化 RAG"的全景认知。下午跑通一个 PDF 问答 Hello World（PDF → split → embed → 向量库 → retriever → LCEL chain → LLM）。

提前准备：
- ~~Docker Desktop 启动（Milvus 要用）~~ → 用 Milvus Lite 或 FAISS 跳过 Docker
- 准备 1-2 个 PDF 测试文件（arxiv 上的论文最稳）
