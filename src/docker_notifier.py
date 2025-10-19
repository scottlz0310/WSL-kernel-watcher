"""Docker環境からWSL経由でWindows通知を送信するモジュール"""

import logging
import subprocess

logger = logging.getLogger(__name__)


class DockerNotifier:
    """Docker環境からWSL経由でWindows通知を送信"""

    def __init__(self):
        self.powershell_script = self._create_notification_script()

    def _create_notification_script(self) -> str:
        """Windows Toast通知用PowerShellスクリプトを生成"""
        return """
param(
    [string]$Title,
    [string]$Message,
    [string]$AppId = "WSL.KernelWatcher"
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Windows Toast通知を表示
$null = [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]
$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)

$toastXml = [xml] $template.GetXml()
$toastXml.GetElementsByTagName("text")[0].AppendChild($toastXml.CreateTextNode($Title)) | Out-Null
$toastXml.GetElementsByTagName("text")[1].AppendChild($toastXml.CreateTextNode($Message)) | Out-Null

$toast = [Windows.UI.Notifications.ToastNotification]::new($toastXml)
$notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($AppId)
$notifier.Show($toast)
"""

    def send_notification(self, title: str, message: str) -> bool:
        """WSL経由でWindows通知を送信"""
        try:
            # PowerShellスクリプトを一時ファイルに保存
            script_content = self.powershell_script

            # WSL経由でPowerShellを実行
            cmd = [
                "wsl.exe",
                "-e",
                "bash",
                "-c",
                f'powershell.exe -Command "{script_content}" -Title "{title}" -Message "{message}"',
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                logger.info(f"通知送信成功: {title}")
                return True
            else:
                logger.error(f"通知送信失敗: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("通知送信がタイムアウトしました")
            return False
        except Exception as e:
            logger.error(f"通知送信エラー: {e}")
            return False

    def notify_kernel_update(self, new_version: str, current_version: str) -> bool:
        """カーネル更新通知を送信"""
        title = "WSL2カーネル更新通知"
        message = f"新しいバージョンが利用可能です\n現在: {current_version}\n最新: {new_version}"

        return self.send_notification(title, message)
