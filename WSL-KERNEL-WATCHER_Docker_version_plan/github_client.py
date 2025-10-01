import logging
import os
from typing import Any, Optional

import aiohttp

logger = logging.getLogger(__name__)


class GitHubClient:
    def __init__(self, mcp_url: str = None, github_token: str = None):
        self.mcp_url = mcp_url
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.headers = {}

        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"

    async def get_latest_release(self, repo: str) -> Optional[dict[str, Any]]:
        """最新リリース情報を取得（MCP優先、フォールバックでGitHub API）"""

        # MCP経由を試行
        if self.mcp_url:
            try:
                result = await self._get_via_mcp(repo)
                if result:
                    logger.debug(f"Got release via MCP for {repo}")
                    return result
            except Exception as e:
                logger.info(f"MCP failed for {repo}, falling back to GitHub API: {e}")

        # GitHub API直接呼び出し
        return await self._get_via_github_api(repo)

    async def _get_via_mcp(self, repo: str) -> Optional[dict[str, Any]]:
        """MCP経由でリリース情報取得"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.mcp_url}/repos/{repo}/releases/latest"
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(
                            f"MCP request failed for {repo}: {response.status}"
                        )
                        return None
        except Exception as e:
            logger.error(f"MCP request error for {repo}: {e}")
            return None

    async def _get_via_github_api(self, repo: str) -> Optional[dict[str, Any]]:
        """GitHub API直接呼び出し"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.github.com/repos/{repo}/releases/latest"
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        logger.debug(f"Got release via GitHub API for {repo}")
                        return await response.json()
                    elif response.status == 403:
                        logger.error(f"GitHub API rate limit exceeded for {repo}")
                        return None
                    else:
                        logger.warning(
                            f"GitHub API request failed for {repo}: {response.status}"
                        )
                        return None
        except Exception as e:
            logger.error(f"GitHub API request error for {repo}: {e}")
            return None
