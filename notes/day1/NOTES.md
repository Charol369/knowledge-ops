# Day 1 笔记 — 5/18 周一

> **目标**：环境搭建 + LLM API + 流式输出

## ✅ 完成情况

- [x] Python 3.11.15 安装（via uv）
- [x] uv 0.11.14 安装
- [x] Git 2.47.1 配置（user.name = Charol369）
- [x] VS Code 安装
- [x] GitHub 仓库 `knowledge-ops` 创建并 clone
- [x] uv init + 装依赖（openai / fastapi / uvicorn / httpx / python-dotenv）
- [x] DeepSeek API Key 配置到 .env（中转站 `api.zhenhaoji.qzz.io/v1` + `deepseek-v4-pro`）
- [x] `01_hello_llm.py` 跑通（Token 用量 26+77=103）
- [x] `02_stream_cli.py` 流式输出生效（七言绝句一字一字冒出）
- [x] `03_stream_api.py` FastAPI SSE 接口工作（`/health` + `/chat` 端点）
- [x] 首次 commit + push 到 GitHub（commit 0dc3e8f）

## 🎯 今天 AHA Moment

**一句话**：原来"流式输出"在代码层面只差一个 `stream=True`——LLM 协议里所谓的"打字机效果"就是把一次性返回的对象拆成生成器，**前端的炫酷其实是后端约定俗成的 `data: xxx\n\n` SSE 协议**而已。把这件事跑通后，对所有 ChatGPT-like 产品的"实现"瞬间祛魅。

**第二个 AHA**：DeepSeek 直接复用 OpenAI SDK 是"协议兼容"的胜利——不只省了 SDK，所有围绕 OpenAI SDK 的工具链（LangChain、LangSmith、Langfuse 等）都能直接用。**LLM 应用层正在围绕 OpenAI 协议形成事实标准**。

## 🔑 核心概念

### LLM API 三要素

```python
client.chat.completions.create(
    model="...",       # 模型名（中转站用 deepseek-v4-pro）
    messages=[...],    # 对话历史
    stream=True/False  # 是否流式
)
```

### 流式 vs 非流式

| | 非流式 | 流式 |
|---|---|---|
| `stream` | `False`（默认） | `True` |
| 返回 | 完整对象 | 迭代器 |
| 用户感知 | 等待→一次性出现 | 字符逐个冒出 |

### SSE 协议

```
data: 第一段内容\n\n
data: 第二段内容\n\n
data: [DONE]\n\n
```

每行 `data: xxx\n\n`（两个换行结尾）。FastAPI 用 `StreamingResponse(generator, media_type="text/event-stream")` 就能输出。

### 中转站使用要点

- **BASE_URL 必须显式带 `/v1`**：DeepSeek 官方 SDK 内部会自动加，中转站没这个逻辑
- 模型名跟着中转站走（`deepseek-v4-pro` 而非官方 `deepseek-chat`）
- **合规风险**：秋招简历上写"DeepSeek 官方 API"，不要暴露用了中转

## ❓ 卡壳记录（今天的 3 个坑 + 解决方案，**可作面试谈资**）

### ❌ 坑 1：`UnicodeEncodeError: 'gbk' codec can't encode character`

**根因**：Windows PowerShell 控制台默认 GBK 编码，Python `print` emoji 时被 GBK 编码器卡住
**解决**：脚本顶部加
```python
import sys
sys.stdout.reconfigure(encoding="utf-8")
```
**深层教训**：跨平台代码不能假设运行环境编码，**程序自己控制 stdout 编码**才稳

### ❌ 坑 2：`AttributeError: 'str' object has no attribute 'choices'`

**根因**：中转站 `api.zhenhaoji.qzz.io` 不会像 DeepSeek 官方那样自动补 `/v1` 路径，请求被转发到错误端点返回了字符串而非标准 JSON
**解决**：`.env` 里 `DEEPSEEK_BASE_URL=https://api.zhenhaoji.qzz.io/v1`（**显式带 `/v1`**）
**深层教训**：OpenAI SDK 的 `base_url` 行为不同实现间有差异，**用前查文档约定**

### ❌ 坑 3：`IndexError: list index out of range`（流式最后一个 chunk）

**根因**：OpenAI SDK 2.x 流式协议——**最后一个 chunk 的 `choices` 是空列表**（只用来回传 `usage` 统计），不是真正的内容 chunk
**解决**：循环里加防御
```python
for chunk in stream:
    if not chunk.choices:  # 最后一个 usage-only chunk
        continue
    ...
```
**深层教训**：**永远不要假设流式响应每个 chunk 结构相同**，要看 SDK 版本变更日志

### ❌ 坑 4：GitHub push TLS 错

**根因**：国内直连 GitHub 不稳定
**解决**：`git config --global http.proxy http://127.0.0.1:7897`（Clash 代理）

## 💭 自由发挥

- 今天最爽的瞬间是 `02_stream_cli.py` 跑出"指尖流淌一荧屏，代码如波意未停"那一刻——LLM 写诗这事真的有种荒诞的浪漫
- 中转站这种"灰色基建"确实让学习成本变低了，但产生了一种"我在用别人冒着合规风险搭的服务"的微妙感觉。秋招前要 rotate key + 换官方 API
- DeepSeek V4 Pro 写七言绝句还行，但格律不算严——下次试试用 system prompt 强制"按平水韵"看会不会更好
- 6 小时的活我用了大概 2 小时跑通——是不是说明这个学习路径设计得太宽松了？还是说 Day1 本来就是"建立信心"的暖身？

## 📅 明日预告

Day 2：Prompt 工程（Anthropic 官方 Tutorial 3h 跑完）+ Function Calling（计算器 + 天气 mock）。今晚先 clone：

```powershell
cd C:\Users\sundewang\Desktop
git clone https://github.com/anthropics/prompt-eng-interactive-tutorial.git
```
