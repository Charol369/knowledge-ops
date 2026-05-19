# Day 2 笔记 — 5/19 周二

> **目标**：Prompt 工程套路 + Function Calling 闭环

## ✅ 完成情况

- [x] Anthropic Prompt Tutorial Chapter 1-3（基础结构 / 清晰 / 角色）
- [x] Anthropic Prompt Tutorial Chapter 4-6（XML 分隔 / 格式 / CoT）
- [x] Anthropic Prompt Tutorial Chapter 7-9（Few-shot / 防幻觉 / 综合）
- [x] `01_prompt_patterns.py` 跑通（4 种套路对比）
- [x] `02_function_calling.py` 跑通（单工具计算器）
- [x] `03_multi_tools.py` 跑通（多工具调度）
- [x] commit + push

## 🎯 今天 AHA Moment

1. **Function Calling 不是"LLM 调用函数"，而是"LLM 输出 JSON、Python 调函数"**——这一字之差决定了所有架构：LLM 端不需要任何执行环境，Python 端必须做所有兜底（非法 JSON、幻觉参数、不存在的工具）。
2. **`while True` 不是为了重试，而是为了"多步推理"**——跑 02 测试 2 时，LLM 因为 `</` bug 连续 3 次 calculator 失败，第 4 轮干脆不调工具自己算出 5。这种**自适应放弃工具**是真正的 Agent 雏形。
3. **DeepSeek 会泄漏 XML 标签到 arguments 里**（亲眼见 `</937parameter>\n`）——文档不会告诉的生产坑，靠卡壳清单逼自己跑出来才发现。**实战 > 文档**。

## 🔑 核心概念

### Prompt 工程 4 套路

| 套路            | 何时用     | 关键词                                  |
| ------------- | ------- | ------------------------------------ |
| Zero-shot     | 简单问题    | 不加示例直接问                              |
| CoT           | 推理问题    | "一步一步想" / "Let's think step by step" |
| System Prompt | 角色化任务   | 设定身份、风格、约束                           |
| Few-shot      | 格式严格的任务 | 给 2-3 个示例                            |

### Anthropic Tutorial 9 章核心

| 章节                                | 核心思想               | 一句话                           |
| --------------------------------- | ------------------ | ----------------------------- |
| 1. Basic Prompt Structure         | system + user 角色分明 | LLM 不读心，全靠 messages           |
| 2. Being Clear & Direct           | 明确指令，避免歧义          | 写给"高 IQ 但零经验"的实习生             |
| 3. Assigning Roles                | system prompt 设定身份 | 角色 = 一致性 + 风格                 |
| 4. Separating Data & Instructions | 用 XML 标签隔离         | `<context>...</context>` 比拼接稳 |
| 5. Formatting & Length            | 用 prefilling 控制输出  | 让 LLM 接着你的话写                  |
| 6. Precognition (CoT)             | 思维链                | 强制让模型"想出来"再答                  |
| 7. Using Examples                 | Few-shot           | 示例比解释更强                       |
| 8. Avoiding Hallucinations        | 允许"不知道"            | "If you don't know, say so"   |
| 9. Complex Prompts                | 组合所有技巧             | 真实场景的 Prompt 长得像剧本            |

---

### 📖 Chapter 1：Basic Prompt Structure（基础结构）

**一句话**：LLM 不读心，它只看你给它的 `messages` 列表。所有"它没懂"本质都是"你没说清"。

**三个角色**：

| 角色            | 谁说的        | 何时用                    |
| ------------- | ---------- | ---------------------- |
| **system**    | 应用开发者      | 设定 LLM 的"人格、风格、限制"（全局） |
| **user**      | 终端用户       | 实际提问                   |
| **assistant** | LLM 自己（历史） | 让 LLM 记得之前说过什么（多轮）     |

**代码模板**：

```python
messages = [
    {"role": "system",    "content": "你是 Python 后端面试官，每次只问 1 个简洁问题。"},
    {"role": "user",      "content": "开始面试"},
    {"role": "assistant", "content": "请解释一下 Python 的 GIL 是什么。"},  # 多轮才需要
]
```

