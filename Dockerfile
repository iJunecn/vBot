# vBot 镜像：使用 Docker Hub 代理，避免部署机直连 Docker Hub 超时。
FROM docker.m.daocloud.io/docker.io/library/python:3.11-slim AS runtime

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
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# 复制源码（src/ 是目录）
COPY src /app/src

# 复制静态配置文件——每个 COPY 一行，避免多源 COPY 在某些 BuildKit 组合下产生路径歧义
COPY config.yaml /app/config.yaml

# 运行时以非 root 用户运行
RUN useradd --create-home --shell /bin/bash vbot \
    && chown -R vbot:vbot /app
USER vbot

# 默认入口
ENTRYPOINT ["python", "-m", "main"]
