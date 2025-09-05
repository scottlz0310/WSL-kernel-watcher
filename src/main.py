"""
WSLカーネル安定版リリース監視ツール - メインエントリーポイント

このモジュールはアプリケーションのメインエントリーポイントを提供します。
全コンポーネントを統合したメインアプリケーションを実装します。
要件1.1, 4.1, 5.1に対応。
"""

import signal
import sys
import time
from pathlib import Path
from typing import NoReturn, Optional

from .config import Config, ConfigManager
from .github_api import GitHubAPIClient
from .logger import get_logger
from .notification import NotificationManager
from .scheduler import Scheduler
from .tray import TrayManager
from .wsl_utils import WSLUtils


class WSLKernelWatcherApp:
    """
    WSLカーネル監視アプリケーションのメインクラス

    全コンポーネントを統合し、アプリケーションのライフサイクルを管理します。
    """

    def __init__(self):
        """アプリケーションを初期化"""
        self.logger = get_logger()
        self.config: Optional[Config] = None
        self.config_manager: Optional[ConfigManager] = None
        self.github_client: Optional[GitHubAPIClient] = None
        self.wsl_utils: Optional[WSLUtils] = None
        self.notification_manager: Optional[NotificationManager] = None
        self.tray_manager: Optional[TrayManager] = None
        self.scheduler: Optional[Scheduler] = None
        self._shutdown_requested = False
        self._shutdown_in_progress = False

        # シグナルハンドラーを設定
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def initialize(self) -> bool:
        """
        アプリケーションの初期化

        Returns:
            初期化に成功した場合True
        """
        try:
            self.logger.info("WSLカーネル安定版リリース監視ツールを初期化中...")
            self.logger.info(f"Python バージョン: {sys.version}")
            self.logger.info(f"作業ディレクトリ: {Path.cwd()}")

            # Step 1: 設定管理システムの初期化
            if not self._initialize_config():
                return False

            # Step 2: WSL連携機能の初期化
            if not self._initialize_wsl_utils():
                return False

            # Step 3: GitHub APIクライアントの初期化
            if not self._initialize_github_client():
                return False

            # Step 4: 通知システムの初期化
            if not self._initialize_notification_manager():
                return False

            # Step 5: タスクトレイ管理の初期化（ワンショットモードではスキップ）
            if self.config.execution_mode != "oneshot":
                if not self._initialize_tray_manager():
                    return False

            # Step 6: スケジューリングシステムの初期化
            if not self._initialize_scheduler():
                return False

            self.logger.info("アプリケーションの初期化が完了しました")
            return True

        except Exception as e:
            self.logger.error(
                f"アプリケーション初期化中にエラーが発生しました: {e}", exc_info=True
            )
            return False

    def _initialize_config(self) -> bool:
        """設定管理システムの初期化"""
        try:
            self.logger.debug("設定管理システムを初期化中...")
            self.config_manager = ConfigManager()
            self.config = self.config_manager.load_config()

            # ログレベルを設定に基づいて更新
            import logging

            logging.getLogger().setLevel(
                getattr(logging, self.config.log_level.upper())
            )

            self.logger.info(
                f"設定を読み込みました: チェック間隔={self.config.check_interval_minutes}分"
            )
            return True

        except Exception as e:
            self.logger.error(f"設定管理システムの初期化に失敗しました: {e}")
            return False

    def _initialize_wsl_utils(self) -> bool:
        """WSL連携機能の初期化"""
        try:
            self.logger.debug("WSL連携機能を初期化中...")
            self.wsl_utils = WSLUtils()

            # WSL環境の基本チェック
            current_version = self.wsl_utils.get_current_kernel_version()
            if current_version:
                self.logger.info(
                    f"WSL環境を確認しました: カーネルバージョン={current_version}"
                )
            else:
                self.logger.warning("WSLカーネルバージョンの取得に失敗しました")

            return True

        except Exception as e:
            self.logger.error(f"WSL連携機能の初期化に失敗しました: {e}")
            return False

    def _initialize_github_client(self) -> bool:
        """GitHub APIクライアントの初期化"""
        try:
            self.logger.debug("GitHub APIクライアントを初期化中...")
            self.github_client = GitHubAPIClient(self.config.repository_url)

            # GitHub APIの基本チェック
            latest_release = self.github_client.get_latest_stable_release()
            if latest_release:
                self.logger.info(
                    f"GitHub API接続を確認しました: 最新リリース={latest_release.tag_name}"
                )
            else:
                self.logger.warning("GitHub APIからのリリース情報取得に失敗しました")

            return True

        except Exception as e:
            self.logger.error(f"GitHub APIクライアントの初期化に失敗しました: {e}")
            return False

    def _initialize_notification_manager(self) -> bool:
        """通知システムの初期化"""
        try:
            self.logger.debug("通知システムを初期化中...")
            self.notification_manager = NotificationManager(self.config, self.wsl_utils)

            if self.notification_manager.is_notification_supported():
                self.logger.info("Windows通知システムが利用可能です")
            else:
                self.logger.warning("Windows通知システムが利用できません")

            return True

        except Exception as e:
            self.logger.error(f"通知システムの初期化に失敗しました: {e}")
            return False

    def _initialize_tray_manager(self) -> bool:
        """タスクトレイ管理の初期化"""
        try:
            self.logger.debug("タスクトレイ管理を初期化中...")
            self.tray_manager = TrayManager("WSL Kernel Watcher")

            # コールバックを設定
            self.tray_manager.set_quit_callback(self._quit_from_tray)
            self.tray_manager.set_check_callback(self._manual_check)

            # タスクトレイアイコンを作成
            self.tray_manager.create_tray_icon()

            self.logger.info("タスクトレイアイコンを作成しました")
            return True

        except Exception as e:
            self.logger.error(f"タスクトレイ管理の初期化に失敗しました: {e}")
            return False

    def _initialize_scheduler(self) -> bool:
        """スケジューリングシステムの初期化"""
        try:
            self.logger.debug("スケジューリングシステムを初期化中...")
            self.scheduler = Scheduler(
                self.config,
                self.github_client,
                self.wsl_utils,
                self.notification_manager,
            )

            self.logger.info("スケジューリングシステムを初期化しました")
            return True

        except Exception as e:
            self.logger.error(f"スケジューリングシステムの初期化に失敗しました: {e}")
            return False

    def start(self) -> bool:
        """
        アプリケーションを開始

        Returns:
            開始に成功した場合True
        """
        try:
            self.logger.info("アプリケーションを開始します")

            # スケジューラーによる監視を開始
            if not self.scheduler.start_monitoring():
                self.logger.error("監視の開始に失敗しました")
                return False

            self.logger.info("WSLカーネル監視を開始しました")
            return True

        except Exception as e:
            self.logger.error(f"アプリケーション開始中にエラーが発生しました: {e}")
            return False

    def run(self) -> None:
        """
        アプリケーションのメインループ（常駐モード）

        タスクトレイアイコンが実行中の間、アプリケーションを維持します。
        """
        try:
            self.logger.info("アプリケーションのメインループを開始します")

            # タスクトレイアイコンが実行中の間、アプリケーションを維持
            while not self._shutdown_requested and self.tray_manager.is_running():
                time.sleep(1)

            self.logger.info("メインループを終了します")

        except KeyboardInterrupt:
            self.logger.info("ユーザーによる中断を検出しました")
        except Exception as e:
            self.logger.error(f"メインループ中にエラーが発生しました: {e}")

    def run_oneshot(self) -> None:
        """
        ワンショットモードで実行

        チェックを一度実行して即座に終了します。
        """
        try:
            self.logger.info("ワンショットモードでカーネルチェックを実行します")

            if self.scheduler:
                # ワンショットチェックを実行（常に通知表示）
                result = self.scheduler.check_for_updates(force_notify=True)
                if result:
                    self.logger.info("カーネルチェックが正常に完了しました")
                else:
                    self.logger.warning("カーネルチェックに失敗しました")
            else:
                self.logger.error("スケジューラーが初期化されていません")

            self.logger.info("ワンショットモード完了、アプリケーションを終了します")

        except Exception as e:
            self.logger.error(f"ワンショットモード実行中にエラーが発生しました: {e}")

    def shutdown(self) -> None:
        """
        アプリケーションの終了処理
        """
        if self._shutdown_in_progress:
            return

        try:
            self._shutdown_in_progress = True
            self.logger.info("アプリケーションの終了処理を開始します")
            self._shutdown_requested = True

            # スケジューラーを停止
            if self.scheduler:
                self.scheduler.stop_monitoring()
                self.logger.debug("スケジューラーを停止しました")

            # タスクトレイアイコンを停止
            if self.tray_manager:
                self.tray_manager.stop_icon()
                self.logger.debug("タスクトレイアイコンを停止しました")

            self.logger.info("アプリケーションの終了処理が完了しました")

        except Exception as e:
            self.logger.error(f"終了処理中にエラーが発生しました: {e}")
        finally:
            self._shutdown_in_progress = False

    def _signal_handler(self, signum: int, frame) -> None:
        """
        シグナルハンドラー

        Args:
            signum: シグナル番号
            frame: フレームオブジェクト
        """
        if self._shutdown_in_progress:
            return

        signal_name = signal.Signals(signum).name
        self.logger.info(f"シグナル {signal_name} を受信しました")
        self.shutdown()

    def _quit_from_tray(self) -> None:
        """
        タスクトレイからの終了処理
        """
        if self._shutdown_in_progress:
            return

        self.logger.info("タスクトレイから終了要求を受信しました")
        self._shutdown_requested = True

    def _manual_check(self) -> None:
        """
        手動チェック処理
        """
        try:
            self.logger.info("手動チェックを実行します")
            self.logger.debug(f"schedulerオブジェクト: {self.scheduler}")
            if self.scheduler:
                self.logger.debug("scheduler.check_for_updates()を呼び出し中...")
                result = self.scheduler.check_for_updates(force_notify=True)
                self.logger.debug(f"check_for_updates結果: {result}")
            else:
                self.logger.warning("スケジューラーが初期化されていません")
        except Exception as e:
            self.logger.error(
                f"手動チェック中にエラーが発生しました: {e}", exc_info=True
            )


