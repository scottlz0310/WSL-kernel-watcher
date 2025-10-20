#!/bin/bash
# WSLファイル監視システムのsystemdサービスアンインストールスクリプト

SERVICE_NAME="wsl-kernel-watcher-monitor"
SERVICE_FILE="$SERVICE_NAME.service"
SYSTEMD_DIR="/etc/systemd/system"

echo "WSL Kernel Watcher監視システムのアンインストール開始..."

# サービス停止・無効化
echo "サービスを停止・無効化中..."
sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true
sudo systemctl disable "$SERVICE_NAME" 2>/dev/null || true

# systemdサービスファイル削除
echo "systemdサービスファイルを削除中..."
sudo rm -f "$SYSTEMD_DIR/$SERVICE_FILE"

# systemdリロード
echo "systemdをリロード中..."
sudo systemctl daemon-reload

# 既存プロセス停止
echo "既存の監視プロセスを停止中..."
pkill -f wsl-file-watcher.sh || true

echo ""
echo "✅ WSL Kernel Watcher監視システムのアンインストール完了"
echo ""
echo "確認コマンド:"
echo "  サービス状態: sudo systemctl status $SERVICE_NAME"
echo "  (Unit $SERVICE_NAME.service could not be found. と表示されれば正常)"