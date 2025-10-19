"""メインアプリケーションのテスト"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from src_v2.github_watcher import Release
from src_v2.main import WSLKernelWatcher, setup_logging


class TestSetupLogging:
    """ログ設定テスト"""

    @patch("logging.basicConfig")
    def test_setup_logging_info(self, mock_basic_config):
        """INFOレベルログ設定テスト"""
        setup_logging("INFO")

        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["level"] == 20  # logging.INFO


class TestWSLKernelWatcher:
    """WSLKernelWatcherクラスのテスト"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """テストセットアップ"""
        with patch("src_v2.main.ConfigManager") as mock_config_manager, \
             patch("src_v2.main.GitHubWatcher") as mock_watcher_class, \
             patch("src_v2.main.DockerNotifier") as mock_notifier_class, \
             patch("src_v2.main.setup_logging"):
            
            mock_config = Mock()
            mock_config.repository_url = "test/repo"
            mock_config.check_interval_minutes = 1
            mock_config.log_level = "INFO"
            mock_config_manager.load.return_value = mock_config

            self.mock_github_watcher = Mock()
            mock_watcher_class.return_value = self.mock_github_watcher

            self.mock_notifier = Mock()
            mock_notifier_class.return_value = self.mock_notifier

            self.watcher = WSLKernelWatcher()
            yield

    @patch("src_v2.main.ConfigManager")
    @patch("src_v2.main.GitHubWatcher")
    @patch("src_v2.main.DockerNotifier")
    @patch("src_v2.main.setup_logging")
    def test_init(
        self,
        mock_setup_logging,
        mock_notifier_class,
        mock_watcher_class,
        mock_config_manager,
    ):
        """初期化テスト"""
        # モック設定
        mock_config = Mock()
        mock_config.log_level = "DEBUG"
        mock_config_manager.load.return_value = mock_config

        # テスト実行
        watcher = WSLKernelWatcher()

        # 検証
        assert watcher.config is not None
        assert watcher.github_watcher is not None
        assert watcher.notifier is not None
        assert watcher.current_version is None
        mock_setup_logging.assert_called_once_with("DEBUG")

    @pytest.mark.asyncio
    async def test_check_for_updates_initial_version(self):
        """初回バージョン設定テスト"""
        # モック設定
        release = Release(
            tag_name="v5.15.95.1",
            name="Release v5.15.95.1",
            published_at=datetime.now(),
            prerelease=False,
            html_url="https://github.com/test/repo",
        )
        self.mock_github_watcher.get_latest_stable_release.return_value = release

        # テスト実行
        await self.watcher.check_for_updates()

        # 検証
        assert self.watcher.current_version == "v5.15.95.1"
        self.mock_notifier.notify_kernel_update.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_for_updates_new_version(self):
        """新バージョン検出テスト"""
        # 初期バージョン設定
        self.watcher.current_version = "v5.15.90.1"

        # モック設定
        release = Release(
            tag_name="v5.15.95.1",
            name="Release v5.15.95.1",
            published_at=datetime.now(),
            prerelease=False,
            html_url="https://github.com/test/repo",
        )
        self.mock_github_watcher.get_latest_stable_release.return_value = release
        self.mock_notifier.notify_kernel_update.return_value = True

        # テスト実行
        await self.watcher.check_for_updates()

        # 検証
        assert self.watcher.current_version == "v5.15.95.1"
        self.mock_notifier.notify_kernel_update.assert_called_once_with(
            "v5.15.95.1", "v5.15.90.1"
        )

    @pytest.mark.asyncio
    async def test_check_for_updates_no_change(self):
        """バージョン変更なしテスト"""
        # 初期バージョン設定
        self.watcher.current_version = "v5.15.95.1"

        # モック設定
        release = Release(
            tag_name="v5.15.95.1",
            name="Release v5.15.95.1",
            published_at=datetime.now(),
            prerelease=False,
            html_url="https://github.com/test/repo",
        )
        self.mock_github_watcher.get_latest_stable_release.return_value = release

        # テスト実行
        await self.watcher.check_for_updates()

        # 検証
        assert self.watcher.current_version == "v5.15.95.1"
        self.mock_notifier.notify_kernel_update.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_for_updates_no_release(self):
        """リリース情報なしテスト"""
        # モック設定
        self.mock_github_watcher.get_latest_stable_release.return_value = None

        # テスト実行
        await self.watcher.check_for_updates()

        # 検証
        assert self.watcher.current_version is None
        self.mock_notifier.notify_kernel_update.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_for_updates_notification_failure(self):
        """通知失敗テスト"""
        # 初期バージョン設定
        self.watcher.current_version = "v5.15.90.1"

        # モック設定
        release = Release(
            tag_name="v5.15.95.1",
            name="Release v5.15.95.1",
            published_at=datetime.now(),
            prerelease=False,
            html_url="https://github.com/test/repo",
        )
        self.mock_github_watcher.get_latest_stable_release.return_value = release
        self.mock_notifier.notify_kernel_update.return_value = False

        # テスト実行
        await self.watcher.check_for_updates()

        # 検証（通知失敗時はバージョン更新しない）
        assert self.watcher.current_version == "v5.15.90.1"