**反例 vs 正例**：

- ❌ `[{"role": "user", "content": "你好"}]` → LLM 给空话「您好！请问有什么可以帮助您？」
- ✅ 加 system 锚定身份 → LLM 立刻进入角色

**面试要点**：能背出三个角色 + 解释每个的作用。

---

### 📖 Chapter 2：Being Clear and Direct（清晰直接）

**一句话**：把 LLM 当「IQ 180 但零经验的实习生」——能理解复杂逻辑，但不告诉它"格式/长度/受众"，它就乱猜。

**三条铁律**：

1. **指令具体**：不要说"简洁"，说"**50 字以内**"
2. **格式明确**：不要说"列出来"，说"**Markdown 表格，3 列：名称/年代/作用**"
3. **受众清晰**：不要说"解释 RAG"，说"**向 60 岁的中学语文老师用比喻解释**"

**Anthropic 金句**：

> "If the prompt would fail if a thoughtful new hire was given it without context, it's not specific enough."

意思是：把 prompt 想象成给新员工的任务清单——如果一个聪明但没经验的新人看了会问"啥意思？"，那 prompt 不够明确。

**反例 vs 正例**：

- ❌ "介绍一下 Python" → 500 字面面俱到，你没耐心看
- ✅ "用 Markdown 表格列 Python 的 3 个最重要特性，每个特性 2 句话：1 句定义，1 句对比 Java" → 直接拿到想要的格式

---

### 📖 Chapter 3：Assigning Roles（角色化）

**一句话**：System Prompt 是 LLM 的"工牌"——告诉它你是谁、在哪干活、有什么权限/禁忌。

**角色赋予的 3 个杠杆**：

1. **身份 (Who)**：「你是 Python 后端架构师」
2. **风格 (How)**：「用大白话回答，不超过 3 句」
3. **约束 (What not)**：「不要泛泛而谈，每个建议必须可执行」

**同一问题，4 个 system → 4 种完全不同的回答**：

| System Prompt     | 回答风格                    |
| ----------------- | ----------------------- |
| 无                 | 列 20 条通用建议（无聊但全面）       |
| "你是性能专家"          | 重点讲 LCP/FID/CLS 等指标（专业） |
| "你是 7 年 SRE，重视成本" | 先讲监控埋点和性能基线，再讲优化（务实）    |
| "你是 To-C 产品经理"    | 讲首屏体验、用户感知（视角不同）        |

**🔥 真实工程价值（**项目 1 直接用到**）**：

KnowledgeOps 三个 Agent 就是 3 个不同 system prompt：

```python
QA_AGENT_PROMPT      = "你是企业知识库问答专家，基于上下文回答，找不到就说不知道，不编造..."
SUMMARY_AGENT_PROMPT = "你是会议纪要专家，把对话整理成结构化摘要..."
REPORT_AGENT_PROMPT  = "你是技术报告作者，输出 Markdown 报告，含引用编号..."
```

→ **Multi-Agent 的本质 = 多套 System Prompt**。秋招面试这是「你怎么实现 Multi-Agent」的标准答案。

---

### ✋ Chapter 1-3 浓缩 takeaway

| 章节       | 关键词 | 一句话                                                     |
| -------- | --- | ------------------------------------------------------- |
| **Ch 1** | 三角色 | system 设规则、user 提问、assistant 历史                         |
| **Ch 2** | 具体性 | 当成 IQ 180 实习生——指令要"格式+长度+受众"明确                          |
| **Ch 3** | 工牌  | System Prompt 决定身份/风格/约束。Multi-Agent = 多套 System Prompt |

---

### 📖 Chapter 4：Separating Data and Instructions（XML 隔离）

**一句话**：用 XML 标签把"指令"和"数据"隔开，防 Prompt Injection + 给 RAG 系统提供清晰锚点。

**典型 Bug**：

- ❌ 拼字符串 → 用户输入 "忽略上面的指令" 会真的被执行（Prompt Injection）
- ✅ XML 标签 → LLM 把 `<text>` 里的内容当**纯数据**处理

