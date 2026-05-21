# Day 4 笔记 — 5/21 周四

> **目标**：4 小时通读 all-in-rag 教程建立 RAG 全景认知 + 跑通第一个 PDF 问答

## ✅ 完成情况

- [x] all-in-rag 1-4 章速览（解锁 RAG / 数据加载分块 / 嵌入与向量库 / 混合检索）
- [x] `uv add langchain-milvus pymilvus[milvus-lite] sentence-transformers pypdf langchain-huggingface langchain-text-splitters` 装齐 RAG 全家桶（torch 2.10 / transformers 5.9 / sentence-transformers 5.5）
- [x] 下载 `data/attention_is_all_you_need.pdf`（arxiv 1706.03762，15 页）作为测试样本
- [x] `01_pdf_rag.py` 跑通端到端：PDF → split (93 块) → embed (BAAI/bge-small-en-v1.5, 384 维) → FAISS → retriever → LCEL chain → DeepSeek
- [x] 3 个测试问题全部通过：Transformer 架构（英文 → 英文）/ multi-head attention（中文 → 中文跨语言）/ Paris 防幻觉（PDF 外 → `I don't know`）
- [x] `.gitignore` 追加 `data/` / `*.db` / `faiss_attention/`
- [x] commit 入库（`7c5d85c`）

## 🎯 今天 AHA Moment

**一句话**：第一次端到端跑通 RAG，**七步走的物理过程**清晰可触：

```
PDF (15 页) → split (93 块) → embed (384 维, 8.4s)
            → FAISS 入库 (6.2s) → retriever (Top-3)
            → format_docs → prompt → LLM → 答案
```

最震撼的是 **跨语言 RAG**：英文 PDF + 中文问题 → 中文答案，LLM 给出 `h=8 / d_k=d_v=d_model/h=64` 的公式。RAG 不是"语言转换"，而是 **"语义对齐"**——embedding 把同一概念的中英文映射到相近向量，LLM 看到检索出的英文 chunks 自然能用中文复述。

**第二个 AHA**：防幻觉 prompt 那一句 `"Answer based ONLY on context. If not, say 'I don't know' — do not make things up."`——**24 个字符**让 LLM 对 `What is the capital of France?` 老老实实答 `I don't know`，哪怕 PDF 里出现了 `English-to-French translation` 这种诱导词。**这是 RAG 里最值钱的一行 prompt engineering**。

**第三个 AHA / 反直觉**：教程示范的 **Milvus Lite 没跑通**（兼容 bug，下方有详述），换成 **FAISS 反而一行 import 就跑通了**。VectorStore 抽象层的真正价值，在切换底层时才体现出来——LangChain 抽象让 vector store 像 USB 接口一样可热插拔。

## 🔑 核心概念

### RAG 全景认知（一图流）

```
============ 离线建库 ============           ============ 在线查询 ============
原始文档（PDF/Word/网页）                       用户提问
   ↓ 数据加载（Document Loader）                   ↓
段落 / 章节                                   嵌入（必须同一个 Embedding Model！）
   ↓ 分块（Text Splitter）                        ↓
chunks（典型 500-1000 字符）                   查询向量
   ↓ 嵌入（Embedding Model）                      ↓ 相似度搜索（Top-K）
N 维向量（384 / 768 / 1024）                  最相关的 K 个 chunks
   ↓ 入库（Vector Store）                         ↓ 塞进 Prompt
向量库                                        LLM 生成最终回答
```

**为什么必须同一个 embedding 模型**：不同模型把同一段话映射到**不同的语义空间**（甚至维度都不同：bge-small 384 维，bge-large 1024 维）。即使维度一样，两个模型的"狗"向量也指向不同方向，余弦相似度毫无意义。

**面试金句**：*"Embedding 模型本质是把文本编码到学习到的语义空间，离线建库和在线查询如果用不同模型，就像用英文字典查中文词——空间不对齐，相似度计算等于随机数。"*

### RAG 三阶段演进（**必背面试图**）

| 阶段 | 流程 | 关键技术 |
|---|---|---|
| **Naive RAG**（今天做的） | 索引 → 检索 → 生成 | 基础向量检索 |
| **Advanced RAG**（W3 项目期） | 索引 → **查询重写** → 检索 → **Rerank** → 生成 | HyDE / Cross-Encoder / Query Expansion |
| **Modular RAG**（W4-W5 项目期） | 路由 / 融合 / 自我修正等积木式 | LangGraph + Multi-Agent + Self-RAG |

**我的项目 1 最终目标 = Modular RAG**（技能图谱里 RAG"高薪点"的核心）。

