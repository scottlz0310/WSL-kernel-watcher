#!/usr/bin/env python3
"""
Windows Toast Notification Server
Docker containers can send HTTP requests to display Windows toast notifications
"""

import json
import logging
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

# ログ設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class NotificationHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """POST /notify - Toast通知を表示"""
        try:
            # リクエストボディを読み取り
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)

            # JSON解析
            notification_data = json.loads(post_data.decode("utf-8"))

            # 必須フィールドの確認
            title = notification_data.get("title", "Notification")
            message = notification_data.get("message", "")
            url = notification_data.get("url", "")

            # Toast通知を表示
            self._show_toast_notification(title, message, url)

            # レスポンス送信
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())

            logger.info(f"Notification sent: {title}")

        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON")
        except Exception as e:
            logger.error(f"Error processing notification: {e}")
            self._send_error(500, str(e))

    def do_GET(self):
        """GET /health - ヘルスチェック"""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        else:
            self._send_error(404, "Not Found")

    def _show_toast_notification(self, title: str, message: str, url: str = ""):
        """Windows Toast通知を表示"""
        try:
            # PowerShell BurntToast コマンド構築
            ps_command = f"""
            if (Get-Module -ListAvailable -Name BurntToast) {{
                New-BurntToastNotification -Text '{title}' -Text '{message}' -Sound 'Default'
            }} else {{
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.MessageBox]::Show('{message}', '{title}', 'OK', 'Information')
            }}
            """

            # PowerShell実行
            result = subprocess.run(
                ["powershell", "-WindowStyle", "Hidden", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                logger.warning(f"PowerShell warning: {result.stderr}")
                # フォールバック: 標準MessageBox
                self._show_message_box(title, message)

        except subprocess.TimeoutExpired:
            logger.error("PowerShell command timed out")
        except Exception as e:
            logger.error(f"Error showing notification: {e}")
            # フォールバック: 標準MessageBox
            self._show_message_box(title, message)

    def _show_message_box(self, title: str, message: str):
        """フォールバック: 標準MessageBox"""
        try:
            subprocess.run(
                [
                    "powershell",
                    "-WindowStyle",
                    "Hidden",
                    "-Command",
                    f"Add-Type -AssemblyName System.Windows.Forms; "
                    f"[System.Windows.Forms.MessageBox]::Show('{message}', '{title}')",
                ],
                timeout=5,
            )
        except Exception as e:
            logger.error(f"Fallback notification failed: {e}")

    def _send_error(self, code: int, message: str):
        """エラーレスポンス送信"""
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())

    def log_message(self, format, *args):
        """アクセスログを標準ログに統合"""
        logger.info(f"{self.address_string()} - {format % args}")


def main():
    """メイン関数"""
    port = int(os.getenv("NOTIFICATION_PORT", "9999"))

    try:
        # BurntToastモジュールの確認
        result = subprocess.run(
            ["powershell", "-Command", "Get-Module -ListAvailable -Name BurntToast"],
            capture_output=True,
            text=True,
        )

        if "BurntToast" not in result.stdout:
            logger.warning(
                "BurntToast module not found. Install with: Install-Module -Name BurntToast"
            )
            logger.info("Falling back to standard MessageBox notifications")

        # HTTPサーバー起動
        server = HTTPServer(("0.0.0.0", port), NotificationHandler)
        logger.info(f"Notification server started on port {port}")
        logger.info("Send POST requests to http://localhost:9999/notify")

        server.serve_forever()

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
