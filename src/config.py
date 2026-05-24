"""项目配置：用 pydantic-settings 从 .env 加载。

所有"全局可配"的参数（API key / 模型名 / 路径 / 超参）必须走这里，
禁止在业务代码里散落 os.getenv("XXX") —— 否则 Sprint 4 加配置中心会撕裂。
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ============== LLM ==============
    deepseek_api_key: str
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # ============== Embeddings ==============
    embed_model: str = "BAAI/bge-m3"

    # ============== Vector DB ==============
    milvus_uri: str = "./data/milvus_demo.db"
    collection_name: str = "knowledge_ops"

    # ============== Retrieval ==============
    top_k_dense: int = 10
    top_k_sparse: int = 10
    top_k_final: int = 5  # rerank 后送给 LLM 的 chunk 数

    # ============== Generation ==============
    max_tokens: int = 2048
    temperature: float = 0.3  # 低温度 = 减少幻觉

    # ============== Observability ==============
    langsmith_tracing: bool = False
    langsmith_api_key: str = ""
    langsmith_project: str = "knowledge-ops"

    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"


settings = Settings()
