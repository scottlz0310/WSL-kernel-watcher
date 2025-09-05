"""
タスクトレイ管理モジュール

このモジュールは、Windowsタスクトレイでのアイコン表示とコンテキストメニュー管理を提供します。
"""

import threading
from typing import Callable, Optional

import pystray
from PIL import Image, ImageDraw

from .logger import get_logger


class TrayManager:
    """
    タスクトレイアイコンとメニューを管理するクラス

    pystrayを使用してWindowsタスクトレイにアイコンを表示し、
    アイコン状態管理とコンテキストメニューを提供します。
    """

    def __init__(self, app_name: str = "WSL Kernel Watcher") -> None:
        """
        TrayManagerを初期化

        Args:
            app_name: アプリケーション名
        """
        self.logger = get_logger()
        self.app_name = app_name
        self._icon: Optional[pystray.Icon] = None
        self._has_update = False
        self._quit_callback: Optional[Callable[[], None]] = None
        self._settings_callback: Optional[Callable[[], None]] = None
        self._check_callback: Optional[Callable[[], None]] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None

        self.logger.info("TrayManager初期化完了")

    def create_tray_icon(self) -> None:
        """
        タスクトレイアイコンを作成して表示

        要件4.1: システムはWindowsタスクトレイにアイコンを表示する
        """
        try:
            # アイコン画像を作成
            icon_image = self._create_icon_image(self._has_update)

            # メニューを作成
            menu = self._create_menu()

            # アイコンを作成
            self._icon = pystray.Icon(
                name=self.app_name, icon=icon_image, title=self.app_name, menu=menu
            )

            # 別スレッドでアイコンを実行
            self._running = True
            self._thread = threading.Thread(target=self._run_icon, daemon=True)
            self._thread.start()

            self.logger.info("タスクトレイアイコンを作成しました")

        except Exception as e:
            self.logger.error(f"タスクトレイアイコンの作成に失敗しました: {e}")
            raise

    def update_icon_state(self, has_update: bool) -> None:
        """
        アイコンの状態を更新

        Args:
            has_update: 更新が利用可能かどうか

        要件4.4: システムはタスクトレイアイコンの表示を「更新あり」状態に変更する
        """
        try:
            if self._has_update != has_update:
                self._has_update = has_update

                if self._icon is not None:
                    # アイコン画像を更新
                    new_icon = self._create_icon_image(has_update)
                    self._icon.icon = new_icon

                    # タイトルも更新
                    status = "更新あり" if has_update else "最新"
                    self._icon.title = f"{self.app_name} - {status}"

                    self.logger.info(
                        f"アイコン状態を更新しました: has_update={has_update}"
                    )

        except Exception as e:
            self.logger.error(f"アイコン状態の更新に失敗しました: {e}")

    def show_context_menu(self) -> None:
        """
        コンテキストメニューを表示

        要件4.2: システムはコンテキストメニューを表示する
        注意: pystrayでは右クリック時に自動的にメニューが表示されるため、
        この関数は主にテスト用途で使用されます。
        """
        self.logger.debug("コンテキストメニュー表示要求")

    def quit_application(self) -> None:
        """
        アプリケーションを終了

        要件4.3: システムは適切にアプリケーションを終了する
        """
        try:
            self.logger.info("アプリケーション終了処理を開始")

            # 終了コールバックを実行
            if self._quit_callback:
                self._quit_callback()

            self.stop_icon()
            self.logger.info("アプリケーション終了処理完了")

        except Exception as e:
            self.logger.error(f"アプリケーション終了処理でエラーが発生しました: {e}")

    def stop_icon(self) -> None:
        """
        アイコンを停止
        """
        try:
            # アイコンを停止
            if self._icon is not None:
                self._icon.stop()

            self._running = False

            # スレッドの終了を待機
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=5.0)

        except Exception as e:
            self.logger.error(f"アイコン停止処理でエラーが発生しました: {e}")

    def set_quit_callback(self, callback: Callable[[], None]) -> None:
        """
        終了時のコールバック関数を設定

        Args:
            callback: 終了時に呼び出される関数
        """
        self._quit_callback = callback
        self.logger.debug("終了コールバックを設定しました")

    def set_settings_callback(self, callback: Callable[[], None]) -> None:
        """
        設定表示時のコールバック関数を設定

        Args:
            callback: 設定表示時に呼び出される関数
        """
        self._settings_callback = callback
        self.logger.debug("設定コールバックを設定しました")

    def set_check_callback(self, callback: Callable[[], None]) -> None:
        """
        今すぐチェック時のコールバック関数を設定

        Args:
            callback: 今すぐチェック時に呼び出される関数
        """
        self._check_callback = callback
        self.logger.debug("チェックコールバックを設定しました")

    def is_running(self) -> bool:
        """
        タスクトレイアイコンが実行中かどうかを確認

        Returns:
            実行中の場合True
        """
        return self._running and self._icon is not None

    def _create_icon_image(self, has_update: bool) -> Image.Image:
        """
        アイコン画像を作成

        Args:
            has_update: 更新が利用可能かどうか

        Returns:
            PIL Image オブジェクト
        """
        # 32x32のアイコンを作成
        size = (32, 32)
        image = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        if has_update:
            # 更新ありの場合は赤い円
            draw.ellipse(
                [4, 4, 28, 28], fill=(255, 0, 0, 255), outline=(128, 0, 0, 255)
            )
            # 感嘆符を描画
            draw.text((13, 8), "!", fill=(255, 255, 255, 255))
        else:
            # 通常時は青い円
            draw.ellipse(
                [4, 4, 28, 28], fill=(0, 100, 200, 255), outline=(0, 50, 100, 255)
            )
            # チェックマークを描画
            draw.text((11, 8), "✓", fill=(255, 255, 255, 255))

        return image

    def _create_menu(self) -> pystray.Menu:
        """
        コンテキストメニューを作成

        Returns:
            pystray.Menu オブジェクト
        """
        menu_items = [
            pystray.MenuItem(
                "設定",
                self._on_settings_clicked,
                enabled=self._settings_callback is not None,
            ),
            pystray.MenuItem("今すぐチェック", self._on_check_now_clicked),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("終了", self._on_quit_clicked),
        ]

        return pystray.Menu(*menu_items)

    def _run_icon(self) -> None:
        """
        アイコンを実行（別スレッドで実行される）
        """
        try:
            if self._icon:
                self._icon.run()
        except Exception as e:
            self.logger.error(f"タスクトレイアイコンの実行でエラーが発生しました: {e}")
        finally:
            self._running = False

    def _on_settings_clicked(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """
        設定メニューがクリックされた時の処理
        """
        self.logger.info("設定メニューがクリックされました")
        if self._settings_callback:
            try:
                self._settings_callback()
            except Exception as e:
                self.logger.error(f"設定コールバックの実行でエラーが発生しました: {e}")

    def _on_check_now_clicked(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """
        今すぐチェックメニューがクリックされた時の処理
        """
        self.logger.info("今すぐチェックメニューがクリックされました")
        # チェックコールバックを実行
        if self._check_callback:
            try:
                self._check_callback()
            except Exception as e:
                self.logger.error(
                    f"チェックコールバックの実行でエラーが発生しました: {e}"
                )

    def _on_quit_clicked(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """
        終了メニューがクリックされた時の処理
        """
        self.logger.info("終了メニューがクリックされました")
        # コールバックを呼び出してアプリケーション全体の終了を開始
        if self._quit_callback:
            self._quit_callback()
        # アイコンだけを停止
        self.stop_icon()
