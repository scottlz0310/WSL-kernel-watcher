FROM python:3.11-slim

WORKDIR /app

# システム依存関係インストール
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# uvインストール
RUN pip install --no-cache-dir uv

# 依存関係ファイルコピー
COPY pyproject.toml uv.lock ./

# 依存関係インストール
RUN uv sync --frozen --no-dev

# アプリケーションコードコピー
COPY src_v2/ ./src_v2/

# 実行
CMD ["uv", "run", "python", "-m", "src_v2.main"]