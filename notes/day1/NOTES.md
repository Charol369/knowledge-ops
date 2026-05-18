# Day 1 笔记 — 5/18 周一

> **目标**：环境搭建 + LLM API + 流式输出

## ✅ 完成情况

- [x] Python 3.11 安装
- [x] uv 安装
- [x] Git 配置
- [x] VS Code 安装
- [x] GitHub 仓库 `knowledge-ops` 创建并 clone
- [x] uv init + 装依赖
- [x] DeepSeek API Key 配置到 .env
- [ ] `01_hello_llm.py` 跑通
- [ ] `02_stream_cli.py` 流式输出生效
- [ ] `03_stream_api.py` FastAPI 接口工作

## 🎯 今天 AHA Moment

```
（晚上 21:00 复盘时填）
```

## 🔑 核心概念

### LLM API 三要素

```python
client.chat.completions.create(
    model="...",       # 模型名
    messages=[...],    # 对话历史
    stream=True/False  # 是否流式
)
```

### 流式 vs 非流式

| | 非流式 | 流式 |
|---|---|---|
| `stream` | `False`（默认） | `True` |
| 返回 | 完整对象 | 迭代器 |
| 用户感知 | 等待→一次性 | 字符逐个冒出 |

### SSE 协议

```
data: 第一段内容\n\n
data: 第二段内容\n\n
data: [DONE]\n\n
```

每行 `data: xxx\n\n`（两个换行结尾）。

## ❓ 卡壳记录

```
（遇到问题写这里，不要原地深挖）
```

## 💭 自由发挥

```
```
