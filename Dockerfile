FROM python:3.14-slim

WORKDIR /app

# システム依存関係インストール
RUN apt-get update && apt-get install -y \
    curl \
    binfmt-support \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# uvインストール
RUN pip install --no-cache-dir uv

# 依存関係ファイルコピー
COPY pyproject.toml uv.lock README.md ./

# 依存関係インストール
RUN uv sync --frozen --no-dev

# アプリケーションコードコピー
COPY src/ ./src/

# 実行
CMD ["uv", "run", "python", "-m", "src.main"]