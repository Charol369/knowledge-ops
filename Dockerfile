# KnowledgeOps · 应用镜像
# 基于 uv 官方推荐的多阶段构建

FROM python:3.11-slim AS builder

# 装 uv（最快的 Python 包管理器）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 装依赖（利用 Docker 层缓存：pyproject.toml + uv.lock 没变就不重跑 sync）
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 拷业务代码
COPY src ./src
COPY scripts ./scripts

# =============== Runtime ===============
FROM python:3.11-slim

WORKDIR /app

# 拷预装好的 venv（节省 50%+ 镜像体积）
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/scripts /app/scripts

# 配置环境
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
