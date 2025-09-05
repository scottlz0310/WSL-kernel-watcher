"""
通知システムの単体テスト

NotificationManagerクラスの機能をテストします。
"""

from unittest.mock import Mock, patch

import pytest

from src.config import Config
from src.notification import NotificationContent, NotificationManager
from src.wsl_utils import WSLUtils


@pytest.fixture
def mock_config():
    """テスト用の設定オブジェクト"""
    config = Mock(spec=Config)
    config.notification_enabled = True
    config.enable_build_action = False
    return config


@pytest.fixture
def mock_wsl_utils():
    """テスト用のWSLUtilsオブジェクト"""
    wsl_utils = Mock(spec=WSLUtils)
    wsl_utils.execute_build_script.return_value = True
    return wsl_utils


@pytest.fixture
def mock_windows_toaster():
    """テスト用のWindowsToasterモック"""
    with patch("src.notification.WindowsToaster") as mock_toaster_class:
        mock_toaster = Mock()
        mock_toaster_class.return_value = mock_toaster
        yield mock_toaster


@pytest.fixture
def mock_toast():
    """テスト用のToastモック"""
    with patch("src.notification.Toast") as mock_toast_class:
        mock_toast = Mock()
        mock_toast_class.return_value = mock_toast
        yield mock_toast


class TestNotificationContent:
    """NotificationContentクラスのテスト"""

    def test_notification_content_creation(self):
        """NotificationContentの作成テスト"""
        content = NotificationContent(
            current_version="5.15.90.1", latest_version="5.15.91.1"
        )

        assert content.current_version == "5.15.90.1"
        assert content.latest_version == "5.15.91.1"
        assert content.title == "WSLカーネル更新通知"
        assert "現在: {current}" in content.message_template
        assert "最新: {latest}" in content.message_template

    def test_notification_content_custom_values(self):
        """カスタム値でのNotificationContent作成テスト"""
        content = NotificationContent(
            current_version="5.15.90.1",
            latest_version="5.15.91.1",
            title="カスタムタイトル",
            message_template="カスタムメッセージ: {current} -> {latest}",
        )

        assert content.title == "カスタムタイトル"
        assert content.message_template == "カスタムメッセージ: {current} -> {latest}"


