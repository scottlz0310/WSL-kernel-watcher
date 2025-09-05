"""GitHub API クライアント

Microsoft WSL2 Linux Kernel リポジトリの最新リリース情報を取得する機能を提供します。
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger(__name__)


@dataclass
class Release:
    """GitHub リリース情報を表すデータクラス"""
    tag_name: str
    name: str
    published_at: datetime
    prerelease: bool
    html_url: str


class GitHubAPIClient:
    """GitHub API クライアント
    
    WSL2 Linux Kernel リポジトリの最新安定版リリース情報を取得します。
    リトライ機能とレート制限対応を含みます。
    """
    
    def __init__(self, repository_url: str = "microsoft/WSL2-Linux-Kernel"):
        """GitHubAPIClient を初期化
        
        Args:
            repository_url: 監視対象のリポジトリ（owner/repo形式）
        """
        self.repository_url = repository_url
        self.base_url = "https://api.github.com"
        self.session = self._create_session_with_retry()
        
    def _create_session_with_retry(self) -> requests.Session:
        """リトライ機能付きのHTTPセッションを作成
        
        Returns:
            リトライ戦略が設定されたrequests.Session
        """
        session = requests.Session()
        
        # リトライ戦略を設定
        retry_strategy = Retry(
            total=3,  # 最大3回まで再試行
            backoff_factor=1,  # 指数バックオフの基数
            status_forcelist=[429, 500, 502, 503, 504],  # リトライ対象のHTTPステータス
            allowed_methods=["HEAD", "GET", "OPTIONS"]  # リトライを許可するHTTPメソッド
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # User-Agentを設定
        session.headers.update({
            "User-Agent": "WSL-Kernel-Watcher/1.0",
            "Accept": "application/vnd.github.v3+json"
        })
        
        return session
    
    def get_latest_stable_release(self) -> Optional[Release]:
        """最新の安定版リリースを取得
        
        プレリリースを除外し、最新の安定版リリースのみを返します。
        
        Returns:
            最新の安定版リリース情報。取得できない場合はNone
            
        Raises:
            requests.RequestException: API呼び出しでエラーが発生した場合
        """
        try:
            url = f"{self.base_url}/repos/{self.repository_url}/releases"
            logger.info(f"GitHub APIからリリース情報を取得中: {url}")
            
            response = self.session.get(url)
            
            # レート制限をチェック
            self._handle_rate_limit(response)
            
            response.raise_for_status()
            releases_data = response.json()
            
            # プレリリースを除外して最新の安定版を検索
            for release_data in releases_data:
                if not self.is_prerelease(release_data):
                    release = self._parse_release_data(release_data)
                    logger.info(f"最新安定版リリースを発見: {release.tag_name}")
                    return release
            
            logger.warning("安定版リリースが見つかりませんでした")
            return None
            
        except requests.RequestException as e:
            logger.error(f"GitHub API呼び出しでエラーが発生: {e}")
            raise
        except (KeyError, ValueError) as e:
            logger.error(f"レスポンスデータの解析でエラーが発生: {e}")
            raise
    
    def _handle_rate_limit(self, response: requests.Response) -> None:
        """GitHub APIのレート制限を処理
        
        Args:
            response: GitHub APIからのレスポンス
            
        Raises:
            requests.RequestException: レート制限に達した場合
        """
        # レート制限の情報をヘッダーから取得
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset_time = response.headers.get("X-RateLimit-Reset")
        
        if remaining is not None:
            remaining_requests = int(remaining)
            logger.debug(f"GitHub API残りリクエスト数: {remaining_requests}")
            
            # レート制限に近づいている場合は警告
            if remaining_requests < 10:
                logger.warning(f"GitHub APIレート制限に近づいています: 残り{remaining_requests}リクエスト")
        
        # レート制限に達した場合（HTTP 429）
        if response.status_code == 429:
            if reset_time is not None:
                reset_timestamp = int(reset_time)
                current_time = int(time.time())
                wait_time = max(reset_timestamp - current_time, 0) + 1  # 1秒のバッファを追加
                
                logger.warning(f"GitHub APIレート制限に達しました。{wait_time}秒待機します")
                time.sleep(wait_time)
            else:
                # リセット時間が不明な場合は60秒待機
                logger.warning("GitHub APIレート制限に達しました。60秒待機します")
                time.sleep(60)
    
    def is_prerelease(self, release_data: dict) -> bool:
        """リリースがプレリリースかどうかを判定
        
        Args:
            release_data: GitHub APIから取得したリリースデータ
            
        Returns:
            プレリリースの場合True、安定版の場合False
        """
        # GitHub APIのprereleaseフラグをチェック
        if release_data.get("prerelease", False):
            return True
            
        # タグ名にRC、alpha、beta、previewなどが含まれている場合もプレリリースとして扱う
        tag_name = release_data.get("tag_name", "").lower()
        prerelease_keywords = ["rc", "alpha", "beta", "preview", "pre"]
        
        for keyword in prerelease_keywords:
            if keyword in tag_name:
                return True
                
        return False
    
    def _parse_release_data(self, release_data: dict) -> Release:
        """GitHub APIのレスポンスデータをReleaseオブジェクトに変換
        
        Args:
            release_data: GitHub APIから取得したリリースデータ
            
        Returns:
            Releaseオブジェクト
            
        Raises:
            KeyError: 必要なフィールドが存在しない場合
            ValueError: 日付の解析に失敗した場合
        """
        published_at_str = release_data["published_at"]
        # ISO 8601形式の日付文字列をdatetimeオブジェクトに変換
        published_at = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
        
        return Release(
            tag_name=release_data["tag_name"],
            name=release_data["name"],
            published_at=published_at,
            prerelease=release_data["prerelease"],
            html_url=release_data["html_url"]
        )