"""統合テスト"""

from unittest.mock import Mock, patch

from src_v2.main import WSLKernelWatcher


class TestIntegration:
    """統合テスト"""

    @patch("src_v2.main.ConfigManager")
    @patch("subprocess.run")
    @patch("requests.Session.get")
    async def test_full_workflow_new_release(
        self, mock_get, mock_subprocess, mock_config_manager
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

        # PowerShell実行モック
        mock_subprocess.return_value = Mock(returncode=0, stderr="")

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
        mock_subprocess.assert_called()

        # PowerShellコマンドの検証
        call_args = mock_subprocess.call_args[0][0]
        assert "wsl.exe" in call_args
        assert "powershell.exe" in call_args

    @patch("src_v2.main.ConfigManager")
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

    @patch("src_v2.main.ConfigManager")
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
