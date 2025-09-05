"""
メインアプリケーション統合テスト

エンドツーエンドの動作確認テスト、各コンポーネント間の連携テスト、
異常系のテストケースを実装します。
要件: 全要件
"""

import threading
import time
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.config import Config
from src.github_api import Release
from src.main import WSLKernelWatcherApp, main


class TestWSLKernelWatcherApp:
    """WSLKernelWatcherAppクラスの統合テスト"""

    def setup_method(self):
        """各テストメソッドの前に実行される初期化処理"""
        self.app = WSLKernelWatcherApp()

    def teardown_method(self):
        """各テストメソッドの後に実行されるクリーンアップ処理"""
        if self.app:
            self.app.shutdown()

    @patch('src.main.TrayManager')
    @patch('src.main.Scheduler')
    @patch('src.main.NotificationManager')
    @patch('src.main.GitHubAPIClient')
    @patch('src.main.WSLUtils')
    @patch('src.main.ConfigManager')
    def test_initialize_success(self, mock_config_manager, mock_wsl_utils, 
                               mock_github_client, mock_notification_manager,
                               mock_scheduler, mock_tray_manager):
        """正常な初期化のテスト"""
        # モックの設定
        mock_config = Config()
        mock_config_manager.return_value.load_config.return_value = mock_config
        mock_wsl_utils.return_value.get_current_kernel_version.return_value = "5.15.90.1"
        
        mock_release = Release(
            tag_name="linux-msft-wsl-5.15.90.2",
            name="Linux-msft-wsl-5.15.90.2",
            published_at=None,
            prerelease=False,
            html_url="https://github.com/test"
        )
        mock_github_client.return_value.get_latest_stable_release.return_value = mock_release
        mock_notification_manager.return_value.is_notification_supported.return_value = True
        mock_tray_manager.return_value.is_running.return_value = True

        # 初期化を実行
        result = self.app.initialize()

        # 結果を検証
        assert result is True
        assert self.app.config is not None
        assert self.app.config_manager is not None
        assert self.app.github_client is not None
        assert self.app.wsl_utils is not None
        assert self.app.notification_manager is not None
        assert self.app.tray_manager is not None
        assert self.app.scheduler is not None

    @patch('src.main.ConfigManager')
    def test_initialize_config_failure(self, mock_config_manager):
        """設定初期化失敗のテスト"""
        # 設定読み込みでエラーを発生させる
        mock_config_manager.side_effect = Exception("設定読み込みエラー")

        # 初期化を実行
        result = self.app.initialize()

        # 結果を検証
        assert result is False
        assert self.app.config is None

    @patch('src.main.TrayManager')
    @patch('src.main.Scheduler')
    @patch('src.main.NotificationManager')
    @patch('src.main.GitHubAPIClient')
    @patch('src.main.WSLUtils')
    @patch('src.main.ConfigManager')
    def test_initialize_wsl_failure(self, mock_config_manager, mock_wsl_utils,
                                   mock_github_client, mock_notification_manager,
                                   mock_scheduler, mock_tray_manager):
        """WSL初期化失敗のテスト"""
        # 設定は正常、WSLでエラー
        mock_config = Config()
        mock_config_manager.return_value.load_config.return_value = mock_config
        mock_wsl_utils.side_effect = Exception("WSL接続エラー")

        # 初期化を実行
        result = self.app.initialize()

        # 結果を検証
        assert result is False

    @patch('src.main.TrayManager')
    @patch('src.main.Scheduler')
    @patch('src.main.NotificationManager')
    @patch('src.main.GitHubAPIClient')
    @patch('src.main.WSLUtils')
    @patch('src.main.ConfigManager')
    def test_start_success(self, mock_config_manager, mock_wsl_utils,
                          mock_github_client, mock_notification_manager,
                          mock_scheduler, mock_tray_manager):
        """正常な開始処理のテスト"""
        # 初期化を成功させる
        mock_config = Config()
        mock_config_manager.return_value.load_config.return_value = mock_config
        mock_wsl_utils.return_value.get_current_kernel_version.return_value = "5.15.90.1"
        
        mock_release = Release(
            tag_name="linux-msft-wsl-5.15.90.2",
            name="Linux-msft-wsl-5.15.90.2",
            published_at=None,
            prerelease=False,
            html_url="https://github.com/test"
        )
        mock_github_client.return_value.get_latest_stable_release.return_value = mock_release
        mock_notification_manager.return_value.is_notification_supported.return_value = True
        mock_tray_manager.return_value.is_running.return_value = True
        mock_scheduler.return_value.start_monitoring.return_value = True

        # 初期化と開始を実行
        init_result = self.app.initialize()
        start_result = self.app.start()

        # 結果を検証
        assert init_result is True
        assert start_result is True
        mock_scheduler.return_value.start_monitoring.assert_called_once()

    @patch('src.main.TrayManager')
    @patch('src.main.Scheduler')
    @patch('src.main.NotificationManager')
    @patch('src.main.GitHubAPIClient')
    @patch('src.main.WSLUtils')
    @patch('src.main.ConfigManager')
    def test_start_scheduler_failure(self, mock_config_manager, mock_wsl_utils,
                                    mock_github_client, mock_notification_manager,
                                    mock_scheduler, mock_tray_manager):
        """スケジューラー開始失敗のテスト"""
        # 初期化は成功、スケジューラー開始で失敗
        mock_config = Config()
        mock_config_manager.return_value.load_config.return_value = mock_config
        mock_wsl_utils.return_value.get_current_kernel_version.return_value = "5.15.90.1"
        
        mock_release = Release(
            tag_name="linux-msft-wsl-5.15.90.2",
            name="Linux-msft-wsl-5.15.90.2",
            published_at=None,
            prerelease=False,
            html_url="https://github.com/test"
        )
        mock_github_client.return_value.get_latest_stable_release.return_value = mock_release
        mock_notification_manager.return_value.is_notification_supported.return_value = True
        mock_tray_manager.return_value.is_running.return_value = True
        mock_scheduler.return_value.start_monitoring.return_value = False

        # 初期化と開始を実行
        init_result = self.app.initialize()
        start_result = self.app.start()

        # 結果を検証
        assert init_result is True
        assert start_result is False

    @patch('src.main.TrayManager')
    @patch('src.main.Scheduler')
    @patch('src.main.NotificationManager')
    @patch('src.main.GitHubAPIClient')
    @patch('src.main.WSLUtils')
    @patch('src.main.ConfigManager')
    def test_shutdown_process(self, mock_config_manager, mock_wsl_utils,
                             mock_github_client, mock_notification_manager,
                             mock_scheduler, mock_tray_manager):
        """終了処理のテスト"""
        # 初期化を成功させる
        mock_config = Config()
        mock_config_manager.return_value.load_config.return_value = mock_config
        mock_wsl_utils.return_value.get_current_kernel_version.return_value = "5.15.90.1"
        
        mock_release = Release(
            tag_name="linux-msft-wsl-5.15.90.2",
            name="Linux-msft-wsl-5.15.90.2",
            published_at=None,
            prerelease=False,
            html_url="https://github.com/test"
        )
        mock_github_client.return_value.get_latest_stable_release.return_value = mock_release
        mock_notification_manager.return_value.is_notification_supported.return_value = True
        mock_tray_manager.return_value.is_running.return_value = True

        # 初期化を実行
        self.app.initialize()

        # 終了処理を実行
        self.app.shutdown()

        # 結果を検証
        assert self.app._shutdown_requested is True
        mock_scheduler.return_value.stop_monitoring.assert_called_once()
        mock_tray_manager.return_value.quit_application.assert_called_once()

    @patch('src.main.TrayManager')
    @patch('src.main.Scheduler')
    @patch('src.main.NotificationManager')
    @patch('src.main.GitHubAPIClient')
    @patch('src.main.WSLUtils')
    @patch('src.main.ConfigManager')
    def test_component_integration(self, mock_config_manager, mock_wsl_utils,
                                  mock_github_client, mock_notification_manager,
                                  mock_scheduler, mock_tray_manager):
        """各コンポーネント間の連携テスト"""
        # モックの設定
        mock_config = Config()
        mock_config.check_interval_minutes = 15
        mock_config.repository_url = "microsoft/WSL2-Linux-Kernel"
        mock_config.enable_build_action = True
        mock_config.notification_enabled = True
        
        mock_config_manager.return_value.load_config.return_value = mock_config
        mock_wsl_utils.return_value.get_current_kernel_version.return_value = "5.15.90.1"
        
        mock_release = Release(
            tag_name="linux-msft-wsl-5.15.90.2",
            name="Linux-msft-wsl-5.15.90.2",
            published_at=None,
            prerelease=False,
            html_url="https://github.com/test"
        )
        mock_github_client.return_value.get_latest_stable_release.return_value = mock_release
        mock_notification_manager.return_value.is_notification_supported.return_value = True
        mock_tray_manager.return_value.is_running.return_value = True

        # 初期化を実行
        result = self.app.initialize()

        # 結果を検証
        assert result is True

        # 各コンポーネントが正しい設定で初期化されたことを確認
        mock_github_client.assert_called_once_with("microsoft/WSL2-Linux-Kernel")
        mock_notification_manager.assert_called_once_with(mock_config, mock_wsl_utils.return_value)
        mock_scheduler.assert_called_once_with(
            mock_config,
            mock_github_client.return_value,
            mock_wsl_utils.return_value,
            mock_notification_manager.return_value
        )

        # タスクトレイの終了コールバックが設定されたことを確認
        mock_tray_manager.return_value.set_quit_callback.assert_called_once()