class TestNotificationManager:
    """NotificationManagerクラスのテスト"""

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_init_with_windows_toasts_available(
        self, mock_config, mock_windows_toaster
    ):
        """Windows-Toastsが利用可能な場合の初期化テスト"""
        manager = NotificationManager(mock_config)

        assert manager.config == mock_config
        assert manager._is_supported is True
        assert manager.toaster is not None

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", False)
    def test_init_without_windows_toasts(self, mock_config):
        """Windows-Toastsが利用できない場合の初期化テスト"""
        manager = NotificationManager(mock_config)

        assert manager.config == mock_config
        assert manager._is_supported is False
        assert manager.toaster is None

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_init_with_windows_toasts_error(self, mock_config):
        """Windows-Toasts初期化エラーのテスト"""
        with patch(
            "src.notification.WindowsToaster", side_effect=Exception("初期化エラー")
        ):
            manager = NotificationManager(mock_config)

            assert manager._is_supported is False
            assert manager.toaster is None

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_is_notification_supported_enabled(self, mock_config, mock_windows_toaster):
        """通知機能サポート確認テスト（有効）"""
        mock_config.notification_enabled = True
        manager = NotificationManager(mock_config)

        assert manager.is_notification_supported() is True

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_is_notification_supported_disabled(
        self, mock_config, mock_windows_toaster
    ):
        """通知機能サポート確認テスト（無効）"""
        mock_config.notification_enabled = False
        manager = NotificationManager(mock_config)

        assert manager.is_notification_supported() is False

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", False)
    def test_is_notification_supported_not_available(self, mock_config):
        """通知機能サポート確認テスト（利用不可）"""
        manager = NotificationManager(mock_config)

        assert manager.is_notification_supported() is False

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_show_update_notification_success(
        self, mock_config, mock_windows_toaster, mock_toast
    ):
        """更新通知表示成功テスト"""
        mock_config.notification_enabled = True
        manager = NotificationManager(mock_config)

        result = manager.show_update_notification("5.15.90.1", "5.15.91.1")

        assert result is True
        mock_windows_toaster.show_toast.assert_called_once()
        assert mock_toast.text_fields[0] == "WSLカーネル更新通知"
        assert "5.15.90.1" in mock_toast.text_fields[1]
        assert "5.15.91.1" in mock_toast.text_fields[1]

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_show_update_notification_not_supported(
        self, mock_config, mock_windows_toaster
    ):
        """通知機能が無効な場合のテスト"""
        mock_config.notification_enabled = False
        manager = NotificationManager(mock_config)

        result = manager.show_update_notification("5.15.90.1", "5.15.91.1")

        assert result is False
        mock_windows_toaster.show_toast.assert_not_called()

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_show_update_notification_error(
        self, mock_config, mock_windows_toaster, mock_toast
    ):
        """通知表示エラーテスト"""
        mock_config.notification_enabled = True
        mock_windows_toaster.show_toast.side_effect = Exception("通知エラー")
        manager = NotificationManager(mock_config)

        result = manager.show_update_notification("5.15.90.1", "5.15.91.1")

        assert result is False

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_register_click_handler(self, mock_config, mock_windows_toaster):
        """クリックハンドラー登録テスト"""
        manager = NotificationManager(mock_config)
        callback = Mock()

        manager.register_click_handler(callback)

        assert manager._click_callback == callback

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_notification_click_without_build_action(
        self, mock_config, mock_windows_toaster
    ):
        """ビルドアクション無効時の通知クリックテスト"""
        mock_config.enable_build_action = False
        manager = NotificationManager(mock_config)
        callback = Mock()
        manager.register_click_handler(callback)

        manager._handle_notification_click("5.15.90.1", "5.15.91.1")

        callback.assert_called_once_with("5.15.90.1", "5.15.91.1")

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_notification_click_with_build_action_success(
        self, mock_config, mock_wsl_utils, mock_windows_toaster
    ):
        """ビルドアクション有効時の通知クリック成功テスト"""
        mock_config.enable_build_action = True
        mock_config.notification_enabled = True
        mock_wsl_utils.execute_build_script.return_value = True

        manager = NotificationManager(mock_config, mock_wsl_utils)

        with patch.object(manager, "show_info_notification") as mock_show_info:
            manager._handle_notification_click("5.15.90.1", "5.15.91.1")

            mock_wsl_utils.execute_build_script.assert_called_once()
            assert mock_show_info.call_count == 2  # 開始と完了の通知

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_notification_click_with_build_action_failure(
        self, mock_config, mock_wsl_utils, mock_windows_toaster
    ):
        """ビルドアクション失敗時の通知クリックテスト"""
        mock_config.enable_build_action = True
        mock_config.notification_enabled = True
        mock_wsl_utils.execute_build_script.return_value = False

        manager = NotificationManager(mock_config, mock_wsl_utils)

        with patch.object(manager, "show_error_notification") as mock_show_error:
            manager._handle_notification_click("5.15.90.1", "5.15.91.1")

            mock_wsl_utils.execute_build_script.assert_called_once()
            mock_show_error.assert_called_once()

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_notification_click_without_wsl_utils(
        self, mock_config, mock_windows_toaster
    ):
        """WSLUtilsが無い場合のビルドアクションテスト"""
        mock_config.enable_build_action = True
        mock_config.notification_enabled = True

        manager = NotificationManager(mock_config, None)

        with patch.object(manager, "show_error_notification") as mock_show_error:
            manager._handle_notification_click("5.15.90.1", "5.15.91.1")

            mock_show_error.assert_called_once()

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_notification_click_callback_error(self, mock_config, mock_windows_toaster):
        """コールバック実行エラーテスト"""
        mock_config.enable_build_action = False
        manager = NotificationManager(mock_config)

        callback = Mock(side_effect=Exception("コールバックエラー"))
        manager.register_click_handler(callback)

        # エラーが発生してもクラッシュしないことを確認
        manager._handle_notification_click("5.15.90.1", "5.15.91.1")

        callback.assert_called_once()

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_show_info_notification(
        self, mock_config, mock_windows_toaster, mock_toast
    ):
        """情報通知表示テスト"""
        mock_config.notification_enabled = True
        manager = NotificationManager(mock_config)

        result = manager.show_info_notification("テストタイトル", "テストメッセージ")

        assert result is True
        mock_windows_toaster.show_toast.assert_called_once()
        assert mock_toast.text_fields == ["テストタイトル", "テストメッセージ"]

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_show_error_notification(
        self, mock_config, mock_windows_toaster, mock_toast
    ):
        """エラー通知表示テスト"""
        mock_config.notification_enabled = True
        manager = NotificationManager(mock_config)

        result = manager.show_error_notification("エラータイトル", "エラーメッセージ")

        assert result is True
        mock_windows_toaster.show_toast.assert_called_once()
        assert mock_toast.text_fields == ["エラータイトル", "エラーメッセージ"]

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_set_build_action_enabled(self, mock_config, mock_windows_toaster):
        """ビルドアクション有効/無効設定テスト"""
        manager = NotificationManager(mock_config)

        manager.set_build_action_enabled(True)
        assert mock_config.enable_build_action is True

        manager.set_build_action_enabled(False)
        assert mock_config.enable_build_action is False

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_is_build_action_enabled(self, mock_config, mock_windows_toaster):
        """ビルドアクション有効確認テスト"""
        mock_config.enable_build_action = True
        manager = NotificationManager(mock_config)

        assert manager.is_build_action_enabled() is True

        mock_config.enable_build_action = False
        assert manager.is_build_action_enabled() is False


