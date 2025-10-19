"""Docker環境からWSL経由でWindows通知を送信するモジュール"""

import logging
import subprocess

logger = logging.getLogger(__name__)


class DockerNotifier:
    """Docker環境からWSL経由でWindows通知を送信"""

    def send_notification(self, title: str, message: str) -> bool:
        """WSL経由でWindows通知を送信"""
        try:
            ps_script = f'''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
$template.GetElementsByTagName("text")[0].AppendChild($template.CreateTextNode("{title}")) | Out-Null
$template.GetElementsByTagName("text")[1].AppendChild($template.CreateTextNode("{message}")) | Out-Null
$toast = [Windows.UI.Notifications.ToastNotification]::new($template)
$notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("WSL.KernelWatcher")
$notifier.Show($toast)
'''

            # PowerShellのフルパスを使用（WSL環境対応）
            ps_path = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
            cmd = ["wsl.exe", "-e", ps_path, "-Command", ps_script]
            result = subprocess.run(
                cmd, capture_output=True, timeout=30, encoding="cp932", errors="ignore"
            )

            if result.returncode == 0:
                logger.info(f"通知送信成功: {title}")
                return True
            else:
                logger.error(f"通知送信失敗: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"通知送信エラー: {e}")
            return False

    def notify_kernel_update(self, new_version: str, current_version: str) -> bool:
        """カーネル更新通知を送信"""
        title = "WSL2カーネル更新通知"
        message = f"新しいバージョンが利用可能です\\n現在: {current_version}\\n最新: {new_version}"

        return self.send_notification(title, message)
