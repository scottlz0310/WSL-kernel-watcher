#!/bin/bash
# WSLホスト側ファイル監視・自動実行スクリプト

WATCH_DIR="$(dirname "$(readlink -f "$0")")"
SCRIPT_PATTERN="docker_notify_*.sh"

echo "WSLホスト側ファイル監視開始: $WATCH_DIR"

while true; do
    # Docker通知スクリプトファイルを監視
    for script in $WATCH_DIR/docker_notify_*.sh; do
        if [ -f "$script" ]; then
            echo "通知スクリプト検出: $script"
            
            # ファイルを先に移動して競合状態を回避
            temp_script="${script}.processing"
            if mv "$script" "$temp_script" 2>/dev/null; then
                # WSL経由でPowerShell実行
                bash "$temp_script"
                
                # 実行後にファイル削除
                rm "$temp_script" 2>/dev/null
                echo "通知スクリプト実行完了・削除"
            fi
        fi
    done
    
    sleep 1
done