**面试金句**：*"我的项目 1 最终是 Modular RAG，用 LangGraph 把 query rewrite / multi-retriever fusion / self-correction 等模块编排成状态机，而不是写死的线性 chain。"*

### 分块策略对比（**面试常问**）

| 策略 | 优点 | 缺点 |
|---|---|---|
| 固定字符 | 简单 | 可能切断句子 |
| **递归字符**（默认推荐，今天用的） | 优先按段落/句子切，保持语义 | -- |
| 语义分块 | 最贴近语义 | 慢、贵 |
| Token-based | 控制 Token 数 | 需 tokenizer |

**关键参数**：`chunk_size` + `chunk_overlap`

| chunk_size | 优点 | 缺点 |
|---|---|---|
| 小（100-200） | 精确定位 | 上下文不足；概念被切碎；检索 N 多块凑答案 |
| **中（500-1000，主流）** | 既有上下文也精确 | -- |
| 大（1500+） | 上下文完整 | 噪音多；embedding 失焦；prompt 占 token 多 |

**经验法则**：
- 知识密度高的文档（论文、技术 wiki）→ `chunk_size 300-500`（今天用 500）
- 叙事性文档（小说、新闻）→ `chunk_size 800-1500`
- 极短结构化数据（FAQ、产品参数）→ 一条一块，不用 splitter
- `chunk_overlap = chunk_size × 10-20%`（今天 500/50）

**overlap 设 0 的后果**：句子可能恰好被切在两块边界（如 *"Transformer is | based on attention"*），单独一块语义不全。Top-K 可能因为相邻块各掉一半上下文而漏关键信息。

### 嵌入模型选型

| 模型 | 语种 | 大小 | 维度 | 适合 |
|---|---|---|---|---|
| `bge-small-zh-v1.5` | 中文 | 100MB | 512 | 中文文档 baseline |
| `bge-small-en-v1.5` | 英文 | 130MB | 384 | **今天用的**（英文论文） |
| `bge-large-zh-v1.5` | 中文 | 1.3GB | 1024 | 准确率优先 |
| `bge-m3` | 多语种 | 2.3GB | 1024 | 项目 1 正式版 + 中英文混合 |
| `text-embedding-3-small` | OpenAI | 云端 | 1536 | 不想自己跑模型，付钱给 API |

### 为什么 `normalize_embeddings=True`

向量"归一化"= 把每个向量除以模长，变成单位长度（模 = 1）。

| 距离度量 | 没归一化 | 归一化后 |
|---|---|---|
| 余弦相似度 | `cos = A·B / (‖A‖·‖B‖)`（要算分母） | `cos = A·B`（直接内积，省一步） |
| L2 距离 | 受向量长度影响 | `L2² = 2 - 2·A·B`，单调等价于内积 |
| 内积（IP） | 不等同余弦 | 等同余弦 |

**为什么实战必开归一化**：
1. **省计算**：内积 = 余弦，向量库的 IP 索引（HNSW-IP / FAISS IndexFlatIP）比 L2 索引在某些硬件上更快
2. **语义稳定**：BERT 系模型的输出向量长度本身会随文本长度变化（**长度是噪音**），归一化后只比"方向"

### Top-K 的取舍

| K | 优点 | 缺点 |
|---|---|---|
| 小（K=3，**今天用的**） | prompt 短、token 省、噪音少；LLM 焦点集中 | 漏检风险（答案块没进 Top-3） |
| 大（K=10+） | 召回更全 | prompt 膨胀（10 × 500 = 5000 字符上下文）；LLM 被无关块干扰；成本上升 |

**进阶组合**（W3 会做）：**先大 K 召回，再 Rerank 精排到小 K**——`K_retrieve=20` → Cross-Encoder rerank → 取 Top-3 进 prompt。既提高召回又控制噪音。

### Milvus 索引类型（面试常问）

| 索引 | 原理 | 速度 | 内存 | 适合 |
|---|---|---|---|---|
| **FLAT** | 精确暴力搜索 | 慢 | 小 | 万级以下数据 |
| **HNSW** | 图索引（近似最近邻） | 快、召回高 | 大 | 百万级 |
| **IVF_FLAT** | 倒排+聚类 | 中 | 中 | 千万级 |
| **IVF_PQ** | IVF + 向量压缩 | 中 | **极小** | 亿级 |

生产 RAG baseline → HNSW；超大规模 → IVF_PQ。

### 防幻觉 prompt 设计（**面试和项目核心**）

