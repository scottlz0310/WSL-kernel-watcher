"""GitHub監視モジュールのテスト"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
import requests

from src_v2.github_watcher import GitHubWatcher, Release


class TestGitHubWatcher:
    """GitHubWatcherクラスのテスト"""

    def setup_method(self):
        """テストセットアップ"""
        self.watcher = GitHubWatcher("test/repo")

    def test_init(self):
        """初期化テスト"""
        assert self.watcher.repository_url == "test/repo"
        assert self.watcher.base_url == "https://api.github.com"
        assert self.watcher.session is not None

    @patch("requests.Session.get")
    def test_get_latest_stable_release_success(self, mock_get):
        """最新安定版リリース取得成功テスト"""
        # モックレスポンス作成
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"X-RateLimit-Remaining": "100"}
        mock_response.json.return_value = [
            {
                "tag_name": "v5.15.95.1",
                "name": "Release v5.15.95.1",
                "published_at": "2024-01-01T00:00:00Z",
                "prerelease": False,
                "html_url": "https://github.com/test/repo/releases/tag/v5.15.95.1",
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # テスト実行
        release = self.watcher.get_latest_stable_release()

        # 検証
        assert release is not None
        assert release.tag_name == "v5.15.95.1"
        assert release.name == "Release v5.15.95.1"
        assert not release.prerelease

    @patch("requests.Session.get")
    def test_get_latest_stable_release_no_stable(self, mock_get):
        """安定版なしテスト"""
        # プレリリースのみのモックレスポンス
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"X-RateLimit-Remaining": "100"}
        mock_response.json.return_value = [
            {
                "tag_name": "v5.15.95.1-rc1",
                "name": "Release v5.15.95.1-rc1",
                "published_at": "2024-01-01T00:00:00Z",
                "prerelease": True,
                "html_url": "https://github.com/test/repo/releases/tag/v5.15.95.1-rc1",
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # テスト実行
        release = self.watcher.get_latest_stable_release()

        # 検証
        assert release is None

    @patch("requests.Session.get")
    def test_get_latest_stable_release_api_error(self, mock_get):
        """API呼び出しエラーテスト"""
        # エラーレスポンス
        mock_get.side_effect = requests.RequestException("API Error")

        # テスト実行・検証
        with pytest.raises(requests.RequestException):
            self.watcher.get_latest_stable_release()

    def test_is_prerelease_flag_true(self):
        """プレリリースフラグTrueテスト"""
        release_data = {"prerelease": True, "tag_name": "v1.0.0"}
        assert self.watcher._is_prerelease(release_data) is True

    def test_is_prerelease_tag_name(self):
        """タグ名によるプレリリース判定テスト"""
        test_cases = [
            ("v1.0.0-rc1", True),
            ("v1.0.0-alpha", True),
            ("v1.0.0-beta", True),
            ("v1.0.0-preview", True),
            ("v1.0.0", False),
            ("v1.0.0-stable", False),
        ]

        for tag_name, expected in test_cases:
            release_data = {"prerelease": False, "tag_name": tag_name}
            assert self.watcher._is_prerelease(release_data) == expected

    def test_parse_release(self):
        """リリースデータ解析テスト"""
        release_data = {
            "tag_name": "v5.15.95.1",
            "name": "Release v5.15.95.1",
            "published_at": "2024-01-01T12:00:00Z",
            "prerelease": False,
            "html_url": "https://github.com/test/repo/releases/tag/v5.15.95.1",
        }

        release = self.watcher._parse_release(release_data)

        assert isinstance(release, Release)
        assert release.tag_name == "v5.15.95.1"
        assert release.name == "Release v5.15.95.1"
        assert isinstance(release.published_at, datetime)
        assert not release.prerelease
        assert (
            release.html_url == "https://github.com/test/repo/releases/tag/v5.15.95.1"
        )
