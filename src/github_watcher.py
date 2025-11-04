"""GitHub監視モジュール - Docker環境対応版"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


@dataclass
class Release:
    """GitHub リリース情報"""

    tag_name: str
    name: str
    published_at: datetime
    prerelease: bool
    html_url: str


class GitHubWatcher:
    """GitHub監視クライアント - Docker環境最適化版"""

    def __init__(self, repository_url: str = "microsoft/WSL2-Linux-Kernel"):
        self.repository_url = repository_url
        self.base_url = "https://api.github.com"
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """HTTPセッション作成"""
        import os

        session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        headers = {
            "User-Agent": "WSL-Kernel-Watcher-Docker/2.0",
            "Accept": "application/vnd.github.v3+json",
        }

        # GitHub Personal Access Tokenを使用
        github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN") or os.getenv(
            "GITHUB_TOKEN"
        )
        if github_token:
            headers["Authorization"] = f"token {github_token}"
            logger.info("GitHub Personal Access Tokenを使用")
        else:
            logger.warning("GitHub Personal Access Tokenが設定されていません")

        session.headers.update(headers)
        return session

    def get_latest_stable_release(self) -> Release | None:
        """最新安定版リリース取得"""
        try:
            url = f"{self.base_url}/repos/{self.repository_url}/releases"
            logger.info(f"GitHub APIからリリース情報取得: {url}")

            response = self.session.get(url)
            self._handle_rate_limit(response)
            response.raise_for_status()

            releases_data = response.json()

            for release_data in releases_data:
                if not self._is_prerelease(release_data):
                    release = self._parse_release(release_data)
                    logger.info(f"最新安定版発見: {release.tag_name}")
                    return release

            logger.warning("安定版リリースが見つかりません")
            return None

        except requests.RequestException as e:
            logger.error(f"GitHub API呼び出しエラー: {e}")
            raise
        except (KeyError, ValueError) as e:
            logger.error(f"レスポンス解析エラー: {e}")
            raise

    def _handle_rate_limit(self, response: requests.Response) -> None:
        """レート制限処理"""
        remaining = response.headers.get("X-RateLimit-Remaining")

        if remaining and int(remaining) < 10:
            logger.warning(f"レート制限接近: 残り{remaining}リクエスト")

        if response.status_code == 429:
            reset_time = response.headers.get("X-RateLimit-Reset")
            wait_time = 60

            if reset_time:
                wait_time = max(int(reset_time) - int(time.time()), 0) + 1

            logger.warning(f"レート制限到達: {wait_time}秒待機")
            time.sleep(wait_time)

    def _is_prerelease(self, release_data: dict) -> bool:
        """プレリリース判定"""
        if release_data.get("prerelease", False):
            return True

        tag_name = release_data.get("tag_name", "").lower()
        prerelease_keywords = ["rc", "alpha", "beta", "preview", "pre"]

        return any(keyword in tag_name for keyword in prerelease_keywords)

    def _parse_release(self, release_data: dict) -> Release:
        """リリースデータ解析"""
        published_at_str = release_data["published_at"]
        published_at = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))

        return Release(
            tag_name=release_data["tag_name"],
            name=release_data["name"],
            published_at=published_at,
            prerelease=release_data["prerelease"],
            html_url=release_data["html_url"],
        )
