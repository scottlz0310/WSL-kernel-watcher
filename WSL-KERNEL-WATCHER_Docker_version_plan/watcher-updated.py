import logging
import re
from typing import Any, Optional

import requests
from mcp_client import MCPClient

from config import Config
from wsl_utils import WSLUtils

logger = logging.getLogger(__name__)


class GitHubWatcher:
    def __init__(self, config: Config):
        self.config = config
        self.mcp_client = MCPClient(config.mcp_github_url)
        self.wsl_utils = WSLUtils()
        self.last_versions = {}

    async def check_repositories(self):
        """監視対象リポジトリをチェック"""
        for repo in self.config.repositories:
            try:
                await self._check_repository(repo)
            except Exception as e:
                logger.error(f"Error checking {repo}: {e}")

    async def _check_repository(self, repo: str):
        """個別リポジトリのチェック"""
        try:
            # MCP経由で最新リリース取得
            latest_release = await self.mcp_client.get_latest_release(repo)

            if not latest_release:
                return

            version = latest_release["tag_name"]

            # WSLカーネルリポジトリの場合は特別処理
            if repo == "microsoft/WSL2-Linux-Kernel":
                await self._check_wsl_kernel(repo, version, latest_release)
            else:
                await self._check_generic_repository(repo, version, latest_release)

        except Exception as e:
            logger.error(f"Error checking repository {repo}: {e}")

    async def _check_wsl_kernel(
        self, repo: str, latest_version: str, release: dict[str, Any]
    ):
        """WSLカーネル専用チェック"""
        try:
            # 現在のWSLカーネルバージョンを取得
            current_version = self.wsl_utils.get_current_kernel_version()

            if not current_version:
                logger.warning("Could not get current WSL kernel version")
                return

            # バージョン番号を正規化 (linux-msft-wsl-5.15.90.1 -> 5.15.90.1)
            latest_clean = self._extract_version_number(latest_version)

            if not latest_clean:
                logger.warning(f"Could not parse version from tag: {latest_version}")
                return

            logger.info(
                f"WSL Kernel - Current: {current_version}, Latest: {latest_clean}"
            )

            # バージョン比較
            if self.wsl_utils.compare_versions(current_version, latest_clean):
                logger.info(f"New WSL kernel version available: {latest_clean}")
                await self._send_wsl_notification(
                    current_version, latest_clean, release
                )
            else:
                logger.info("WSL kernel is up to date")

        except Exception as e:
            logger.error(f"Error checking WSL kernel: {e}")

    async def _check_generic_repository(
        self, repo: str, version: str, release: dict[str, Any]
    ):
        """一般リポジトリのチェック（従来の方式）"""
        # 前回バージョンと比較
        if repo not in self.last_versions:
            self.last_versions[repo] = version
            logger.info(f"Initial version for {repo}: {version}")
            return

        if version != self.last_versions[repo]:
            logger.info(f"New version detected for {repo}: {version}")
            await self._send_notification(repo, version, release)
            self.last_versions[repo] = version

    def _extract_version_number(self, tag: str) -> Optional[str]:
        """タグからバージョン番号を抽出"""
        # linux-msft-wsl-5.15.90.1 -> 5.15.90.1
        # v5.15.90.1 -> 5.15.90.1
        version_patterns = [
            r"linux-msft-wsl-(\d+\.\d+\.\d+\.\d+)",
            r"v?(\d+\.\d+\.\d+\.\d+)",
            r"(\d+\.\d+\.\d+)",
        ]

        for pattern in version_patterns:
            match = re.search(pattern, tag)
            if match:
                return match.group(1)

        return None

    async def _send_wsl_notification(
        self, current: str, latest: str, release: dict[str, Any]
    ):
        """WSLカーネル専用通知"""
        try:
            notification_data = {
                "title": "WSL Kernel Update Available",
                "message": f"New kernel version {latest} available\nCurrent: {current}",
                "url": release.get("html_url", ""),
                "repo": "microsoft/WSL2-Linux-Kernel",
                "current_version": current,
                "latest_version": latest,
            }

            response = requests.post(
                self.config.notification_url, json=notification_data, timeout=10
            )

            if response.status_code == 200:
                logger.info(f"WSL kernel notification sent: {current} -> {latest}")
            else:
                logger.error(f"Failed to send WSL notification: {response.status_code}")

        except Exception as e:
            logger.error(f"Error sending WSL notification: {e}")

    async def _send_notification(
        self, repo: str, version: str, release: dict[str, Any]
    ):
        """一般通知送信"""
        try:
            notification_data = {
                "title": f"New Release: {repo}",
                "message": f"Version {version} is now available",
                "url": release.get("html_url", ""),
                "repo": repo,
                "version": version,
            }

            response = requests.post(
                self.config.notification_url, json=notification_data, timeout=10
            )

            if response.status_code == 200:
                logger.info(f"Notification sent for {repo} {version}")
            else:
                logger.error(f"Failed to send notification: {response.status_code}")

        except Exception as e:
            logger.error(f"Error sending notification: {e}")
