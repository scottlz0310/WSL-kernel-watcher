import logging
from typing import Any

import requests
from mcp_client import MCPClient

from config import Config

logger = logging.getLogger(__name__)


class GitHubWatcher:
    def __init__(self, config: Config):
        self.config = config
        self.mcp_client = MCPClient(config.mcp_github_url)
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

            # 前回バージョンと比較
            if repo not in self.last_versions:
                self.last_versions[repo] = version
                logger.info(f"Initial version for {repo}: {version}")
                return

            if version != self.last_versions[repo]:
                logger.info(f"New version detected for {repo}: {version}")
                await self._send_notification(repo, version, latest_release)
                self.last_versions[repo] = version

        except Exception as e:
            logger.error(f"Error checking repository {repo}: {e}")

    async def _send_notification(
        self, repo: str, version: str, release: dict[str, Any]
    ):
        """通知送信"""
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