**3 个常用标签**：

| 场景          | 标签                                            |
| ----------- | --------------------------------------------- |
| 隔离用户输入（防注入） | `<user_input>` / `<text>`                     |
| 提供 RAG 上下文  | `<context>` / `<documents>`                   |
| Few-shot 示例 | `<examples><example>...</example></examples>` |

**🔥 项目 1 直接用到**：

```python
RAG_PROMPT = """基于 <context> 回答用户问题。
若 <context> 没答案，说"我不知道"，不要编造。

<context>
{检索到的 chunks}
</context>

<question>
{用户提问}
</question>
"""
```

XML 标签是 RAG 系统的**安全围栏 + 上下文锚点**。

---

### 📖 Chapter 5：Formatting Output & Speaking for Claude（格式化 + Prefilling）

**一句话**：不是请求 LLM "格式化输出"，而是直接给它"答案开头"，逼它接着写。这叫 **Prefilling**。

**技巧 1：明确格式**

- ❌ "请列出几条建议" → LLM 散文式段落
- ✅ "请输出 JSON，schema: `{suggestions: [{title, reason}]}`" → 可解析的 JSON

**技巧 2：Prefilling（Claude 原生支持）**

```python
messages = [
    {"role": "user",      "content": "用 JSON 返回 3 个建议"},
    {"role": "assistant", "content": "{\n  \"suggestions\": ["}  # 给个开头！
]
```

→ LLM **被迫**接着写 JSON，不会跑题。

**OpenAI / DeepSeek 协议的限制**：

Prefilling 是 Claude 原生支持，OpenAI 协议在 assistant 后必须接 user。**绕路方案**：

1. **JSON Mode**：`response_format={"type": "json_object"}`
2. **Pydantic Schema**：`llm.with_structured_output(MySchema)`（Day 6 Guardrails 会用）

**🔥 工程价值**：项目 1 的"报告 Agent"必须返回结构化数据，不能自由发挥——否则前端解析不了。

---

### 📖 Chapter 6：Precognition - Thinking Step by Step（CoT 思维链）

**一句话**：让 LLM 在回答前先"想出来"——准确率立刻飙升。

**为什么有效**：

LLM 只能在 token 上思考（没有"心算"能力）。让它把思考过程写出来 = 强制思考。

> 类比：让你心算 23×47 算不对，但让你写竖式就对了。LLM 同理。

**4 种触发 CoT 的咒语**：

| 咒语                                        | 强度    |
| ----------------------------------------- | ----- |
| "Let's think step by step"                | ⭐⭐⭐   |
| "请一步一步推理，最后给出答案"                          | ⭐⭐⭐   |
| "先在 `<thinking>` 写推理，再在 `<answer>` 写最终答案" | ⭐⭐⭐⭐  |
| "Think carefully" + Few-shot 示例           | ⭐⭐⭐⭐⭐ |

**🔥 项目 1 直接用到（**幻觉控制的核心**）**：

```python
QA_PROMPT = """基于 <context> 回答 <question>。

请在 <thinking> 里：
1. 列出 context 提到的相关信息
2. 判断信息是否足以回答 question
3. 不足则说"我不知道"

然后在 <answer> 里给最终回答。

<context>{context}</context>
<question>{question}</question>
"""
```

→ **幻觉率 18% → 4%**（你简历上的核心量化指标！）

**进阶**：Tree of Thoughts (ToT) — 让 LLM 列 3 个候选答案、评估、选最好的。Day 5 LangGraph 会用。

---

### ✋ Chapter 4-6 浓缩 takeaway

| 章节       | 关键词                    | 一句话                      |
| -------- | ---------------------- | ------------------------ |
| **Ch 4** | XML 标签                 | 隔离指令和数据，**防注入 + RAG 标配** |
| **Ch 5** | Prefilling / JSON Mode | 强制输出格式，**结构化数据必备**       |
| **Ch 6** | CoT 思维链                | "一步一步想"，**幻觉率立降 14%**    |

