"""GitHub API クライアントのテスト"""

import json
import time
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
import requests
from requests.exceptions import RequestException

from src.github_api import GitHubAPIClient, Release


class TestRelease:
    """Releaseデータクラスのテスト"""
    
    def test_release_creation(self):
        """Releaseオブジェクトの作成テスト"""
        published_at = datetime(2023, 3, 15, 10, 0, 0)
        release = Release(
            tag_name="linux-msft-wsl-5.15.90.1",
            name="Linux-msft-wsl-5.15.90.1",
            published_at=published_at,
            prerelease=False,
            html_url="https://github.com/microsoft/WSL2-Linux-Kernel/releases/tag/linux-msft-wsl-5.15.90.1"
        )
        
        assert release.tag_name == "linux-msft-wsl-5.15.90.1"
        assert release.name == "Linux-msft-wsl-5.15.90.1"
        assert release.published_at == published_at
        assert release.prerelease is False
        assert "WSL2-Linux-Kernel" in release.html_url


class TestGitHubAPIClient:
    """GitHubAPIClientクラスのテスト"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される初期化処理"""
        self.client = GitHubAPIClient()
        
    def test_init_default_repository(self):
        """デフォルトリポジトリでの初期化テスト"""
        client = GitHubAPIClient()
        assert client.repository_url == "microsoft/WSL2-Linux-Kernel"
        assert client.base_url == "https://api.github.com"
        assert client.session is not None
        
    def test_init_custom_repository(self):
        """カスタムリポジトリでの初期化テスト"""
        custom_repo = "owner/repo"
        client = GitHubAPIClient(custom_repo)
        assert client.repository_url == custom_repo
        
    def test_session_has_retry_strategy(self):
        """セッションにリトライ戦略が設定されているかテスト"""
        session = self.client.session
        assert "User-Agent" in session.headers
        assert "WSL-Kernel-Watcher" in session.headers["User-Agent"]
        assert session.headers["Accept"] == "application/vnd.github.v3+json"
        
    def test_is_prerelease_with_prerelease_flag(self):
        """prereleaseフラグがTrueの場合のテスト"""
        release_data = {
            "tag_name": "linux-msft-wsl-5.15.90.1",
            "prerelease": True
        }
        assert self.client.is_prerelease(release_data) is True
        
    def test_is_prerelease_with_rc_tag(self):
        """RCタグを含む場合のテスト"""
        release_data = {
            "tag_name": "linux-msft-wsl-5.15.90.1-rc1",
            "prerelease": False
        }
        assert self.client.is_prerelease(release_data) is True
        
    def test_is_prerelease_with_alpha_tag(self):
        """alphaタグを含む場合のテスト"""
        release_data = {
            "tag_name": "linux-msft-wsl-5.15.90.1-alpha",
            "prerelease": False
        }
        assert self.client.is_prerelease(release_data) is True
        
    def test_is_prerelease_with_beta_tag(self):
        """betaタグを含む場合のテスト"""
        release_data = {
            "tag_name": "linux-msft-wsl-5.15.90.1-beta",
            "prerelease": False
        }
        assert self.client.is_prerelease(release_data) is True
        
    def test_is_prerelease_with_preview_tag(self):
        """previewタグを含む場合のテスト"""
        release_data = {
            "tag_name": "linux-msft-wsl-5.15.90.1-preview",
            "prerelease": False
        }
        assert self.client.is_prerelease(release_data) is True
        
    def test_is_not_prerelease_stable(self):
        """安定版の場合のテスト"""
        release_data = {
            "tag_name": "linux-msft-wsl-5.15.90.1",
            "prerelease": False
        }
        assert self.client.is_prerelease(release_data) is False
        
    def test_parse_release_data(self):
        """リリースデータの解析テスト"""
        release_data = {
            "tag_name": "linux-msft-wsl-5.15.90.1",
            "name": "Linux-msft-wsl-5.15.90.1",
            "published_at": "2023-03-15T10:00:00Z",
            "prerelease": False,
            "html_url": "https://github.com/microsoft/WSL2-Linux-Kernel/releases/tag/linux-msft-wsl-5.15.90.1"
        }
        
        release = self.client._parse_release_data(release_data)
        
        assert release.tag_name == "linux-msft-wsl-5.15.90.1"
        assert release.name == "Linux-msft-wsl-5.15.90.1"
        assert release.published_at.year == 2023
        assert release.published_at.month == 3
        assert release.published_at.day == 15
        assert release.prerelease is False
        assert "WSL2-Linux-Kernel" in release.html_url
        
    def test_parse_release_data_missing_field(self):
        """必要なフィールドが不足している場合のテスト"""
        release_data = {
            "tag_name": "linux-msft-wsl-5.15.90.1",
            # "name"フィールドが不足
            "published_at": "2023-03-15T10:00:00Z",
            "prerelease": False,
            "html_url": "https://github.com/microsoft/WSL2-Linux-Kernel/releases/tag/linux-msft-wsl-5.15.90.1"
        }
        
        with pytest.raises(KeyError):
            self.client._parse_release_data(release_data)
            
    def test_parse_release_data_invalid_date(self):
        """不正な日付形式の場合のテスト"""
        release_data = {
            "tag_name": "linux-msft-wsl-5.15.90.1",
            "name": "Linux-msft-wsl-5.15.90.1",
            "published_at": "invalid-date",
            "prerelease": False,
            "html_url": "https://github.com/microsoft/WSL2-Linux-Kernel/releases/tag/linux-msft-wsl-5.15.90.1"
        }
        
        with pytest.raises(ValueError):
            self.client._parse_release_data(release_data)


