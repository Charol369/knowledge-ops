"""Day4 - 端到端 PDF RAG Hello World

七步走：PDF → 分块 → 嵌入 → 入库 → 检索 → 拼 Prompt → LLM 生成

本脚本对 Day4 文档示范的调整：
1. 用 Attention Is All You Need（英文 PDF）→ 配 BAAI/bge-small-en-v1.5（英文 embedding）
   而不是文档示范的中文 bge-small-zh-v1.5——embedding 语种要和文档语种一致才准
2. ⚠️ 用 FAISS 替代 Milvus Lite（Day4 文档示范的本地选项）。
   原因：langchain-milvus 0.3.3 + pymilvus 2.6 在 milvus-lite 模式下有兼容 bug
   （内部 col 属性走 ORM 风格 Collection(name, using=alias)，需要全局 connections 池注册，
    但 MilvusClient(uri=...) 新机制不注册，二者撕裂）。
   FAISS 已经被 milvus-lite 当依赖装好，工业级，langchain 集成稳定。
   Day4 用 Milvus Lite 的核心诉求是"无需 Docker"，FAISS 一样满足。
   W2-W3 项目期切真正的 Milvus standalone（Docker 版）时，只需改 3 行代码——
   这正是 LangChain VectorStore 抽象的价值。
3. 增加分阶段耗时统计，让 Boss 直观看到 RAG 的性能瓶颈

⚠️ 首次运行：bge-small-en-v1.5 约 130MB，会从 HuggingFace 下载
   如果下载失败，把下面 HF_ENDPOINT 注释取消即可走 hf-mirror.com 国内镜像
"""
import os
import sys
import time

# 国内访问 HuggingFace 不稳时取消下面这行注释切镜像
# os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


# ============== 0. 配置 ==============
PDF_PATH = "data/attention_is_all_you_need.pdf"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"   # 英文 PDF 用英文 embedding
FAISS_INDEX_DIR = "./faiss_attention"    # FAISS 本地持久化目录
TOP_K = 3


def stopwatch(label: str):
    """简单计时上下文：with stopwatch('xxx'): ..."""
    class _Ctx:
        def __enter__(self):
            self.t0 = time.perf_counter()
            return self

        def __exit__(self, *_):
            dt = time.perf_counter() - self.t0
            print(f"    ⏱  {label} 耗时 {dt:.2f}s")
    return _Ctx()


# ============== 1. 数据加载 ==============
print(f"📄 加载 PDF：{PDF_PATH}")
with stopwatch("PyPDFLoader.load"):
    docs = PyPDFLoader(PDF_PATH).load()
print(f"   共 {len(docs)} 页，首页前 80 字符预览：")
print(f"   {docs[0].page_content[:80].strip()}...")


# ============== 2. 文本分块（RecursiveCharacterTextSplitter）==============
# chunk_size=500：每块约 500 字符（不是 token），适合大多数中长 chunk 场景
# chunk_overlap=50：相邻块重叠 50 字符，避免在句子中间切断丢失语义
# 递归策略：先按 \n\n（段落）切，再 \n（行）、空格、字符，优先保持语义完整
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)
with stopwatch("split_documents"):
    chunks = splitter.split_documents(docs)
print(f"✂️  切成 {len(chunks)} 块，平均每块 {sum(len(c.page_content) for c in chunks) // len(chunks)} 字符")


# ============== 3. 嵌入模型 ==============
# normalize_embeddings=True：把向量归一化到单位长度
#   → 内积 = 余弦相似度（少一步计算 + 多数向量库支持 IP 索引更快）
# 首次跑：模型下载到 ~/.cache/huggingface/hub/，约 130MB
print(f"🧠 加载 embedding 模型：{EMBED_MODEL}")
with stopwatch("HuggingFaceEmbeddings init"):
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )


# ============== 4. 入库（FAISS 本地向量库）==============
# FAISS.from_documents 会：
#   1. 对每个 chunk 调用 embeddings.embed_documents → 得到 384 维向量
#   2. 在内存建 FAISS 索引（默认 IndexFlatL2，brute-force L2 距离）
#   3. 返回 vectorstore 对象，里面同时存了向量 + 原文 chunks + metadata
# save_local 持久化到磁盘，下次跑可以用 FAISS.load_local 秒级加载，跳过 embed
print(f"💾 入库到 FAISS（in-memory + 持久化到 {FAISS_INDEX_DIR}）")
with stopwatch("FAISS.from_documents（含 embed 全部 chunks）"):
    vectorstore = FAISS.from_documents(chunks, embedding=embeddings)

with stopwatch("FAISS.save_local"):
    vectorstore.save_local(FAISS_INDEX_DIR)


# ============== 5. 检索器 ==============
# search_kwargs={"k": 3}：每次返回相似度 Top-3 的 chunks
# 也可以传 search_type="mmr" 用 Maximal Marginal Relevance 去重
retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})


# ============== 6. RAG Chain ==============
llm = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)

# Prompt 模板：明确告诉 LLM "上下文里没答案就说不知道"
# → 防止 LLM 自由发挥编造（hallucination）
prompt = ChatPromptTemplate.from_template("""
You are a helpful research assistant. Answer the question based ONLY on the following context.
If the context does not contain the answer, say "I don't know" — do not make things up.
Answer in the same language as the question.

Context:
{context}

Question: {question}

Answer:
""")


def format_docs(docs):
    """把多个检索到的 chunks 用空行分隔拼成一段文本"""
    return "\n\n".join(d.page_content for d in docs)


# RunnablePassthrough：把 invoke 的输入原样塞到字典的 question 字段
# {"context": retriever | format_docs, "question": RunnablePassthrough()}
#   → invoke("xxx") 时
#     · context  = format_docs(retriever.invoke("xxx"))
#     · question = "xxx"
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


# ============== 7. 问答 ==============
questions = [
    "What is the Transformer architecture? Why was it proposed instead of using RNN or CNN?",
    "请用中文解释什么是 multi-head attention，以及为什么需要它。",
    "What is the capital of France?",  # PDF 里没答案，验证防幻觉
]

for q in questions:
    print("\n" + "=" * 70)
    print(f"❓ {q}")
    print("=" * 70)

    with stopwatch("rag_chain.invoke（检索 + 生成）"):
        answer = rag_chain.invoke(q)
    print(f"\n💡 回答：\n{answer}")

    # [DEBUG] 把检索到的 chunks 也打出来，让 Boss 看 RAG 内部
    print(f"\n📚 [DEBUG] 检索到的 Top-{TOP_K} chunks（每块前 150 字符预览）：")
    for i, doc in enumerate(retriever.invoke(q), 1):
        preview = doc.page_content[:150].replace("\n", " ").strip()
        page = doc.metadata.get("page", "?")
        print(f"  [{i}] page={page} | {preview}...")
