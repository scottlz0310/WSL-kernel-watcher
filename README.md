# WSL Kernel Watcher v2 - Docker常駐版

Docker常駐 → WSL経由PowerShell → Windows Toast通知の新アーキテクチャ

## アーキテクチャ

```
┌─────────────────────────────────────┐
│  Docker Container (Linux)           │
│  ┌─────────────────────────────┐   │
│  │ WSL Kernel Watcher v2       │   │
│  │ - GitHub API監視            │   │
│  │ - バージョン比較            │   │
│  └─────────────────────────────┘   │
└─────────────────┬───────────────────┘
                  │ 新バージョン検出
                  ↓
         ┌────────────────────┐
         │ WSL経由でPowerShell │
         │ 実行                │
         └────────┬───────────┘
                  │
                  ↓
         ┌────────────────────┐
         │ Windows Toast通知   │
         └────────────────────┘
```

## 特徴

- 🐳 **Docker常駐**: 軽量なLinuxコンテナで24/7監視
- 🔔 **WSL経由通知**: Docker → WSL → Windows Toast通知
- ⚙️ **環境変数設定**: docker-compose.ymlで簡単設定
- 🔄 **自動再起動**: コンテナクラッシュ時も自動復旧
- 📊 **非同期処理**: リソース効率的な実装

## クイックスタート

### 1. 環境変数設定（オプション）

```bash
cp .env.example .env
# .envファイルを編集
```

### 2. Docker起動

```bash
docker-compose up -d
```

### 3. ログ確認

```bash
docker-compose logs -f wsl-kernel-watcher
```

### 4. 停止

```bash
docker-compose down
```

## 設定

### 環境変数

| 変数名 | デフォルト値 | 説明 |
|--------|-------------|------|
| `REPOSITORY_URL` | `microsoft/WSL2-Linux-Kernel` | 監視対象リポジトリ |
| `CHECK_INTERVAL_MINUTES` | `30` | チェック間隔（分） |
| `LOG_LEVEL` | `INFO` | ログレベル |
| `GITHUB_TOKEN` | なし | GitHub Personal Access Token |

### docker-compose.yml

```yaml
services:
  wsl-kernel-watcher:
    environment:
      - REPOSITORY_URL=microsoft/WSL2-Linux-Kernel
      - CHECK_INTERVAL_MINUTES=30
      - LOG_LEVEL=INFO
```

## 開発

### テスト実行

```bash
# パッケージテスト
uv run pytest tests/ -v

# カバレッジ付き
uv run pytest tests/ --cov=src --cov-report=html
```

### ローカル実行

```bash
# 環境変数設定
export REPOSITORY_URL=microsoft/WSL2-Linux-Kernel
export CHECK_INTERVAL_MINUTES=30
export LOG_LEVEL=DEBUG

# 実行
uv run python -m src.main
```

## トラブルシューティング

### 通知が表示されない

1. WSLからPowerShellが実行できるか確認:
   ```bash
   wsl.exe -e powershell.exe -Command "Write-Host 'Test'"
   ```

2. Docker内からWSLにアクセスできるか確認:
   ```bash
   docker exec wsl-kernel-watcher wsl.exe -e echo "Test"
   ```

### コンテナが起動しない

```bash
# ログ確認
docker-compose logs wsl-kernel-watcher

# コンテナ再ビルド
docker-compose build --no-cache
docker-compose up -d
```

## ディレクトリ構成

```
src/                        # アプリケーション本体
├── __init__.py
├── docker_notifier.py     # WSL経由通知
├── github_watcher.py      # GitHub監視
├── main.py               # メインアプリ
└── config.py             # 設定管理

tests/                      # 自動テスト
├── test_docker_notifier.py
├── test_github_watcher.py
├── test_config.py
├── test_main.py
└── test_integration.py

Dockerfile                 # Dockerイメージ定義
docker-compose.yml         # Docker Compose設定
.env.example               # 環境変数例
```

## ライセンス

MIT License