class TestMainFunction:
    """main関数のテスト"""

    @patch('src.main.WSLKernelWatcherApp')
    @pytest.mark.timeout(5)  # 5秒でタイムアウト
    def test_main_normal_execution(self, mock_app_class):
        """正常実行のテスト"""
        # モックアプリケーションの設定
        mock_app = Mock()
        mock_app.initialize.return_value = True
        mock_app.start.return_value = True
        mock_app._shutdown_requested = False
        mock_app_class.return_value = mock_app

        # メインループを短時間で終了させるため、runメソッドをモック
        def mock_run():
            # 短時間待機後に終了フラグを設定
            time.sleep(0.1)
            mock_app._shutdown_requested = True

        mock_app.run = mock_run

        with pytest.raises(SystemExit) as exc_info:
            main()

        # 正常終了（exit code 0）を確認
        assert exc_info.value.code == 0

        # アプリケーションのメソッドが呼び出されたことを確認
        mock_app.initialize.assert_called_once()
        mock_app.start.assert_called_once()
        mock_app.shutdown.assert_called_once()

    @patch('src.main.WSLKernelWatcherApp')
    def test_main_initialization_failure(self, mock_app_class):
        """初期化失敗のテスト"""
        # モックアプリケーションの設定（初期化失敗）
        mock_app = Mock()
        mock_app.initialize.return_value = False
        mock_app_class.return_value = mock_app

        with pytest.raises(SystemExit) as exc_info:
            main()

        # エラー終了（exit code 1）を確認
        assert exc_info.value.code == 1

        # 初期化のみ呼び出され、開始は呼び出されないことを確認
        mock_app.initialize.assert_called_once()
        mock_app.start.assert_not_called()
        mock_app.shutdown.assert_called_once()

    @patch('src.main.WSLKernelWatcherApp')
    def test_main_start_failure(self, mock_app_class):
        """開始失敗のテスト"""
        # モックアプリケーションの設定（開始失敗）
        mock_app = Mock()
        mock_app.initialize.return_value = True
        mock_app.start.return_value = False
        mock_app_class.return_value = mock_app

        with pytest.raises(SystemExit) as exc_info:
            main()

        # エラー終了（exit code 1）を確認
        assert exc_info.value.code == 1

        # 初期化と開始が呼び出されることを確認
        mock_app.initialize.assert_called_once()
        mock_app.start.assert_called_once()
        mock_app.shutdown.assert_called_once()

    @patch('src.main.WSLKernelWatcherApp')
    @pytest.mark.timeout(3)  # 3秒でタイムアウト
    def test_main_keyboard_interrupt(self, mock_app_class):
        """キーボード割り込みのテスト"""
        # モックアプリケーションの設定
        mock_app = Mock()
        mock_app.initialize.return_value = True
        mock_app.start.return_value = True
        mock_app_class.return_value = mock_app

        # runメソッドでKeyboardInterruptを発生させる
        mock_app.run.side_effect = KeyboardInterrupt("テスト用割り込み")

        with pytest.raises(SystemExit) as exc_info:
            main()

        # 正常終了（exit code 0）を確認
        assert exc_info.value.code == 0

        # 終了処理が呼び出されることを確認
        mock_app.shutdown.assert_called_once()

    @patch('src.main.WSLKernelWatcherApp')
    def test_main_unexpected_error(self, mock_app_class):
        """予期しないエラーのテスト"""
        # モックアプリケーションの設定
        mock_app = Mock()
        mock_app.initialize.side_effect = RuntimeError("予期しないエラー")
        mock_app_class.return_value = mock_app

        with pytest.raises(SystemExit) as exc_info:
            main()

        # エラー終了（exit code 1）を確認
        assert exc_info.value.code == 1

        # 終了処理が呼び出されることを確認
        mock_app.shutdown.assert_called_once()


