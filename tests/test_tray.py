"""
TrayManagerクラスのテスト

このモジュールは、TrayManagerクラスの機能をテストします。
"""

import time
from unittest.mock import Mock, patch

import pytest
from PIL import Image

from src.tray import TrayManager


class TestTrayManager:
    """TrayManagerクラスのテストクラス"""

    def setup_method(self) -> None:
        """各テストメソッドの前に実行される初期化処理"""
        self.tray_manager = TrayManager("Test App")

    def teardown_method(self) -> None:
        """各テストメソッドの後に実行される後処理"""
        if self.tray_manager.is_running():
            self.tray_manager.quit_application()
            time.sleep(0.1)  # 終了処理の完了を待機

    def test_init(self) -> None:
        """
        TrayManagerの初期化をテスト

        要件4.1: システムはWindowsタスクトレイにアイコンを表示する
        """
        assert self.tray_manager.app_name == "Test App"
        assert not self.tray_manager.is_running()
        assert self.tray_manager._has_update is False
        assert self.tray_manager._icon is None

    @patch("src.tray.pystray.Icon")
    @patch("src.tray.threading.Thread")
    def test_create_tray_icon(self, mock_thread: Mock, mock_icon_class: Mock) -> None:
        """
        タスクトレイアイコンの作成をテスト

        要件4.1: システムはWindowsタスクトレイにアイコンを表示する
        """
        # モックの設定
        mock_icon = Mock()
        mock_icon_class.return_value = mock_icon
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        # アイコンを作成
        self.tray_manager.create_tray_icon()

        # アイコンが作成されたことを確認
        mock_icon_class.assert_called_once()
        call_args = mock_icon_class.call_args
        assert call_args[1]["name"] == "Test App"
        assert call_args[1]["title"] == "Test App"
        assert isinstance(call_args[1]["icon"], Image.Image)
        assert call_args[1]["menu"] is not None

        # スレッドが開始されたことを確認
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

        assert self.tray_manager._running is True
        assert self.tray_manager._icon == mock_icon

    @patch("src.tray.pystray.Icon")
    def test_create_tray_icon_error(self, mock_icon_class: Mock) -> None:
        """
        タスクトレイアイコン作成時のエラーハンドリングをテスト
        """
        # アイコン作成時にエラーを発生させる
        mock_icon_class.side_effect = Exception("Icon creation failed")

        # エラーが発生することを確認
        with pytest.raises(Exception, match="Icon creation failed"):
            self.tray_manager.create_tray_icon()

    def test_update_icon_state_no_icon(self) -> None:
        """
        アイコンが作成されていない状態での状態更新をテスト

        要件4.4: システムはタスクトレイアイコンの表示を「更新あり」状態に変更する
        """
        # アイコンが作成されていない状態で状態を更新
        self.tray_manager.update_icon_state(True)

        # 内部状態は更新されるが、エラーは発生しない
        assert self.tray_manager._has_update is True

    @patch("src.tray.pystray.Icon")
    def test_update_icon_state_with_icon(self, mock_icon_class: Mock) -> None:
        """
        アイコンが存在する状態での状態更新をテスト

        要件4.4: システムはタスクトレイアイコンの表示を「更新あり」状態に変更する
        """
        # モックアイコンを設定
        mock_icon = Mock()
        self.tray_manager._icon = mock_icon

        # 状態を更新
        self.tray_manager.update_icon_state(True)

        # アイコンとタイトルが更新されたことを確認
        assert mock_icon.icon is not None
        assert mock_icon.title == "Test App - 更新あり"
        assert self.tray_manager._has_update is True

        # 状態を元に戻す
        self.tray_manager.update_icon_state(False)
        assert mock_icon.title == "Test App - 最新"
        assert self.tray_manager._has_update is False

    def test_show_context_menu(self) -> None:
        """
        コンテキストメニュー表示をテスト

        要件4.2: システムはコンテキストメニューを表示する
        """
        # メニュー表示（実際にはpystrayが自動処理するため、ログ出力のみ）
        self.tray_manager.show_context_menu()
        # エラーが発生しないことを確認

    def test_quit_application_no_callback(self) -> None:
        """
        コールバックなしでのアプリケーション終了をテスト

        要件4.3: システムは適切にアプリケーションを終了する
        """
        # モックアイコンを設定
        mock_icon = Mock()
        self.tray_manager._icon = mock_icon
        self.tray_manager._running = True

        # アプリケーションを終了
        self.tray_manager.quit_application()

        # アイコンが停止されたことを確認
        mock_icon.stop.assert_called_once()
        assert self.tray_manager._running is False

    def test_quit_application_with_callback(self) -> None:
        """
        コールバックありでのアプリケーション終了をテスト

        要件4.3: システムは適切にアプリケーションを終了する
        """
        # コールバックを設定
        quit_callback = Mock()
        self.tray_manager.set_quit_callback(quit_callback)

        # モックアイコンを設定
        mock_icon = Mock()
        self.tray_manager._icon = mock_icon
        self.tray_manager._running = True

        # アプリケーションを終了
        self.tray_manager.quit_application()

        # コールバックが呼び出されたことを確認
        quit_callback.assert_called_once()
        mock_icon.stop.assert_called_once()
        assert self.tray_manager._running is False

    def test_set_quit_callback(self) -> None:
        """
        終了コールバックの設定をテスト
        """
        callback = Mock()
        self.tray_manager.set_quit_callback(callback)
        assert self.tray_manager._quit_callback == callback

    def test_set_settings_callback(self) -> None:
        """
        設定コールバックの設定をテスト
        """
        callback = Mock()
        self.tray_manager.set_settings_callback(callback)
        assert self.tray_manager._settings_callback == callback

    def test_is_running_false(self) -> None:
        """
        実行状態の確認（停止中）をテスト
        """
        assert not self.tray_manager.is_running()

    def test_is_running_true(self) -> None:
        """
        実行状態の確認（実行中）をテスト
        """
        # モックアイコンを設定
        mock_icon = Mock()
        self.tray_manager._icon = mock_icon
        self.tray_manager._running = True

        assert self.tray_manager.is_running()

    def test_create_icon_image_normal(self) -> None:
        """
        通常状態のアイコン画像作成をテスト
        """
        image = self.tray_manager._create_icon_image(False)

        assert isinstance(image, Image.Image)
        assert image.size == (32, 32)
        assert image.mode == "RGBA"

    def test_create_icon_image_update_available(self) -> None:
        """
        更新あり状態のアイコン画像作成をテスト

        要件4.4: システムはタスクトレイアイコンの表示を「更新あり」状態に変更する
        """
        image = self.tray_manager._create_icon_image(True)

        assert isinstance(image, Image.Image)
        assert image.size == (32, 32)
        assert image.mode == "RGBA"

    def test_create_menu(self) -> None:
        """
        コンテキストメニューの作成をテスト

        要件4.2: システムはコンテキストメニューを表示する
        """
        menu = self.tray_manager._create_menu()

        # メニューが作成されたことを確認
        assert menu is not None
        # pystray.Menuの詳細な検証は困難なため、作成されたことのみ確認

    @patch("src.tray.pystray.Icon")
    def test_run_icon_success(self, mock_icon_class: Mock) -> None:
        """
        アイコン実行の成功ケースをテスト
        """
        mock_icon = Mock()
        self.tray_manager._icon = mock_icon

        # _run_iconを直接呼び出し
        self.tray_manager._run_icon()

        # アイコンのrunメソッドが呼び出されたことを確認
        mock_icon.run.assert_called_once()

    def test_run_icon_error(self) -> None:
        """
        アイコン実行のエラーケースをテスト
        """
        mock_icon = Mock()
        mock_icon.run.side_effect = Exception("Icon run failed")
        self.tray_manager._icon = mock_icon
        self.tray_manager._running = True

        # _run_iconを直接呼び出し（エラーが発生するが例外は発生しない）
        self.tray_manager._run_icon()

        # 実行状態がFalseになることを確認
        assert self.tray_manager._running is False

    def test_on_settings_clicked_no_callback(self) -> None:
        """
        設定メニュークリック（コールバックなし）をテスト
        """
        mock_icon = Mock()
        mock_item = Mock()

        # コールバックが設定されていない状態でクリック
        self.tray_manager._on_settings_clicked(mock_icon, mock_item)
        # エラーが発生しないことを確認

    def test_on_settings_clicked_with_callback(self) -> None:
        """
        設定メニュークリック（コールバックあり）をテスト
        """
        mock_icon = Mock()
        mock_item = Mock()
        settings_callback = Mock()

        # コールバックを設定
        self.tray_manager.set_settings_callback(settings_callback)

        # メニューをクリック
        self.tray_manager._on_settings_clicked(mock_icon, mock_item)

        # コールバックが呼び出されたことを確認
        settings_callback.assert_called_once()

    def test_on_settings_clicked_callback_error(self) -> None:
        """
        設定メニュークリック時のコールバックエラーをテスト
        """
        mock_icon = Mock()
        mock_item = Mock()
        settings_callback = Mock()
        settings_callback.side_effect = Exception("Callback error")

        # コールバックを設定
        self.tray_manager.set_settings_callback(settings_callback)

        # メニューをクリック（エラーが発生するが例外は発生しない）
        self.tray_manager._on_settings_clicked(mock_icon, mock_item)

        # コールバックが呼び出されたことを確認
        settings_callback.assert_called_once()

    def test_on_check_now_clicked(self) -> None:
        """
        今すぐチェックメニュークリックをテスト
        """
        mock_icon = Mock()
        mock_item = Mock()

        # メニューをクリック
        self.tray_manager._on_check_now_clicked(mock_icon, mock_item)
        # エラーが発生しないことを確認

    @patch.object(TrayManager, "stop_icon")
    def test_on_quit_clicked(self, mock_stop: Mock) -> None:
        """
        終了メニュークリックをテスト

        要件4.3: システムは適切にアプリケーションを終了する
        """
        mock_icon = Mock()
        mock_item = Mock()

        # メニューをクリック
        self.tray_manager._on_quit_clicked(mock_icon, mock_item)

        # stop_iconが呼び出されたことを確認
        mock_stop.assert_called_once()


