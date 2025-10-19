FROM python:3.11-slim

WORKDIR /app

# システム依存関係をインストール
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をコピーしてインストール
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

# アプリケーションコードをコピー
COPY src/ ./src/
COPY config.toml ./

# 実行
CMD ["uv", "run", "python", "-m", "src.main"]