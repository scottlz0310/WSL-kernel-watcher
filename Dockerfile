FROM python:3.11-slim

WORKDIR /app

# システム依存関係インストール
RUN apt-get update && apt-get install -y \
    curl \
    binfmt-support \
    && rm -rf /var/lib/apt/lists/*

# WSL2統合のための設定
ENV PATH="${PATH}:/mnt/c/Windows/System32"
ENV WSLENV="PATH/l"

# uvインストール
RUN pip install --no-cache-dir uv

# 依存関係ファイルコピー
COPY pyproject.toml uv.lock README.md ./

# 依存関係インストール
RUN uv sync --frozen --no-dev

# アプリケーションコードコピー
COPY src/ ./src/
COPY test-wsl-access.sh test-notification.py ./

# 実行
CMD ["uv", "run", "python", "-m", "src.main"]