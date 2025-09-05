"""E2E統合テスト - 実際の通知表示テスト"""

from unittest.mock import Mock, patch

import pytest

from src.main import WSLKernelWatcherApp


class TestE2EIntegration:
    """E2E統合テストクラス"""

    @pytest.fixture
    def watcher(self):
        """WSLカーネル監視インスタンス"""
        return WSLKernelWatcherApp()

    @patch("subprocess.run")
    @patch("requests.Session.get")
    @patch("src.notification.Toast")
    def test_full_notification_workflow(
        self, mock_toast, mock_session_get, mock_subprocess, watcher
    ):
        """完全な通知ワークフローテスト"""
        # アプリケーション初期化
        assert watcher.initialize() is True

        # モック設定
        mock_subprocess.return_value = Mock(
            returncode=0, stdout="5.15.90.1-microsoft-standard-WSL2"
        )

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

        mock_toast_instance = Mock()
        mock_toast.return_value = mock_toast_instance

        # 手動でバージョンチェックを実行
        current_version = watcher.wsl_utils.get_current_kernel_version()
        latest_release = watcher.github_client.get_latest_stable_release()

        assert "5.15.90.1" in current_version
        assert latest_release.tag_name == "linux-msft-wsl-5.15.95.1"

        # バージョン比較
        comparison = watcher.wsl_utils.compare_versions(current_version, "5.15.95.1")
        assert comparison == -1  # current < latest

    @patch("subprocess.run")
    @patch("requests.Session.get")
    def test_manual_check_trigger(self, mock_session_get, mock_subprocess, watcher):
        """手動チェックトリガーテスト"""
        # アプリケーション初期化
        assert watcher.initialize() is True

        # モック設定
        mock_subprocess.return_value = Mock(
            returncode=0, stdout="5.15.90.1-microsoft-standard-WSL2"
        )

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

        # 基本的なチェック機能をテスト
        current_version = watcher.wsl_utils.get_current_kernel_version()
        latest_release = watcher.github_client.get_latest_stable_release()

        # 結果確認
        assert current_version is not None
        assert latest_release is not None
        assert latest_release.tag_name == "linux-msft-wsl-5.15.95.1"

    def test_notification_content_format(self):
        """通知内容フォーマットテスト"""
        from src.config import Config
        from src.notification import NotificationManager
        from src.wsl_utils import WSLUtils

        config = Config()
        wsl_utils = WSLUtils()
        notification_manager = NotificationManager(config, wsl_utils)

        # 通知内容の生成テスト（実際のメソッドを使用）
        with patch("src.notification.Toast") as mock_toast:
            mock_toast_instance = Mock()
            mock_toast.return_value = mock_toast_instance

            notification_manager.show_update_notification("5.15.95.1", "5.15.90.1")

            # Toastが呼び出されたことを確認
            mock_toast.assert_called_once()
