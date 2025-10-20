"""統合テスト"""

from unittest.mock import Mock, patch

from src.main import WSLKernelWatcher


class TestIntegration:
    """統合テスト"""

    @patch("src.main.ConfigManager")
    @patch("src.docker_notifier.DockerNotifier.send_notification")
    @patch("requests.Session.get")
    async def test_full_workflow_new_release(
        self, mock_get, mock_send_notification, mock_config_manager
    ):
        """新リリース検出から通知までの完全ワークフローテスト"""
        # 設定モック
        mock_config = Mock()
        mock_config.repository_url = "microsoft/WSL2-Linux-Kernel"
        mock_config.check_interval_minutes = 1
        mock_config.log_level = "INFO"
        mock_config_manager.load.return_value = mock_config

        # GitHub APIレスポンスモック
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"X-RateLimit-Remaining": "100"}
        mock_response.json.return_value = [
            {
                "tag_name": "linux-msft-wsl-5.15.95.1",
                "name": "WSL2 Linux Kernel 5.15.95.1",
                "published_at": "2024-01-01T00:00:00Z",
                "prerelease": False,
                "html_url": "https://github.com/microsoft/WSL2-Linux-Kernel/releases/tag/linux-msft-wsl-5.15.95.1",
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # 通知モック
        mock_send_notification.return_value = True

        # テスト実行
        watcher = WSLKernelWatcher()

        # 初回チェック（バージョン設定）
        await watcher.check_for_updates()
        assert watcher.current_version == "linux-msft-wsl-5.15.95.1"

        # 新バージョンのモック
        mock_response.json.return_value = [
            {
                "tag_name": "linux-msft-wsl-5.15.96.1",
                "name": "WSL2 Linux Kernel 5.15.96.1",
                "published_at": "2024-01-02T00:00:00Z",
                "prerelease": False,
                "html_url": "https://github.com/microsoft/WSL2-Linux-Kernel/releases/tag/linux-msft-wsl-5.15.96.1",
            }
        ]

        # 2回目チェック（新バージョン検出・通知）
        await watcher.check_for_updates()

        # 検証
        assert watcher.current_version == "linux-msft-wsl-5.15.96.1"
        mock_send_notification.assert_called_once()

        # 通知引数の検証
        call_args = mock_send_notification.call_args[0]
        assert "WSL2カーネル更新通知" in call_args[0]
        assert "5.15.96.1" in call_args[1]
        assert "5.15.95.1" in call_args[1]

    @patch("src.main.ConfigManager")
    @patch("requests.Session.get")
    async def test_prerelease_filtering(self, mock_get, mock_config_manager):
        """プレリリース除外の統合テスト"""
        # 設定モック
        mock_config = Mock()
        mock_config.repository_url = "microsoft/WSL2-Linux-Kernel"
        mock_config.check_interval_minutes = 1
        mock_config.log_level = "INFO"
        mock_config_manager.load.return_value = mock_config

        # プレリリースを含むレスポンスモック
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"X-RateLimit-Remaining": "100"}
        mock_response.json.return_value = [
            {
                "tag_name": "linux-msft-wsl-5.15.96.1-rc1",
                "name": "WSL2 Linux Kernel 5.15.96.1 RC1",
                "published_at": "2024-01-02T00:00:00Z",
                "prerelease": True,
                "html_url": "https://github.com/microsoft/WSL2-Linux-Kernel/releases/tag/linux-msft-wsl-5.15.96.1-rc1",
            },
            {
                "tag_name": "linux-msft-wsl-5.15.95.1",
                "name": "WSL2 Linux Kernel 5.15.95.1",
                "published_at": "2024-01-01T00:00:00Z",
                "prerelease": False,
                "html_url": "https://github.com/microsoft/WSL2-Linux-Kernel/releases/tag/linux-msft-wsl-5.15.95.1",
            },
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # テスト実行
        watcher = WSLKernelWatcher()
        await watcher.check_for_updates()

        # 検証：プレリリースをスキップして安定版を選択
        assert watcher.current_version == "linux-msft-wsl-5.15.95.1"

    @patch("src.main.ConfigManager")
    @patch("requests.Session.get")
    async def test_api_error_handling(self, mock_get, mock_config_manager):
        """API エラーハンドリングの統合テスト"""
        # 設定モック
        mock_config = Mock()
        mock_config.repository_url = "microsoft/WSL2-Linux-Kernel"
        mock_config.check_interval_minutes = 1
        mock_config.log_level = "INFO"
        mock_config_manager.load.return_value = mock_config

        # API エラーモック
        mock_get.side_effect = Exception("Network Error")

        # テスト実行
        watcher = WSLKernelWatcher()

        # エラーが発生してもアプリケーションがクラッシュしないことを確認
        await watcher.check_for_updates()

        # 検証：バージョンは設定されない
        assert watcher.current_version is None
