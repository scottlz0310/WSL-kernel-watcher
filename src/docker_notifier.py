"""Docker環境からWSL経由でWindows通知を送信するモジュール"""

import logging

logger = logging.getLogger(__name__)


class DockerNotifier:
    """Docker環境からWSL経由でWindows通知を送信"""

    def send_notification(self, title: str, message: str) -> bool:
        """ファイル監視システム経由でWindows通知を送信"""
        try:
            import os
            import time

            # ホスト側で実行するスクリプトを作成
            script_content = f"""#!/bin/bash
/mnt/c/Windows/System32/wsl.exe -e /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.MessageBox]::Show('{message}', '{title}', 'OK', 'Information')
"
"""

            # ユニークなファイル名でスクリプト作成
            timestamp = int(time.time() * 1000)
            script_path = f"/host/docker_notify_{timestamp}.sh"

            with open(script_path, "w") as f:
                f.write(script_content)

            os.chmod(script_path, 0o755)

            # ファイル監視システムが処理するまで待機
            time.sleep(2)

            # スクリプトが削除されたか確認（実行完了の証拠）
            if not os.path.exists(script_path):
                logger.info(f"通知送信成功: {title}")
                return True
            else:
                logger.error("通知送信失敗: ファイル監視システムが動作していない可能性")
                return False

        except Exception as e:
            logger.error(f"通知送信エラー: {e}")
            return False

    def notify_kernel_update(self, new_version: str, current_version: str) -> bool:
        """カーネル更新通知を送信"""
        title = "WSL2カーネル更新通知"
        message = f"新しいバージョンが利用可能です\\n現在: {current_version}\\n最新: {new_version}"

        return self.send_notification(title, message)
