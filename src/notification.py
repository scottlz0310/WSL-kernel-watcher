"""
Windows通知システムの実装

このモジュールは、Windows-Toastsライブラリを使用してWindowsトースト通知を表示し、
通知クリック時のコールバック処理を管理します。
"""

from dataclasses import dataclass
from typing import Any, Callable, Optional

try:
    from windows_toasts import Toast, ToastDisplayImage, WindowsToaster

    WINDOWS_TOASTS_AVAILABLE = True
except ImportError:
    WINDOWS_TOASTS_AVAILABLE = False
    # テスト環境やWindows以外の環境での動作を考慮
    WindowsToaster = None  # type: ignore
    Toast = None  # type: ignore
    ToastDisplayImage = None  # type: ignore

from .config import Config
from .logger import get_logger
from .wsl_utils import WSLUtils


@dataclass
class NotificationContent:
    """通知内容を表すデータクラス"""

    current_version: str
    latest_version: str
    title: str = "WSLカーネル更新通知"
    message_template: str = (
        "新しいWSLカーネルが利用可能です\n現在: {current}\n最新: {latest}"
    )


class NotificationManager:
    """
    Windows通知システムを管理するクラス

    Windows-Toastsライブラリを使用してトースト通知を表示し、
    通知クリック時のコールバック処理を管理します。
    """

    def __init__(self, config: Config, wsl_utils: Optional[WSLUtils] = None) -> None:
        """
        NotificationManagerを初期化

        Args:
            config: アプリケーション設定
            wsl_utils: WSLユーティリティ（ビルドアクション用）
        """
        self.config = config
        self.wsl_utils = wsl_utils
        self.logger = get_logger()
        self._click_callback: Optional[Callable[[str, str], None]] = None
        self.toaster: Optional[Any] = None  # WindowsToasterまたはNone

        # Windows-Toastsの初期化
        if WINDOWS_TOASTS_AVAILABLE and WindowsToaster is not None:
            try:
                self.toaster = WindowsToaster("WSL Kernel Watcher")
                self._is_supported = True
                self.logger.info("Windows通知システムを初期化しました")
            except Exception as e:
                self.logger.error(f"Windows通知システムの初期化に失敗しました: {e}")
                self.toaster = None
                self._is_supported = False
        else:
            self.logger.warning("Windows-Toastsライブラリが利用できません")
            self.toaster = None
            self._is_supported = False

    def is_notification_supported(self) -> bool:
        """
        通知機能がサポートされているかを確認

        Returns:
            通知機能が利用可能な場合True
        """
        return self._is_supported and self.config.notification_enabled

    def show_update_notification(
        self, current_version: str, latest_version: str
    ) -> bool:
        """
        カーネル更新通知を表示

        Args:
            current_version: 現在のカーネルバージョン
            latest_version: 最新のカーネルバージョン

        Returns:
            通知表示に成功した場合True
        """
        self.logger.debug(
            f"show_update_notification呼び出し: {current_version} -> {latest_version}"
        )
        self.logger.debug(
            f"is_notification_supported: {self.is_notification_supported()}"
        )
        self.logger.debug(f"toaster: {self.toaster}")

        if not self.is_notification_supported():
            self.logger.warning("通知機能が無効または利用できません")
            return False

        if not self.toaster:
            self.logger.error("Windows通知システムが初期化されていません")
            return False

        try:
            # 通知内容を作成
            content = NotificationContent(
                current_version=current_version, latest_version=latest_version
            )

            message = content.message_template.format(
                current=current_version, latest=latest_version
            )

            # トースト通知を作成
            toast = Toast()
            toast.text_fields = [content.title, message]

            # 通知クリック時のコールバックを設定
            if self._click_callback:
                toast.on_activated = lambda _: self._handle_notification_click(
                    current_version, latest_version
                )

            # 通知を表示
            self.toaster.show_toast(toast)

            self.logger.info(
                f"更新通知を表示しました: {current_version} -> {latest_version}"
            )
            return True

        except Exception as e:
            self.logger.error(f"通知表示中にエラーが発生しました: {e}")
            return False

    def register_click_handler(self, callback: Callable[[str, str], None]) -> None:
        """
        通知クリック時のコールバック関数を登録

        Args:
            callback: 通知クリック時に呼び出される関数
                     引数: (current_version, latest_version)
        """
        self._click_callback = callback
        self.logger.debug("通知クリックハンドラーを登録しました")

    def set_build_action_enabled(self, enabled: bool) -> None:
        """
        ビルドアクションの有効/無効を設定

        Args:
            enabled: ビルドアクションを有効にする場合True
        """
        self.config.enable_build_action = enabled
        status = "有効" if enabled else "無効"
        self.logger.info(f"ビルドアクションを{status}に設定しました")

    def is_build_action_enabled(self) -> bool:
        """
        ビルドアクションが有効かどうかを確認

        Returns:
            ビルドアクションが有効な場合True
        """
        return self.config.enable_build_action

    def _handle_notification_click(
        self, current_version: str, latest_version: str
    ) -> None:
        """
        通知クリック時の内部処理

        Args:
            current_version: 現在のカーネルバージョン
            latest_version: 最新のカーネルバージョン
        """
        self.logger.info(
            f"通知がクリックされました: {current_version} -> {latest_version}"
        )

        # 設定に基づくアクション実行
        if self.config.enable_build_action:
            self._execute_build_action(current_version, latest_version)
        else:
            self.logger.info("ビルドアクションが無効のため、何も実行しません")

        # 外部コールバックがある場合は実行
        if self._click_callback:
            try:
                self._click_callback(current_version, latest_version)
            except Exception as e:
                self.logger.error(f"通知クリックハンドラーでエラーが発生しました: {e}")

    def _execute_build_action(self, current_version: str, latest_version: str) -> None:
        """
        ビルドアクションを実行

        Args:
            current_version: 現在のカーネルバージョン
            latest_version: 最新のカーネルバージョン
        """
        if not self.wsl_utils:
            self.logger.error(
                "WSLUtilsが初期化されていないため、ビルドアクションを実行できません"
            )
            self.show_error_notification("ビルドエラー", "WSL環境が利用できません")
            return

        self.logger.info(f"ビルドアクションを開始します: {latest_version}")

        # 情報通知を表示
        self.show_info_notification(
            "カーネルビルド開始",
            f"WSLカーネル {latest_version} のビルドを開始します...",
        )

        try:
            # ビルドスクリプトを実行
            success = self.wsl_utils.execute_build_script()

            if success:
                self.show_info_notification(
                    "ビルド完了", f"WSLカーネル {latest_version} のビルドが完了しました"
                )
                self.logger.info("ビルドアクションが正常に完了しました")
            else:
                self.show_error_notification(
                    "ビルドエラー",
                    "カーネルビルドに失敗しました。ログを確認してください。",
                )
                self.logger.error("ビルドアクションが失敗しました")

        except Exception as e:
            error_msg = f"ビルドアクション実行中にエラーが発生しました: {e}"
            self.logger.error(error_msg)
            self.show_error_notification(
                "ビルドエラー", "予期しないエラーが発生しました"
            )

    def show_info_notification(self, title: str, message: str) -> bool:
        """
        一般的な情報通知を表示

        Args:
            title: 通知のタイトル
            message: 通知のメッセージ

        Returns:
            通知表示に成功した場合True
        """
        if not self.is_notification_supported():
            self.logger.warning("通知機能が無効または利用できません")
            return False

        if not self.toaster:
            self.logger.error("Windows通知システムが初期化されていません")
            return False

        try:
            toast = Toast()
            toast.text_fields = [title, message]

            self.toaster.show_toast(toast)

            self.logger.info(f"情報通知を表示しました: {title}")
            return True

        except Exception as e:
            self.logger.error(f"情報通知表示中にエラーが発生しました: {e}")
            return False

    def show_error_notification(self, title: str, message: str) -> bool:
        """
        エラー通知を表示

        Args:
            title: 通知のタイトル
            message: エラーメッセージ

        Returns:
            通知表示に成功した場合True
        """
        if not self.is_notification_supported():
            self.logger.warning("通知機能が無効または利用できません")
            return False

        if not self.toaster:
            self.logger.error("Windows通知システムが初期化されていません")
            return False

        try:
            toast = Toast()
            toast.text_fields = [title, message]

            self.toaster.show_toast(toast)

            self.logger.warning(f"エラー通知を表示しました: {title}")
            return True

        except Exception as e:
            self.logger.error(f"エラー通知表示中にエラーが発生しました: {e}")
            return False
