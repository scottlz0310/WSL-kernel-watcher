"""スケジューリングシステムの単体テスト"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from apscheduler.schedulers.background import BackgroundScheduler

from src.config import Config
from src.github_api import GitHubAPIClient, Release
from src.notification import NotificationManager
from src.scheduler import Scheduler
from src.wsl_utils import WSLCommandError, WSLUtils


class TestScheduler:
    """Schedulerクラスのテストケース"""

    @pytest.fixture
    def mock_config(self):
        """テスト用の設定オブジェクト"""
        return Config(
            check_interval_minutes=30,
            repository_url="microsoft/WSL2-Linux-Kernel",
            enable_build_action=False,
            notification_enabled=True,
            log_level="INFO",
        )

    @pytest.fixture
    def mock_github_client(self):
        """モックGitHub APIクライアント"""
        return Mock(spec=GitHubAPIClient)

    @pytest.fixture
    def mock_wsl_utils(self):
        """モックWSLユーティリティ"""
        return Mock(spec=WSLUtils)

    @pytest.fixture
    def mock_notification_manager(self):
        """モック通知マネージャー"""
        return Mock(spec=NotificationManager)

    @pytest.fixture
    def scheduler(
        self, mock_config, mock_github_client, mock_wsl_utils, mock_notification_manager
    ):
        """テスト用のSchedulerインスタンス"""
        return Scheduler(
            config=mock_config,
            github_client=mock_github_client,
            wsl_utils=mock_wsl_utils,
            notification_manager=mock_notification_manager,
        )

    @pytest.fixture
    def sample_release(self):
        """テスト用のリリースオブジェクト"""
        return Release(
            tag_name="linux-msft-wsl-5.15.90.1",
            name="Linux-msft-wsl-5.15.90.1",
            published_at=datetime.now(),
            prerelease=False,
            html_url="https://github.com/microsoft/WSL2-Linux-Kernel/releases/tag/linux-msft-wsl-5.15.90.1",
        )

    def test_scheduler_initialization(self, scheduler, mock_config):
        """Schedulerの初期化テスト"""
        assert scheduler.config == mock_config
        assert not scheduler.is_monitoring()
        assert scheduler.get_last_check_time() is None
        assert isinstance(scheduler.scheduler, BackgroundScheduler)

    @pytest.mark.timeout(5)  # 5秒でタイムアウト
    def test_start_monitoring_success(self, scheduler):
        """監視開始の成功テスト"""
        with patch.object(scheduler, "check_for_updates") as mock_check:
            mock_check.return_value = True

            result = scheduler.start_monitoring()

            assert result is True
            assert scheduler.is_monitoring()
            mock_check.assert_called_once()

    def test_start_monitoring_already_started(self, scheduler):
        """既に監視が開始されている場合のテスト"""
        scheduler._is_monitoring = True

        result = scheduler.start_monitoring()

        assert result is True
        assert scheduler.is_monitoring()

    def test_start_monitoring_failure(self, scheduler):
        """監視開始の失敗テスト"""
        with patch.object(
            scheduler.scheduler, "start", side_effect=Exception("Test error")
        ):
            result = scheduler.start_monitoring()

            assert result is False
            assert not scheduler.is_monitoring()

    @pytest.mark.timeout(5)  # 5秒でタイムアウト
    def test_stop_monitoring_success(self, scheduler):
        """監視停止の成功テスト"""
        scheduler._is_monitoring = True

        result = scheduler.stop_monitoring()

        assert result is True
        assert not scheduler.is_monitoring()

    def test_stop_monitoring_not_started(self, scheduler):
        """監視が開始されていない場合の停止テスト"""
        result = scheduler.stop_monitoring()

        assert result is True
        assert not scheduler.is_monitoring()

    def test_stop_monitoring_failure(self, scheduler):
        """監視停止の失敗テスト"""
        scheduler._is_monitoring = True

        # schedulerを開始状態にする
        scheduler.scheduler.start()

        with patch.object(
            scheduler.scheduler, "shutdown", side_effect=Exception("Test error")
        ):
            result = scheduler.stop_monitoring()

            assert result is False

        # テスト後のクリーンアップ
        try:
            scheduler.scheduler.shutdown(wait=False)
        except Exception:
            pass

    def test_check_for_updates_new_version_available(
        self,
        scheduler,
        mock_github_client,
        mock_wsl_utils,
        mock_notification_manager,
        sample_release,
    ):
        """新しいバージョンが利用可能な場合の更新チェックテスト"""
        # モックの設定
        mock_github_client.get_latest_stable_release.return_value = sample_release
        mock_wsl_utils.get_current_kernel_version.return_value = (
            "5.15.89.1-microsoft-standard-WSL2"
        )
        mock_wsl_utils.compare_versions.return_value = -1  # 新しいバージョンが利用可能
        mock_notification_manager.show_update_notification.return_value = True

        result = scheduler.check_for_updates()

        assert result is True
        assert scheduler.get_last_check_time() is not None
        mock_github_client.get_latest_stable_release.assert_called_once()
        mock_wsl_utils.get_current_kernel_version.assert_called_once()
        mock_notification_manager.show_update_notification.assert_called_once_with(
            "5.15.89.1-microsoft-standard-WSL2", "linux-msft-wsl-5.15.90.1"
        )

    def test_check_for_updates_current_version_latest(
        self,
        scheduler,
        mock_github_client,
        mock_wsl_utils,
        mock_notification_manager,
        sample_release,
    ):
        """現在のバージョンが最新の場合の更新チェックテスト"""
        # モックの設定
        mock_github_client.get_latest_stable_release.return_value = sample_release
        mock_wsl_utils.get_current_kernel_version.return_value = (
            "5.15.90.1-microsoft-standard-WSL2"
        )
        mock_wsl_utils.compare_versions.return_value = 0  # 同じバージョン

        result = scheduler.check_for_updates()

        assert result is True
        mock_notification_manager.show_update_notification.assert_not_called()

    def test_check_for_updates_current_version_newer(
        self,
        scheduler,
        mock_github_client,
        mock_wsl_utils,
        mock_notification_manager,
        sample_release,
    ):
        """現在のバージョンが最新より新しい場合の更新チェックテスト"""
        # モックの設定
        mock_github_client.get_latest_stable_release.return_value = sample_release
        mock_wsl_utils.get_current_kernel_version.return_value = (
            "5.15.91.1-microsoft-standard-WSL2"
        )
        mock_wsl_utils.compare_versions.return_value = 1  # 現在の方が新しい

        result = scheduler.check_for_updates()

        assert result is True
        mock_notification_manager.show_update_notification.assert_not_called()

    def test_check_for_updates_github_api_failure(
        self, scheduler, mock_github_client, mock_notification_manager
    ):
        """GitHub API呼び出し失敗時の更新チェックテスト"""
        # モックの設定
        mock_github_client.get_latest_stable_release.return_value = None

        result = scheduler.check_for_updates()

        assert result is False
        mock_notification_manager.show_update_notification.assert_not_called()

    def test_check_for_updates_wsl_failure(
        self,
        scheduler,
        mock_github_client,
        mock_wsl_utils,
        mock_notification_manager,
        sample_release,
    ):
        """WSLコマンド失敗時の更新チェックテスト"""
        # モックの設定
        mock_github_client.get_latest_stable_release.return_value = sample_release
        mock_wsl_utils.get_current_kernel_version.return_value = None

        result = scheduler.check_for_updates()

        assert result is False
        mock_notification_manager.show_update_notification.assert_not_called()

    def test_check_for_updates_notification_failure(
        self,
        scheduler,
        mock_github_client,
        mock_wsl_utils,
        mock_notification_manager,
        sample_release,
    ):
        """通知表示失敗時の更新チェックテスト"""
        # モックの設定
        mock_github_client.get_latest_stable_release.return_value = sample_release
        mock_wsl_utils.get_current_kernel_version.return_value = (
            "5.15.89.1-microsoft-standard-WSL2"
        )
        mock_wsl_utils.compare_versions.return_value = -1
        mock_notification_manager.show_update_notification.return_value = False

        result = scheduler.check_for_updates()

        assert result is True  # チェック自体は成功
        mock_notification_manager.show_update_notification.assert_called_once()

    def test_check_for_updates_exception_handling(
        self, scheduler, mock_github_client, mock_notification_manager
    ):
        """例外発生時のエラーハンドリングテスト"""
        # モックの設定 - _perform_integrated_update_check内で例外が発生するようにする
        with patch.object(
            scheduler,
            "_perform_integrated_update_check",
            side_effect=Exception("Test error"),
        ):
            with patch.object(scheduler, "_handle_check_error") as mock_handle_error:
                result = scheduler.check_for_updates()

                assert result is False
                mock_handle_error.assert_called_once()

    def test_extract_version_from_tag(self, scheduler):
        """GitHubタグからのバージョン抽出テスト"""
        # 標準的なタグ形式
        version = scheduler._extract_version_from_tag("linux-msft-wsl-5.15.90.1")
        assert version == "5.15.90.1"

        # 異なる形式のタグ
        version = scheduler._extract_version_from_tag("v5.15.90.1")
        assert version == "5.15.90.1"

        # 数字のみのタグ
        version = scheduler._extract_version_from_tag("5.15.90.1")
        assert version == "5.15.90.1"

    def test_extract_version_from_kernel(self, scheduler):
        """WSLカーネルバージョンからのバージョン抽出テスト"""
        # 標準的なWSLカーネルバージョン
        version = scheduler._extract_version_from_kernel(
            "5.15.90.1-microsoft-standard-WSL2"
        )
        assert version == "5.15.90.1"

        # 異なる形式
        version = scheduler._extract_version_from_kernel("5.15.90.1-custom")
        assert version == "5.15.90.1"

        # バージョン番号のみ
        version = scheduler._extract_version_from_kernel("5.15.90.1")
        assert version == "5.15.90.1"

    def test_should_notify_enabled(self, scheduler):
        """通知が有効な場合の通知判定テスト"""
        scheduler.config.notification_enabled = True
        scheduler._last_known_version = None

        result = scheduler._should_notify("5.15.90.1")

        assert result is True

    def test_should_notify_disabled(self, scheduler):
        """通知が無効な場合の通知判定テスト"""
        scheduler.config.notification_enabled = False

        result = scheduler._should_notify("5.15.90.1")

        assert result is False

    def test_should_notify_already_notified(self, scheduler):
        """既に通知済みの場合の通知判定テスト"""
        scheduler.config.notification_enabled = True
        scheduler._last_known_version = "5.15.90.1"

        result = scheduler._should_notify("5.15.90.1")

        assert result is False

    def test_handle_check_error_github_api_error(
        self, scheduler, mock_notification_manager
    ):
        """GitHub APIエラーのハンドリングテスト"""
        error = Exception("GitHub API error")

        scheduler._handle_check_error(error)

        # エラー通知が表示されることを確認
        mock_notification_manager.show_error_notification.assert_called_once()

    def test_handle_check_error_wsl_error(self, scheduler, mock_notification_manager):
        """WSLエラーのハンドリングテスト"""
        error = WSLCommandError("WSL command failed")

        scheduler._handle_check_error(error)

        # エラー通知が表示されることを確認
        mock_notification_manager.show_error_notification.assert_called_once()

    def test_get_monitoring_status(self, scheduler):
        """監視状況取得テスト"""
        scheduler._is_monitoring = True
        scheduler._last_check_time = datetime.now()
        scheduler._last_known_version = "5.15.90.1"

        status = scheduler.get_monitoring_status()

        assert status["is_monitoring"] is True
        assert status["check_interval_minutes"] == 30
        assert status["last_check_time"] is not None
        assert status["last_known_version"] == "5.15.90.1"
        assert status["notification_enabled"] is True
        assert status["build_action_enabled"] is False

    def test_update_check_interval_valid(self, scheduler):
        """有効なチェック間隔更新テスト"""
        result = scheduler.update_check_interval(60)

        assert result is True
        assert scheduler.config.check_interval_minutes == 60

    def test_update_check_interval_invalid_too_small(self, scheduler):
        """無効なチェック間隔（小さすぎる）更新テスト"""
        result = scheduler.update_check_interval(0)

        assert result is False
        assert scheduler.config.check_interval_minutes == 30  # 元の値のまま

    def test_update_check_interval_invalid_too_large(self, scheduler):
        """無効なチェック間隔（大きすぎる）更新テスト"""
        result = scheduler.update_check_interval(1500)

        assert result is False
        assert scheduler.config.check_interval_minutes == 30  # 元の値のまま

    @pytest.mark.timeout(5)  # 5秒でタイムアウト
    def test_update_check_interval_with_monitoring_restart(self, scheduler):
        """監視中のチェック間隔更新テスト（監視再起動）"""
        scheduler._is_monitoring = True

        with (
            patch.object(scheduler, "stop_monitoring") as mock_stop,
            patch.object(scheduler, "start_monitoring") as mock_start,
        ):
            mock_stop.return_value = True
            mock_start.return_value = True

            result = scheduler.update_check_interval(60)

            assert result is True
            mock_stop.assert_called_once()
            mock_start.assert_called_once()

    def test_perform_integrated_update_check_success(
        self, scheduler, mock_github_client, mock_wsl_utils, sample_release
    ):
        """統合更新チェック成功テスト"""
        # モックの設定
        mock_github_client.get_latest_stable_release.return_value = sample_release
        mock_wsl_utils.get_current_kernel_version.return_value = (
            "5.15.89.1-microsoft-standard-WSL2"
        )
        mock_wsl_utils.compare_versions.return_value = -1

        result = scheduler._perform_integrated_update_check()

        assert result is not None
        assert result["current_version"] == "5.15.89.1-microsoft-standard-WSL2"
        assert result["latest_version"] == "linux-msft-wsl-5.15.90.1"
        assert result["update_available"] is True
        assert result["comparison_result"] == -1

    def test_perform_integrated_update_check_github_failure(
        self, scheduler, mock_github_client
    ):
        """統合更新チェック（GitHub API失敗）テスト"""
        mock_github_client.get_latest_stable_release.return_value = None

        result = scheduler._perform_integrated_update_check()

        assert result is None

    def test_perform_integrated_update_check_wsl_failure(
        self, scheduler, mock_github_client, mock_wsl_utils, sample_release
    ):
        """統合更新チェック（WSL失敗）テスト"""
        mock_github_client.get_latest_stable_release.return_value = sample_release
        mock_wsl_utils.get_current_kernel_version.return_value = None

        result = scheduler._perform_integrated_update_check()

        assert result is None

    def test_process_update_check_result_update_available_notify(
        self, scheduler, mock_notification_manager
    ):
        """更新チェック結果処理（更新あり・通知あり）テスト"""
        update_info = {
            "current_version": "5.15.89.1",
            "latest_version": "5.15.90.1",
            "update_available": True,
            "should_notify": True,
            "latest_release": Mock(),
        }

        with patch.object(
            scheduler, "_execute_notification_logic", return_value=True
        ) as mock_notify:
            result = scheduler._process_update_check_result(update_info)

            assert result is True
            mock_notify.assert_called_once_with(update_info)
            assert scheduler._last_known_version == "5.15.90.1"

    def test_process_update_check_result_update_available_no_notify(self, scheduler):
        """更新チェック結果処理（更新あり・通知なし）テスト"""
        update_info = {"update_available": True, "should_notify": False}

        result = scheduler._process_update_check_result(update_info)

        assert result is True

    def test_process_update_check_result_no_update(self, scheduler):
        """更新チェック結果処理（更新なし）テスト"""
        update_info = {"update_available": False, "should_notify": False}

        result = scheduler._process_update_check_result(update_info)

        assert result is True

    def test_execute_notification_logic_success(
        self, scheduler, mock_notification_manager
    ):
        """通知ロジック実行成功テスト"""
        update_info = {
            "current_version": "5.15.89.1",
            "latest_version": "5.15.90.1",
            "latest_release": Mock(
                html_url="https://example.com",
                published_at=datetime.now(),
                name="Test Release",
            ),
        }

        mock_notification_manager.show_update_notification.return_value = True

        with patch.object(
            scheduler, "_ensure_notification_click_handler"
        ) as mock_handler:
            result = scheduler._execute_notification_logic(update_info)

            assert result is True
            mock_notification_manager.show_update_notification.assert_called_once_with(
                "5.15.89.1", "5.15.90.1"
            )
            mock_handler.assert_called_once()

    def test_execute_notification_logic_failure(
        self, scheduler, mock_notification_manager
    ):
        """通知ロジック実行失敗テスト"""
        update_info = {
            "current_version": "5.15.89.1",
            "latest_version": "5.15.90.1",
            "latest_release": Mock(
                html_url="https://example.com",
                published_at=datetime.now(),
                name="Test Release",
            ),
        }

        mock_notification_manager.show_update_notification.return_value = False

        result = scheduler._execute_notification_logic(update_info)

        assert result is False

    def test_ensure_notification_click_handler(
        self, scheduler, mock_notification_manager
    ):
        """通知クリックハンドラー設定テスト"""
        scheduler._ensure_notification_click_handler()

        mock_notification_manager.register_click_handler.assert_called_once()

    def test_record_notification_interaction(self, scheduler):
        """通知インタラクション記録テスト"""
        # エラーが発生しないことを確認
        scheduler._record_notification_interaction("5.15.89.1", "5.15.90.1")

        # ログが記録されることを確認（実際のログ内容は検証しない）
        assert True  # 例外が発生しなければ成功


class TestSchedulerIntegration:
    """Schedulerの統合テスト"""

    @pytest.fixture
    def real_config(self):
        """実際の設定オブジェクト"""
        return Config(
            check_interval_minutes=1,  # テスト用に短い間隔
            repository_url="microsoft/WSL2-Linux-Kernel",
            enable_build_action=False,
            notification_enabled=True,
            log_level="DEBUG",
        )

    def test_scheduler_lifecycle(self, real_config):
        """スケジューラーのライフサイクル統合テスト"""
        # モックオブジェクトを作成
        mock_github_client = Mock(spec=GitHubAPIClient)
        mock_wsl_utils = Mock(spec=WSLUtils)
        mock_notification_manager = Mock(spec=NotificationManager)

        # Schedulerを作成
        scheduler = Scheduler(
            config=real_config,
            github_client=mock_github_client,
            wsl_utils=mock_wsl_utils,
            notification_manager=mock_notification_manager,
        )

        # 初期状態の確認
        assert not scheduler.is_monitoring()
        assert scheduler.get_last_check_time() is None

        # 監視開始
        with patch.object(scheduler, "check_for_updates", return_value=True):
            result = scheduler.start_monitoring()
            assert result is True
            assert scheduler.is_monitoring()

        # 監視停止
        result = scheduler.stop_monitoring()
        assert result is True
        assert not scheduler.is_monitoring()

    def test_error_recovery(self, real_config):
        """エラー回復の統合テスト"""
        mock_github_client = Mock(spec=GitHubAPIClient)
        mock_wsl_utils = Mock(spec=WSLUtils)
        mock_notification_manager = Mock(spec=NotificationManager)

        scheduler = Scheduler(
            config=real_config,
            github_client=mock_github_client,
            wsl_utils=mock_wsl_utils,
            notification_manager=mock_notification_manager,
        )

        # 最初のチェックでエラーが発生
        mock_github_client.get_latest_stable_release.side_effect = Exception(
            "Network error"
        )

        result = scheduler.check_for_updates()
        assert result is False

        # 次のチェックで成功
        mock_github_client.get_latest_stable_release.side_effect = None
        mock_github_client.get_latest_stable_release.return_value = Mock(
            tag_name="linux-msft-wsl-5.15.90.1",
            name="Test Release",
            published_at=datetime.now(),
            prerelease=False,
            html_url="https://example.com",
        )
        mock_wsl_utils.get_current_kernel_version.return_value = (
            "5.15.89.1-microsoft-standard-WSL2"
        )
        mock_wsl_utils.compare_versions.return_value = 0  # 同じバージョン

        result = scheduler.check_for_updates()
        assert result is True
