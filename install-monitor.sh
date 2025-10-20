#!/bin/bash
# WSLファイル監視システムのsystemdサービスインストールスクリプト

SERVICE_NAME="wsl-kernel-watcher-monitor"
SERVICE_FILE="$SERVICE_NAME.service"
SYSTEMD_DIR="/etc/systemd/system"
CURRENT_USER=$(whoami)
CURRENT_DIR=$(pwd)

echo "WSL Kernel Watcher監視システムのインストール開始..."
echo "ユーザー: $CURRENT_USER"
echo "作業ディレクトリ: $CURRENT_DIR"

# 既存プロセス停止
echo "既存の監視プロセスを停止中..."
pkill -f wsl-file-watcher.sh || true

# systemdサービスファイルを動的に生成
echo "systemdサービスファイルを生成中..."
sed "s|USER_PLACEHOLDER|$CURRENT_USER|g; s|WORKDIR_PLACEHOLDER|$CURRENT_DIR|g" "$SERVICE_FILE" > "/tmp/$SERVICE_FILE"

# systemdサービスファイルをインストール
echo "systemdサービスファイルをインストール中..."
sudo cp "/tmp/$SERVICE_FILE" "$SYSTEMD_DIR/"
rm "/tmp/$SERVICE_FILE"

# systemdリロード
echo "systemdをリロード中..."
sudo systemctl daemon-reload

# サービス有効化・開始
echo "サービスを有効化・開始中..."
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

# 状態確認
echo "サービス状態確認:"
sudo systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo "✅ WSL Kernel Watcher監視システムのインストール完了"
echo ""
echo "管理コマンド:"
echo "  状態確認: sudo systemctl status $SERVICE_NAME"
echo "  停止:     sudo systemctl stop $SERVICE_NAME"
echo "  開始:     sudo systemctl start $SERVICE_NAME"
echo "  ログ確認: sudo journalctl -u $SERVICE_NAME -f"