```python
prompt = """
Answer the question based ONLY on the following context.
If the context does not contain the answer, say "I don't know"
— do not make things up.

Context:
{context}

Question: {question}
"""
```

**今天实测**：问 `What is the capital of France?`（PDF 里没答案但是常识题），LLM 答 `I don't know`，不答 `Paris`，哪怕 PDF 里出现了 `English-to-French translation` 这种诱导词。

**进阶**（项目 1 用）：
- 强制引用 source citation（每个事实标 `[page X]`，便于审计回溯）
- CoT 验证（`<thinking>` 先判断 context 是否足以回答）
- 温度调低（`temperature=0.1-0.3`）

四把刀组合 → **幻觉率 18% → 4%**（简历的核心量化指标）。

## ❓ 卡壳记录 → 🧪 实测答案

| # | 卡壳问题 | 实测答案 | 证据 |
|---|---|---|---|
| Q1 | `chunk_overlap` 设 50 还是 200？ | 经验值 = `chunk_size × 10-20%`。500/50 对论文足够 | 今天 93 块跑通，retrieval Top-3 准确率合理 |
| Q2 | 多个 PDF 入同一个 collection 怎么区分来源？ | 用 metadata：`Document(page_content=..., metadata={"source": "doc_A.pdf", "page": 3})`，检索后 `doc.metadata["source"]` 即来源 | LangChain Document schema |
| Q3 | Milvus 的 HNSW 和 IVF 区别？ | HNSW 图索引（快+召回高+内存大）；IVF 倒排聚类（中速+省内存）。万级 FLAT、百万级 HNSW、亿级 IVF_PQ | Milvus 官方文档 |
| Q4 | 为什么 `normalize_embeddings=True`？ | 归一化让内积 = 余弦相似度，省一步；BERT 输出长度随文本长度变化是噪音，归一化后只比方向 | 今天默认开启 |
| Q5 | RAG 答错了，根因怎么排查？ | (1) 看 retriever 返回的 chunks 对不对（答案块没召回 → 改 chunk_size / Top-K / Rerank）；(2) chunks 对但答案错（LLM 没读懂 → 改 prompt 或换模型） | 我在脚本里加了 `[DEBUG] 检索到的 Top-K chunks` 输出，方便定位 |
| Q6 | `langchain-milvus 0.3.3 + pymilvus 2.6 + milvus-lite` 报 `ConnectionNotExistException: should create connection first.` | 见下方"🐞 兼容 bug 详解" | 实测 + stack trace |
| Q7 | 跨语言 RAG 工作原理？为什么英文 embedding 模型能匹配中文问题？ | embedding 模型即使是英文版（bge-small-en），训练时见过部分多语言数据，对"multi-head attention"和"多头注意力"仍能映射到相近向量。生产用 `bge-m3`（多语言）效果更好 | 今天实测：英文 PDF + 中文问题 → 中文答案 |

### 🐞 工程教训：Milvus Lite → FAISS 切换决策（**面试核心案例**）

**症状**：跑 `Milvus.from_documents(...)` 报：
```
pymilvus.exceptions.ConnectionNotExistException:
should create connection first.
```

**根因**：`langchain-milvus 0.3.3` 内部 `col` 属性走 ORM 风格 `Collection(name, using=alias)`，需要全局 `connections` 池注册；但 `MilvusClient(uri="./milvus_demo.db")` 走的是新机制**不注册全局**——二者撕裂。

**尝试过的修复路径**：
| 方案 | 结果 |
|---|---|
| A. `uv add "pymilvus[milvus_lite]"` extras 写法 | extras 没真正生效，缺 `milvus_lite` 模块 |
| B. `uv add milvus-lite` 独立装 | MilvusClient 能建立，但 ORM 路径仍报错 |
| C. 显式 `connections.connect(alias="default", uri=MILVUS_URI)` | 仍失败，外加 `AsyncMilvusClient._get_connection coroutine never awaited` warning |
| **D. 换 FAISS** ✅ | **一行 import 切完，跑通** |

**决策逻辑**：
1. W1 速成期不该陷在版本兼容里
2. FAISS 已经被 milvus-lite 当依赖装好了（无额外装包成本）
3. FAISS 工业级（Meta 出品，Milvus 底层也用它），langchain 集成稳定
4. `Day 4 文档里"用 Milvus Lite"的核心诉求是"无需 Docker"`——FAISS 同样满足
5. W2-W3 项目期切真正的 Milvus standalone（Docker 版）时，**只改 3 行代码**

**这就是 LangChain VectorStore 抽象的价值——切换底层 vector store 几乎零成本**。

