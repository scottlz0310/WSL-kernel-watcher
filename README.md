# WSL Kernel Watcher v2.1.0 - Docker常駐版

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
- 🔔 **systemd自動化**: ファイル監視システムの自動起動・復旧
- 📝 **ファイル監視**: Docker → ファイル作成 → systemd監視 → WSL実行
- 🌐 **WSL経由通知**: WSL → PowerShell → Windows Toast通知
- ⚙️ **環境変数設定**: docker-compose.ymlで簡単設定
- 🔄 **完全自動化**: 手動操作不要の運用

## クイックスタート

### 1. systemd監視サービスのセットアップ
```bash
# WSLファイル監視システムをsystemdサービスとして登録
./install-monitor.sh
```

### 2. Docker常駐監視の開始
```bash
# 監視開始
make start

# ログ確認
make logs

# 停止
make stop
```

### アンインストール
```bash
# systemd監視サービスをアンインストール
make uninstall-monitor
```

### 詳細な導入手順
📋 **[INSTALLATION_GUIDE.md](docs/INSTALLATION_GUIDE.md)** を参照してください

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

### Makefileコマンド

```bash
# 操作系テスト実行
make test

# 通知テストのみ
make test-notification

# 開発環境セットアップ
make dev-setup

# コード品質チェック
make check-all
```

### 直接実行

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
