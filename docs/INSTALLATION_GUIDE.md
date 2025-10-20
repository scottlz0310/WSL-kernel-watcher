# WSL Kernel Watcher v2.0.0 導入マニュアル

## 🚀 クイックスタート

### 1. リポジトリクローン
```bash
git clone https://github.com/scottlz0310/WSL-kernel-watcher.git
cd WSL-kernel-watcher
```

### 2. systemd監視サービスのインストール
```bash
# WSLファイル監視システムをsystemdサービスとして登録
./install-monitor.sh
```

### 3. Docker常駐監視の開始
```bash
# Docker常駐監視を開始
make start

# ログ確認
make logs
```

## 📋 詳細セットアップ

### 前提条件
- WSL2環境（Windows 10/11）
- Docker + Docker Compose
- sudo権限

### systemd監視サービス
WSL Kernel Watcher v2.0.0では、Docker → WSL通知のためにsystemd監視サービスが必要です。

```bash
# サービス状態確認
sudo systemctl status wsl-kernel-watcher-monitor

# サービス停止・開始
sudo systemctl stop wsl-kernel-watcher-monitor
sudo systemctl start wsl-kernel-watcher-monitor

# ログ確認
sudo journalctl -u wsl-kernel-watcher-monitor -f
```

### Docker設定

#### 環境変数設定（オプション）
```bash
cp .env.example .env
# .envファイルを編集
```

#### 利用可能な環境変数
| 変数名 | デフォルト値 | 説明 |
|--------|-------------|------|
| `REPOSITORY_URL` | `microsoft/WSL2-Linux-Kernel` | 監視対象リポジトリ |
| `CHECK_INTERVAL_MINUTES` | `30` | チェック間隔（分） |
| `LOG_LEVEL` | `INFO` | ログレベル |
| `GITHUB_TOKEN` | なし | GitHub Personal Access Token |

## 🔧 Makefileコマンド

### 基本操作
```bash
make help          # 使用可能なコマンド表示
make start         # Docker常駐監視開始
make stop          # Docker常駐監視停止
make restart       # Docker常駐監視再起動
make logs          # リアルタイムログ表示
make status        # コンテナ状態確認
```

### テスト・開発
```bash
make test-quick           # クイックテスト（コンテナ不要）
make test-core           # コア機能テスト（Docker）
make test-notification   # 通知テスト（スタンドアロン）
make test               # 全テスト実行

make dev-setup          # 開発環境セットアップ
make check-all          # 全品質チェック
```

### メンテナンス
```bash
make build         # Dockerイメージビルド
make clean         # 全Dockerリソースクリーンアップ
make config        # 現在の設定表示
make version       # バージョン情報表示
```

## 🔔 通知テスト

### 手動通知テスト
```bash
# スタンドアロン通知テスト
make test-notification

# Docker経由通知テスト
make start
docker-compose exec wsl-kernel-watcher uv run python -c "
from src.docker_notifier import DockerNotifier
notifier = DockerNotifier()
success = notifier.send_notification('テスト通知', 'WSL Kernel Watcher v2.0.0')
print(f'通知結果: {success}')
"
```

## 🛠️ トラブルシューティング

### systemd監視サービスが動作しない
```bash
# サービス状態確認
sudo systemctl status wsl-kernel-watcher-monitor

# サービス再インストール
sudo systemctl stop wsl-kernel-watcher-monitor
sudo systemctl disable wsl-kernel-watcher-monitor
./install-monitor.sh
```

### Docker通知が動作しない
```bash
# 1. systemd監視サービス確認
sudo systemctl status wsl-kernel-watcher-monitor

# 2. ファイル監視ログ確認
sudo journalctl -u wsl-kernel-watcher-monitor -f

# 3. Docker権限確認
docker-compose exec wsl-kernel-watcher ls -la /host/

# 4. 手動ファイル作成テスト
echo '#!/bin/bash' > docker_notify_test.sh
echo 'echo "手動テスト成功"' >> docker_notify_test.sh
chmod +x docker_notify_test.sh
# 1秒後にファイルが削除されるか確認
```

### コンテナが起動しない
```bash
# ログ確認
make logs

# イメージ再ビルド
make clean
make build
make start
```

## 🔄 アップデート手順

```bash
# 1. 現在の監視停止
make stop
sudo systemctl stop wsl-kernel-watcher-monitor

# 2. 最新コード取得
git pull origin main

# 3. systemd監視サービス更新
./install-monitor.sh

# 4. Docker監視再開
make start
```

## 📊 動作確認

### 正常動作の確認項目
- [ ] systemd監視サービスが`active (running)`状態
- [ ] Dockerコンテナが正常起動
- [ ] GitHub API接続成功
- [ ] 通知テストが成功

### 確認コマンド
```bash
# 全体状態確認
sudo systemctl status wsl-kernel-watcher-monitor
make status
make test-quick

# 通知機能確認
make test-notification
```

## 📝 ログ確認

```bash
# systemd監視サービスログ
sudo journalctl -u wsl-kernel-watcher-monitor -f

# Dockerコンテナログ
make logs

# 全ログ確認
sudo journalctl -u wsl-kernel-watcher-monitor --since "1 hour ago"
docker-compose logs --since 1h
```

## 🎯 運用のベストプラクティス

1. **定期的な動作確認**: 週1回の通知テスト実行
2. **ログ監視**: 異常なエラーログの確認
3. **アップデート**: 月1回の最新版確認
4. **バックアップ**: 設定ファイルのバックアップ

## 📞 サポート

問題が発生した場合：
1. [GitHub Issues](https://github.com/scottlz0310/WSL-kernel-watcher/issues)で報告
2. ログファイルを添付
3. 環境情報（WSLバージョン、Dockerバージョン）を記載