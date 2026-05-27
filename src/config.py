"""项目配置中心。

所有全局可调参数都集中在这里，避免在业务代码里散落 os.getenv。
新的项目原则要求把模型路由、上下文工程和 artifact 持久化也纳入统一配置。
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    deepseek_api_key: str
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    cheap_model: str = "deepseek-chat"
    primary_model: str = "deepseek-chat"
    premium_model: str = "claude-4-7"
    model_router_enabled: bool = True

    embed_model: str = "BAAI/bge-m3"

    milvus_uri: str = "./data/milvus_demo.db"
    collection_name: str = "knowledge_ops"

    top_k_dense: int = 10
    top_k_sparse: int = 10
    top_k_final: int = 5
    max_plan_steps: int = 5
    max_reflection_rounds: int = 1

    artifact_root_dir: str = "./artifacts"
    cache_ttl_seconds: int = 3600

    max_tokens: int = 2048
    temperature: float = 0.3

    langsmith_tracing: bool = False
    langsmith_api_key: str = ""
    langsmith_project: str = "knowledge-ops"

    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"


settings = Settings()