class TestNotificationManagerIntegration:
    """NotificationManagerの統合テスト"""

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_full_notification_flow_with_click(
        self, mock_config, mock_wsl_utils, mock_windows_toaster, mock_toast
    ):
        """通知表示からクリック処理までの完全なフローテスト"""
        mock_config.notification_enabled = True
        mock_config.enable_build_action = True
        mock_wsl_utils.execute_build_script.return_value = True

        manager = NotificationManager(mock_config, mock_wsl_utils)
        callback = Mock()
        manager.register_click_handler(callback)

        # 通知表示
        result = manager.show_update_notification("5.15.90.1", "5.15.91.1")
        assert result is True

        # 通知クリックをシミュレート
        with patch.object(manager, "show_info_notification") as mock_show_info:
            manager._handle_notification_click("5.15.90.1", "5.15.91.1")

            # ビルドアクションが実行されることを確認
            mock_wsl_utils.execute_build_script.assert_called_once()
            # コールバックが呼ばれることを確認
            callback.assert_called_once_with("5.15.90.1", "5.15.91.1")
            # 情報通知が表示されることを確認
            assert mock_show_info.call_count == 2

    @patch("src.notification.WINDOWS_TOASTS_AVAILABLE", True)
    def test_windows_compatibility_check(self, mock_config, mock_windows_toaster):
        """Windows対応確認テスト"""
        with patch("src.notification.WindowsToaster") as mock_toaster_class:
            mock_toaster_class.return_value = mock_windows_toaster
            manager = NotificationManager(mock_config)

            # Windows-Toastsが正常に初期化されることを確認
            assert manager.toaster is not None
            assert manager._is_supported is True

            # Windows 10/11対応の確認（WindowsToasterが正常に作成されることで確認）
            mock_toaster_class.assert_called_once_with("WSL Kernel Watcher")