class TestTrayManagerIntegration:
    """TrayManagerの統合テストクラス"""

    @patch("src.tray.pystray.Icon")
    @patch("src.tray.threading.Thread")
    def test_full_lifecycle(self, mock_thread: Mock, mock_icon_class: Mock) -> None:
        """
        TrayManagerの完全なライフサイクルをテスト

        要件4.1, 4.2, 4.3, 4.4: 全体的な動作確認
        """
        # モックの設定
        mock_icon = Mock()
        mock_icon_class.return_value = mock_icon
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        # TrayManagerを作成
        tray_manager = TrayManager("Integration Test")

        # コールバックを設定
        quit_callback = Mock()
        settings_callback = Mock()
        tray_manager.set_quit_callback(quit_callback)
        tray_manager.set_settings_callback(settings_callback)

        # アイコンを作成
        tray_manager.create_tray_icon()
        assert tray_manager.is_running()

        # 状態を更新
        tray_manager.update_icon_state(True)
        assert tray_manager._has_update is True

        # 状態を元に戻す
        tray_manager.update_icon_state(False)
        assert tray_manager._has_update is False

        # アプリケーションを終了
        tray_manager.quit_application()

        # コールバックが呼び出されたことを確認
        quit_callback.assert_called_once()
        mock_icon.stop.assert_called_once()
        assert not tray_manager.is_running()