def main() -> NoReturn:
    """
    アプリケーションのメインエントリーポイント

    全コンポーネントを統合したメインアプリケーションを起動します。
    アプリケーション起動・終了処理と初期化エラーのハンドリングを実装します。
    """
    logger = get_logger()
    app = None

    try:
        logger.info("WSLカーネル安定版リリース監視ツールを開始します")

        # アプリケーションインスタンスを作成
        app = WSLKernelWatcherApp()

        # アプリケーションを初期化
        if not app.initialize():
            logger.error("アプリケーションの初期化に失敗しました")
            sys.exit(1)

        # ワンショットモードの場合はタスクトレイやスケジューラーを開始しない
        if app.config.execution_mode != "oneshot":
            # アプリケーションを開始
            if not app.start():
                logger.error("アプリケーションの開始に失敗しました")
                sys.exit(1)

        # 実行モードに応じて処理を分岐
        if app.config.execution_mode == "oneshot":
            logger.info("ワンショットモードで実行します")
            app.run_oneshot()
        else:
            logger.info("常駐モードで実行します")
            # メインループを実行
            app.run()

    except KeyboardInterrupt:
        logger.info("ユーザーによる中断を検出しました")
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # 終了処理（ワンショットモードではシンプルな終了）
        if app:
            if app.config.execution_mode == "oneshot":
                logger.info("ワンショットモード終了")
            else:
                app.shutdown()
        logger.info("アプリケーションを終了しました")

    sys.exit(0)


if __name__ == "__main__":
    main()
