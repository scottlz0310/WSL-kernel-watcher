#!/usr/bin/env python3
"""
Enhanced Windows Toast Notification Server
- Docker containers can send HTTP requests to display Windows toast notifications
- WSL kernel version endpoint for Docker containers
"""

import json
import logging
import os
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class NotificationHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """POST /notify - Toast通知を表示"""
        if self.path == "/notify":
            self._handle_notification()
        else:
            self._send_error(404, "Not Found")

    def do_GET(self):
        """GET endpoints"""
        if self.path == "/health":
            self._handle_health()
        elif self.path == "/wsl-version":
            self._handle_wsl_version()
        else:
            self._send_error(404, "Not Found")

    def _handle_notification(self):
        """通知処理"""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            notification_data = json.loads(post_data.decode("utf-8"))

            title = notification_data.get("title", "Notification")
            message = notification_data.get("message", "")
            url = notification_data.get("url", "")

            self._show_toast_notification(title, message, url)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())

            logger.info(f"Notification sent: {title}")

        except Exception as e:
            logger.error(f"Error processing notification: {e}")
            self._send_error(500, str(e))

    def _handle_health(self):
        """ヘルスチェック"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "healthy"}).encode())

    def _handle_wsl_version(self):
        """WSLカーネルバージョン取得"""
        try:
            version = self._get_wsl_kernel_version()
            response_data = {
                "kernel_version": version,
                "status": "success" if version else "failed",
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())

            logger.info(f"WSL version requested: {version}")

        except Exception as e:
            logger.error(f"Error getting WSL version: {e}")
            self._send_error(500, str(e))

    def _get_wsl_kernel_version(self):
        """WSLカーネルバージョンを取得"""
        try:
            result = subprocess.run(
                ["wsl", "-e", "uname", "-r"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                kernel_info = result.stdout.strip()
                version_match = re.search(r"(\d+\.\d+\.\d+\.\d+)", kernel_info)
                if version_match:
                    return version_match.group(1)

            logger.warning(f"Failed to parse WSL kernel version: {result.stdout}")
            return None

        except Exception as e:
            logger.error(f"Error getting WSL kernel version: {e}")
            return None

    def _show_toast_notification(self, title: str, message: str, url: str = ""):
        """Toast通知表示"""
        try:
            ps_command = f"""
            if (Get-Module -ListAvailable -Name BurntToast) {{
                New-BurntToastNotification -Text '{title}' -Text '{message}' -Sound 'Default'
            }} else {{
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.MessageBox]::Show('{message}', '{title}', 'OK', 'Information')
            }}
            """

            result = subprocess.run(
                ["powershell", "-WindowStyle", "Hidden", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                self._show_message_box(title, message)

        except Exception as e:
            logger.error(f"Error showing notification: {e}")
            self._show_message_box(title, message)

    def _show_message_box(self, title: str, message: str):
        """フォールバック通知"""
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
        """エラーレスポンス"""
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())

    def log_message(self, format, *args):
        """ログ統合"""
        logger.info(f"{self.address_string()} - {format % args}")


def main():
    port = int(os.getenv("NOTIFICATION_PORT", "9999"))

    try:
        server = HTTPServer(("0.0.0.0", port), NotificationHandler)
        logger.info(f"Enhanced notification server started on port {port}")
        logger.info("Endpoints:")
        logger.info("  POST /notify - Send notifications")
        logger.info("  GET /health - Health check")
        logger.info("  GET /wsl-version - Get WSL kernel version")

        server.serve_forever()

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