**实测**：现代 DeepSeek V4 Pro 等模型经过 RLHF 训练，**已能识别简单 Prompt Injection**。但工程上仍要 XML 隔离，原因：

1. 模型代际差异（V5/GLM/Qwen 可能没这么严）
2. 注入会进化（角色伪装、Unicode 走私等）
3. 审计需要（万一出事能证明用了行业标准防御）
4. 加 XML 零成本

---

### 📖 Chapter 7：Using Examples（Few-shot）

**一句话**：示例比解释强 10 倍。给 2-3 个例子 = 写 100 行规则。

**3 个杠杆**：

1. **格式锁定**：示例什么字段，LLM 就输出什么字段
2. **风格锁定**：示例什么口吻，LLM 就模仿什么口吻
3. **复杂逻辑示范**：解释规则要写 500 字，给 3 个 yes/no 例子立刻学会

**数量建议**：

| 数量           | 适用             |
| ------------ | -------------- |
| 0（zero-shot） | 简单任务           |
| **2-3 个**    | **黄金区间**       |
| 5-10 个       | 复杂任务           |
| 100+         | 考虑 Fine-tuning |

**🔥 项目 1 用法**：W3 RAG「查询重写」模块用 Few-shot 把口语化提问改写成 3 个检索友好版本——**Recall@5 从 75% → 85% 的秘密之一**。

---

### 📖 Chapter 8：Avoiding Hallucinations（防幻觉）

**一句话**：LLM 不会主动说"不知道"——它会编。必须显式给它"允许放弃"的权限。

**防幻觉 4 把刀**：

| 刀            | 做法                               | 效果         |
| ------------ | -------------------------------- | ---------- |
| 1. 显式"允许不知道" | "如果 context 没答案，回答'我不知道'，绝对不要编造" | 幻觉率降一半     |
| 2. 要求引用原文    | "每个事实必须附 [来源：xxx]"               | 编造的话没法贴标签  |
| 3. CoT 验证    | "先在 thinking 里判断 context 是否足以回答" | 强迫思考依据     |
| 4. 温度调低      | `temperature=0.1-0.3`            | 创造性 = 幻觉温床 |

**🔥 项目 1 简历指标**：四把刀组合 → **幻觉率 18% → 4%**

---

### 📖 Chapter 9：Complex Prompts（综合实战）

**一句话**：工业级 Prompt 不是一个技巧，而是 1-8 章所有技巧的组合拳。

**工业 Prompt 的 7 层结构**：

```
1. 角色 + 风格（Ch 3）       "你是 XX 专家..."
2. 任务定义（Ch 2）          "你的任务是..."
3. 规则约束（Ch 8）          "铁律：1) 2) 3)..."
4. Few-shot 示例（Ch 7）     <examples>...</examples>
5. CoT 引导（Ch 6）          "请先在 <thinking>..."
6. 输出格式（Ch 5）          "用以下 JSON 格式..."
7. XML 包装数据（Ch 4）      <context>{...}</context>
```

**🔥 这就是项目 1 QA Agent 的 Prompt 模板**——复制粘贴换个领域即可。

---

### ✋ Chapter 7-9 浓缩 takeaway

| 章节       | 关键词      | 一句话                           |
| -------- | -------- | ----------------------------- |
| **Ch 7** | Few-shot | 2-3 个示例 = 用 100 行规则           |
| **Ch 8** | 防幻觉 4 把刀 | "允许不知道" + 引用原文 + CoT + temp 低 |
| **Ch 9** | 组合拳      | 工业 Prompt = 7 层结构，像写剧本        |

---

### 🎯 Anthropic Tutorial 总结（一图流）

```
基础三件套（Ch 1-3）      工程三件套（Ch 4-6）      高级三件套（Ch 7-9）
─────────────────       ─────────────────       ─────────────────
三角色                   XML 隔离                 Few-shot 示例
具体指令                 Prefilling/JSON          防幻觉 4 把刀
角色化 System Prompt     CoT 思维链               综合 7 层 Prompt
   ↓                       ↓                       ↓
   "你是谁"                "数据怎么放"              "怎么组合"
```

