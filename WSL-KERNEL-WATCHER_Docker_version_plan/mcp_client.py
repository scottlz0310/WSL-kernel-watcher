import logging
from typing import Any, Optional

import aiohttp

logger = logging.getLogger(__name__)


class MCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get_latest_release(self, repo: str) -> Optional[dict[str, Any]]:
        """MCP経由で最新リリース情報を取得"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/repos/{repo}/releases/latest"
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(
                            f"Failed to get release for {repo}: {response.status}"
                        )
                        return None
        except Exception as e:
            logger.error(f"MCP request failed for {repo}: {e}")
            return None
