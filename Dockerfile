# vBot 镜像：基于官方 python:3.11-slim，体积小、依赖少
FROM python:3.11-slim AS runtime

# 防止 Python 写入 .pyc、强制 stdout 不缓冲
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/src

# 仅安装 ca-certificates，减小镜像体积
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先复制依赖清单，利用 Docker 缓存
COPY requirements.txt .
RUN pip install -r requirements.txt

# 再复制源码与配置文件
COPY src ./src
COPY config.yaml .env.example ./

# 运行时以非 root 用户运行
RUN useradd --create-home --shell /bin/bash vbot \
    && chown -R vbot:vbot /app
USER vbot

# 默认入口
ENTRYPOINT ["python", "-m", "main"]