class TestGitHubAPIClientIntegration:
    """GitHubAPIClientの統合テスト（モック使用）"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される初期化処理"""
        self.client = GitHubAPIClient()
        
    @patch('src.github_api.requests.Session.get')
    def test_get_latest_stable_release_success(self, mock_get):
        """最新安定版リリース取得の成功テスト"""
        # モックレスポンスを設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "X-RateLimit-Remaining": "5000",
            "X-RateLimit-Reset": str(int(time.time()) + 3600)
        }
        mock_response.json.return_value = [
            {
                "tag_name": "linux-msft-wsl-5.15.91.1-rc1",
                "name": "Linux-msft-wsl-5.15.91.1-rc1",
                "published_at": "2023-03-20T10:00:00Z",
                "prerelease": True,
                "html_url": "https://github.com/microsoft/WSL2-Linux-Kernel/releases/tag/linux-msft-wsl-5.15.91.1-rc1"
            },
            {
                "tag_name": "linux-msft-wsl-5.15.90.1",
                "name": "Linux-msft-wsl-5.15.90.1",
                "published_at": "2023-03-15T10:00:00Z",
                "prerelease": False,
                "html_url": "https://github.com/microsoft/WSL2-Linux-Kernel/releases/tag/linux-msft-wsl-5.15.90.1"
            }
        ]
        mock_get.return_value = mock_response
        
        release = self.client.get_latest_stable_release()
        
        assert release is not None
        assert release.tag_name == "linux-msft-wsl-5.15.90.1"
        assert release.prerelease is False
        mock_get.assert_called_once()
        
    @patch('src.github_api.requests.Session.get')
    def test_get_latest_stable_release_no_stable_releases(self, mock_get):
        """安定版リリースが存在しない場合のテスト"""
        # プレリリースのみのモックレスポンス
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "X-RateLimit-Remaining": "5000"
        }
        mock_response.json.return_value = [
            {
                "tag_name": "linux-msft-wsl-5.15.91.1-rc1",
                "name": "Linux-msft-wsl-5.15.91.1-rc1",
                "published_at": "2023-03-20T10:00:00Z",
                "prerelease": True,
                "html_url": "https://github.com/microsoft/WSL2-Linux-Kernel/releases/tag/linux-msft-wsl-5.15.91.1-rc1"
            }
        ]
        mock_get.return_value = mock_response
        
        release = self.client.get_latest_stable_release()
        
        assert release is None
        
    @patch('src.github_api.requests.Session.get')
    def test_get_latest_stable_release_api_error(self, mock_get):
        """API呼び出しエラーのテスト"""
        mock_get.side_effect = RequestException("Network error")
        
        with pytest.raises(RequestException):
            self.client.get_latest_stable_release()
            
    @patch('src.github_api.requests.Session.get')
    def test_get_latest_stable_release_http_error(self, mock_get):
        """HTTPエラーのテスト"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {}
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        with pytest.raises(requests.HTTPError):
            self.client.get_latest_stable_release()
            
    @patch('src.github_api.requests.Session.get')
    def test_get_latest_stable_release_invalid_json(self, mock_get):
        """不正なJSONレスポンスのテスト"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError):
            self.client.get_latest_stable_release()


class TestRateLimitHandling:
    """レート制限処理のテスト"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される初期化処理"""
        self.client = GitHubAPIClient()
        
    def test_handle_rate_limit_normal(self):
        """通常のレスポンスでのレート制限処理テスト"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "X-RateLimit-Remaining": "4500",
            "X-RateLimit-Reset": str(int(time.time()) + 3600)
        }
        
        # エラーが発生しないことを確認
        self.client._handle_rate_limit(mock_response)
        
    def test_handle_rate_limit_low_remaining(self):
        """残りリクエスト数が少ない場合のテスト"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "X-RateLimit-Remaining": "5",
            "X-RateLimit-Reset": str(int(time.time()) + 3600)
        }
        
        # 警告ログが出力されるが、エラーは発生しない
        self.client._handle_rate_limit(mock_response)
        
    @patch('src.github_api.time.sleep')
    def test_handle_rate_limit_exceeded(self, mock_sleep):
        """レート制限に達した場合のテスト"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(time.time()) + 60)
        }
        
        self.client._handle_rate_limit(mock_response)
        
        # sleep が呼ばれることを確認
        mock_sleep.assert_called_once()
        args = mock_sleep.call_args[0]
        assert args[0] > 0  # 待機時間が正の値であることを確認
        
    @patch('src.github_api.time.sleep')
    def test_handle_rate_limit_exceeded_no_reset_time(self, mock_sleep):
        """レート制限に達したがリセット時間が不明な場合のテスト"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {
            "X-RateLimit-Remaining": "0"
        }
        
        self.client._handle_rate_limit(mock_response)
        
        # デフォルトの60秒待機が呼ばれることを確認
        mock_sleep.assert_called_once_with(60)
        
    def test_handle_rate_limit_no_headers(self):
        """レート制限ヘッダーが存在しない場合のテスト"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        
        # エラーが発生しないことを確認
        self.client._handle_rate_limit(mock_response)