**面试金句**：*"我评估过 langchain-milvus 0.3 + pymilvus 2.6 的集成 bug——milvus-lite 模式下 ORM 连接池和 MilvusClient 撕裂。W1 速成期 FAISS 是务实选择，W3 项目期上 Milvus standalone 再切，VectorStore 抽象层让切换成本可控。"*——这就是工程师做技术选型的真实流程，比"用了 Milvus"更有内容可讲。

### 📊 性能瓶颈拆解（脚本里的 stopwatch 数据）

| 阶段 | 耗时 | 一次性 / 每次 |
|---|---|---|
| PyPDFLoader.load | 1.5s | 一次性，可缓存 |
| split_documents | <0.01s | CPU 极快 |
| HuggingFaceEmbeddings init | 8.4s | 一次性（torch 启动） |
| embed 93 块 + FAISS 索引 | 6.2s | 一次性 |
| FAISS.save_local | 0.02s | 一次性 |
| **单次 RAG invoke（检索 + LLM）** | **1.8-9.1s** | **每次（LLM 主导）** |

**性能优化顺位**：
1. **embed 缓存**：`FAISS.save_local(...)` + `FAISS.load_local(...)` 跳过 embed 阶段（最大头）
2. **LLM 流式输出**：用户感知延迟下降
3. **Rerank**：先大 K 召回 → Cross-Encoder 精排到 Top-3（W3 做）
4. **批处理 embedding**：sentence-transformers 默认 batch_size=32，长文档可调大

## 💭 自由发挥

- **跨语言 RAG 的语义对齐威力**：今天最让我震撼的不是 LLM 能用中文答出 `h=8`，而是检索能 work——`bge-small-en-v1.5` 是英文模型，但仍把"multi-head attention"和"多头注意力"映射到相近向量。**未来项目 1 用 `bge-m3` 多语言模型会更稳**，但即使是单语言模型也有相当跨语言能力，这超出了我的预期。
- **防幻觉 prompt 的 ROI 极高**：24 个字符让 LLM 老实，**这是性价比最高的 prompt engineering**。生产上还可以加 source citation（要求 LLM 每个事实标 `[page X]`），让用户能回溯，也方便人工审计。
- **VectorStore 抽象的价值在切换时才体现**：今天 Milvus → FAISS 这个切换，让我深刻理解为什么 LangChain 把 VectorStore 做成 abstract base class——业务代码不该绑死底层向量库。**这就是 12-factor app 的 "Backing services as attached resources" 在 RAG 里的实现**。
- **Hugging Face 模型下载首次会慢**：首次跑 `HuggingFaceEmbeddings(...)` 下载 `bge-small-en-v1.5` 用了约 30s（含网络）；二次跑缓存命中只 8s（torch 启动）。生产部署要预热模型 cache，不能让用户等首次冷启。
- **`langchain-milvus` 的 bug 不会很快被官方修**：因为 deprecation warning 已经说 `Collection` ORM API 将在 PyMilvus 3.1 删除——这种夹在两套 API 之间的状态会持续到 langchain-milvus 重写。W3 项目期我会用 Milvus standalone (gRPC 模式，不是 milvus-lite)，那条路径稳定。
- **今天 7 小时的"全周最重的一天"我用了 4 小时**——主要是装包（torch 108MB）和兼容 bug 排错。如果按文档原样照搬 Milvus Lite，估计今天交差不了。**踩坑这件事本身就是 W1 的隐藏交付物**——把"我评估过 X 方案的 Y bug，所以选了 Z"这种故事讲给面试官，比"我用了 Milvus"权重高 10 倍。
- **Day3 + Day4 一天补做完**：连续两天的速成压力可控，主要是因为 Day3 装包顺手装了 Day4 的 RAG 全家桶（torch + sentence-transformers + langchain-huggingface + pypdf 等），下午开 Day4 就不用再 `uv add` 了。**装包合批是补做日的小窍门**。

## 📅 明日预告

**Day 5 - LangGraph + Multi-Agent 概念**

明天进入 Agent 主题：
- **LangGraph**：把"线性 Chain"升级成"带分支 / 循环 / 状态"的图（也是 LangChain 1.x Memory & Agent 的新家）
- **ReAct 模式**：Reasoning + Acting 的经典 Agent 模式
- **Multi-Agent**：多个 Agent 协作（项目 1 的 QA / Summary / Report 三个 Agent 就是这个范式）

**提前装好的包**：`langgraph 1.2.0` 已经被 Day3 的 `langchain` 拉成依赖装齐，明天不用再装。