class TestEndToEndIntegration:
    """エンドツーエンド統合テスト"""

    @patch('src.main.TrayManager')
    @patch('src.main.Scheduler')
    @patch('src.main.NotificationManager')
    @patch('src.main.GitHubAPIClient')
    @patch('src.main.WSLUtils')
    @patch('src.main.ConfigManager')
    @pytest.mark.timeout(5)  # 5秒でタイムアウト
    def test_full_application_lifecycle(self, mock_config_manager, mock_wsl_utils,
                                       mock_github_client, mock_notification_manager,
                                       mock_scheduler, mock_tray_manager):
        """アプリケーション全体のライフサイクルテスト"""
        # 完全なモック設定
        mock_config = Config()
        mock_config.check_interval_minutes = 30
        mock_config.repository_url = "microsoft/WSL2-Linux-Kernel"
        mock_config.enable_build_action = False
        mock_config.notification_enabled = True
        mock_config.log_level = "INFO"

        mock_config_manager.return_value.load_config.return_value = mock_config
        mock_wsl_utils.return_value.get_current_kernel_version.return_value = "5.15.90.1"
        
        mock_release = Release(
            tag_name="linux-msft-wsl-5.15.90.2",
            name="Linux-msft-wsl-5.15.90.2",
            published_at=None,
            prerelease=False,
            html_url="https://github.com/microsoft/WSL2-Linux-Kernel/releases/tag/linux-msft-wsl-5.15.90.2"
        )
        mock_github_client.return_value.get_latest_stable_release.return_value = mock_release
        mock_notification_manager.return_value.is_notification_supported.return_value = True
        mock_tray_manager.return_value.is_running.return_value = True
        mock_scheduler.return_value.start_monitoring.return_value = True

        # アプリケーションを作成・初期化・開始
        app = WSLKernelWatcherApp()
        
        try:
            # 初期化
            init_result = app.initialize()
            assert init_result is True

            # 開始
            start_result = app.start()
            assert start_result is True

            # 各コンポーネントが正しく呼び出されたことを確認
            mock_config_manager.assert_called_once()
            mock_wsl_utils.assert_called_once()
            mock_github_client.assert_called_once_with("microsoft/WSL2-Linux-Kernel")
            mock_notification_manager.assert_called_once_with(mock_config, mock_wsl_utils.return_value)
            mock_tray_manager.assert_called_once_with("WSL Kernel Watcher")
            mock_scheduler.assert_called_once()

            # スケジューラーが開始されたことを確認
            mock_scheduler.return_value.start_monitoring.assert_called_once()

            # タスクトレイアイコンが作成されたことを確認
            mock_tray_manager.return_value.create_tray_icon.assert_called_once()

        finally:
            # 終了処理
            app.shutdown()

            # 終了処理が正しく呼び出されたことを確認
            mock_scheduler.return_value.stop_monitoring.assert_called_once()
            mock_tray_manager.return_value.quit_application.assert_called_once()

    @patch('src.main.TrayManager')
    @patch('src.main.Scheduler')
    @patch('src.main.NotificationManager')
    @patch('src.main.GitHubAPIClient')
    @patch('src.main.WSLUtils')
    @patch('src.main.ConfigManager')
    @pytest.mark.timeout(5)  # 5秒でタイムアウト
    def test_error_recovery_scenarios(self, mock_config_manager, mock_wsl_utils,
                                     mock_github_client, mock_notification_manager,
                                     mock_scheduler, mock_tray_manager):
        """エラー回復シナリオのテスト"""
        # 部分的な失敗シナリオ
        mock_config = Config()
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        # WSLは失敗するが、他は成功
        mock_wsl_utils.return_value.get_current_kernel_version.return_value = None
        
        # GitHub APIは成功
        mock_release = Release(
            tag_name="linux-msft-wsl-5.15.90.2",
            name="Linux-msft-wsl-5.15.90.2",
            published_at=None,
            prerelease=False,
            html_url="https://github.com/test"
        )
        mock_github_client.return_value.get_latest_stable_release.return_value = mock_release
        
        # 通知システムは利用不可
        mock_notification_manager.return_value.is_notification_supported.return_value = False
        
        # タスクトレイは成功
        mock_tray_manager.return_value.is_running.return_value = True

        app = WSLKernelWatcherApp()
        
        try:
            # 初期化（部分的な失敗があっても継続）
            result = app.initialize()
            
            # WSLの問題があっても、他のコンポーネントは初期化される
            assert result is True
            assert app.config is not None
            assert app.github_client is not None
            assert app.notification_manager is not None
            assert app.tray_manager is not None

        finally:
            app.shutdown()