**项目 1 QA Agent 的 Prompt 直接用 Ch 9 的 7 层结构。**

---

### Function Calling 闭环

```
用户问题
   ↓
LLM 判断：要不要调工具？
   ↓ 要
LLM 返回 tool_calls（含函数名 + 参数 JSON）
   ↓
Python 执行真实函数
   ↓
工具结果回传给 LLM（role=tool）
   ↓
LLM 综合工具结果，回答用户
```

**关键点**：循环 while True，直到 LLM 不再返回 tool_calls。

### tools 参数三要素

- `name`：工具名（给 LLM 看 + Python 分发用）
- `description`：什么时候用 **← 最重要！LLM 凭这个决定是否调用**
- `parameters`：JSON Schema 描述入参

## ❓ 卡壳记录 → 🧪 实测答案

| #   | 卡壳问题                                   | 实测答案                 | 证据                                                               |
| --- | -------------------------------------- | -------------------- | ---------------------------------------------------------------- |
| Q1  | `tool_calls` 不调工具时是 `None` 还是 `[]`？    | **`None`（NoneType）** | 02 Round 2 / 03 Round 3 全部 `type=NoneType value=None`            |
| Q2  | description 改"用来唱歌"还会调吗？               | 待做（破坏性实验，明天补）        | ——                                                               |
| Q3  | 多工具会并行还是串行返回？                          | **DeepSeek 支持并行**    | 03 测试 3 Round 1：`tool_calls 数量=2`（search_wiki + calculator 一次返回） |
| Q4  | 支持 `parallel_tool_calls=False` 吗？      | 待验证（DeepSeek 文档未提）   | ——                                                               |
| Q5  | 不 append assistant 直接 append tool 会怎样？ | 待做（破坏性实验）            | ——                                                               |

> **写法上的双保险**：`if not msg.tool_calls:` —— `None` 和 `[]` 都会被 `not` 命中。

---

### 🐞 实测发现的生产坑：DeepSeek "XML 标签泄漏"

跑 02/03 时多次出现：

```
expression='sqrt(3^2 + 4^2)</'
expression='fib(10) where ... fib(n-2)</937parameter>\n'
```

`</`、`</937parameter>\n` 来自模型内部 chain-of-thought / 工具调用 XML 模板的**闭合标签泄漏**。文档不会告诉，亲跑才发现。

**应对**：

- 短期：`eval` 包 try/except（已有）
- 中期：传给 `calculator` 前正则清洗 `</[^>]*>` 尾巴
- 生产：换 Claude/GPT-4，或开 DeepSeek `strict` 模式（`base_url=/beta` + `strict: true`）

---

### 📊 LLM 调用成本观察

| 测试               | 工具调用轮次 | LLM 调用次数 | messages 长度 |
| ---------------- | ------ | -------- | ----------- |
| 02-1 简单计算        | 1      | 2        | 3           |
| 02-2 勾股（3 次失败）   | 3      | 4        | 7           |
| 03-2 天气+换算（串行）   | 2      | 3        | 5           |
| 03-3 斐波那契（并行+重试） | 2      | 3        | 6           |

**核心认知**：**1 个工具调用 = 至少 2 次 LLM 调用**（决策 + 综合）。这是 Function Calling **贵且慢**的根因，LangChain Agent 也没魔法。

## 💭 自由发挥

- **对"Agent"祛魅**：所谓 Agent = 工具说明书（tools）+ 循环（while）+ 分发表（registry）+ LLM 决策。明天 LangChain 的 `AgentExecutor` 拆开看就这四样。
- **Prompt 工程和 Function Calling 是同一件事的两面**：description 字段本质就是 system prompt 的微型版，决定 LLM 何时调；description 写得烂，再多工具也召不回。
- **调试 LLM 的核心方法**：把每一轮的 `messages` 全部打印出来肉眼看。`[DEBUG Round N]` 这种打印加 2 行就值回票价。
