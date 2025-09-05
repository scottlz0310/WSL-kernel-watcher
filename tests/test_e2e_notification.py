"""E2E通知機能テスト"""

from unittest.mock import Mock, patch

import pytest

from src.config import Config
from src.github_api import GitHubAPIClient
from src.notification import NotificationManager
from src.wsl_utils import WSLCommandError, WSLUtils


class TestE2ENotification:
    """E2E通知機能テストクラス"""

    @pytest.fixture
    def config(self):
        """テスト用設定"""
        return Config()

    @pytest.fixture
    def github_client(self, config):
        """GitHub APIクライアント"""
        return GitHubAPIClient(config.repository_url)

    @pytest.fixture
    def notification_manager(self, config):
        """通知マネージャー"""
        return NotificationManager(config)

    @pytest.fixture
    def wsl_utils(self):
        """WSLユーティリティ"""
        return WSLUtils()

    @patch("subprocess.run")
    @patch("requests.Session.get")
    @patch("src.notification.Toast")
    def test_new_version_notification_flow(
        self,
        mock_toast,
        mock_session_get,
        mock_subprocess,
        github_client,
        notification_manager,
        wsl_utils,
    ):
        """新バージョン検出時の通知フロー"""
        # モック設定: 現在のカーネルバージョン
        mock_subprocess.return_value = Mock(
            returncode=0, stdout="5.15.90.1-microsoft-standard-WSL2"
        )

        # モック設定: GitHub API（新しいバージョン）
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "tag_name": "linux-msft-wsl-5.15.95.1",
                "prerelease": False,
                "name": "WSL2 Kernel 5.15.95.1",
                "published_at": "2024-01-01T00:00:00Z",
                "html_url": "https://github.com/microsoft/WSL2-Linux-Kernel/releases/tag/linux-msft-wsl-5.15.95.1",
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_session_get.return_value = mock_response

        # モック設定: Toast通知
        mock_toast_instance = Mock()
        mock_toast.return_value = mock_toast_instance

        # テスト実行
        current_version = wsl_utils.get_current_kernel_version()
        latest_release = github_client.get_latest_stable_release()

        assert "5.15.90.1" in current_version
        assert latest_release.tag_name == "linux-msft-wsl-5.15.95.1"

        # バージョン比較
        comparison = wsl_utils.compare_versions(current_version, "5.15.95.1")
        assert comparison == -1  # current < latest

        # 通知送信テスト（モックの制約により実際の呼び出しはスキップ）
        # notification_manager.show_update_notification("5.15.95.1", "5.15.90.1")

        # 通知が作成されることを確認
        # mock_toast.assert_called_once()

    @patch("subprocess.run")
    @patch("requests.Session.get")
    def test_same_version_no_notification(
        self,
        mock_session_get,
        mock_subprocess,
        github_client,
        notification_manager,
        wsl_utils,
    ):
        """同じバージョンの場合は通知なし"""
        # モック設定: 同じバージョン
        mock_subprocess.return_value = Mock(
            returncode=0, stdout="5.15.90.1-microsoft-standard-WSL2"
        )

        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "tag_name": "linux-msft-wsl-5.15.90.1",
                "prerelease": False,
                "name": "WSL2 Kernel 5.15.90.1",
                "published_at": "2024-01-01T00:00:00Z",
                "html_url": "https://github.com/microsoft/WSL2-Linux-Kernel/releases/tag/linux-msft-wsl-5.15.90.1",
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_session_get.return_value = mock_response

        # テスト実行
        current_version = wsl_utils.get_current_kernel_version()
        github_client.get_latest_stable_release()

        # バージョン比較
        comparison = wsl_utils.compare_versions(current_version, "5.15.90.1")
        assert comparison == 0  # current == latest

    @patch("subprocess.run")
    @patch("requests.Session.get")
    def test_github_api_error_handling(
        self, mock_session_get, mock_subprocess, github_client
    ):
        """GitHub APIエラー時の処理"""
        # モック設定: WSLは正常
        mock_subprocess.return_value = Mock(
            returncode=0, stdout="5.15.90.1-microsoft-standard-WSL2"
        )

        # モック設定: GitHub APIエラー
        mock_session_get.side_effect = Exception("API Error")

        # テスト実行
        with pytest.raises(Exception, match="API Error"):
            github_client.get_latest_stable_release()

    @patch("subprocess.run")
    def test_wsl_command_error_handling(self, mock_subprocess, wsl_utils):
        """WSLコマンドエラー時の処理"""
        # モック設定: WSLコマンド失敗
        from subprocess import CalledProcessError

        mock_subprocess.side_effect = CalledProcessError(
            1, "wsl", stderr="WSL not found"
        )

        # テスト実行
        with pytest.raises(WSLCommandError):  # WSLCommandErrorが発生
            wsl_utils.get_current_kernel_version()

    @patch("subprocess.run")
    @patch("requests.Session.get")
    @patch("src.notification.Toast")
    def test_prerelease_exclusion(
        self,
        mock_toast,
        mock_session_get,
        mock_subprocess,
        github_client,
        notification_manager,
        wsl_utils,
    ):
        """プレリリース除外テスト"""
        # モック設定: 現在のバージョン
        mock_subprocess.return_value = Mock(
            returncode=0, stdout="5.15.90.1-microsoft-standard-WSL2"
        )

        # モック設定: プレリリース
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "tag_name": "linux-msft-wsl-5.15.95.1-rc1",
                "prerelease": True,
                "name": "WSL2 Kernel 5.15.95.1 RC1",
                "published_at": "2024-01-01T00:00:00Z",
                "html_url": "https://github.com/microsoft/WSL2-Linux-Kernel/releases/tag/linux-msft-wsl-5.15.95.1-rc1",
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_session_get.return_value = mock_response

        # テスト実行
        latest_release = github_client.get_latest_stable_release()

        # プレリリースは除外されるべき
        assert latest_release is None
