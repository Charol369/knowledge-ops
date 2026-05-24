"""嵌入模型封装

Sprint 1 baseline：bge-small-en/zh-v1.5（Day4 已用过）
Sprint 2 升级：bge-m3 多语言 1024 维（架构图设计的目标模型）
"""
from langchain_huggingface import HuggingFaceEmbeddings
from src.config import settings


def get_embedder(model_name: str | None = None) -> HuggingFaceEmbeddings:
    """统一的 embedder 入口。normalize_embeddings=True：内积即余弦相似度（Day4 笔记）"""
    return HuggingFaceEmbeddings(
        model_name=model_name or settings.embed_model,
        encode_kwargs={"normalize_embeddings": True},
    )


# TODO Sprint 1: embed_documents 批量接口（用于离线建库）
# TODO Sprint 1: embed_query 单条接口（用于在线查询）
# TODO Sprint 4: 加 redis cache 避免重复 embedding（query 重复率高的场景）
