"""スケジューリングシステムの実装

このモジュールは、APSchedulerを使用してWSLカーネルの定期チェック機能を提供します。
GitHub API、WSL連携、通知システムを統合した更新チェックロジックを実装します。
"""

from datetime import datetime
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .config import Config
from .github_api import GitHubAPIClient
from .logger import get_logger
from .notification import NotificationManager
from .wsl_utils import WSLUtils


class Scheduler:
    """
    WSLカーネル監視のスケジューリングシステム

    APSchedulerを使用して定期的にGitHub APIをチェックし、
    新しい安定版リリースが見つかった場合に通知を表示します。
    """

    def __init__(
        self,
        config: Config,
        github_client: GitHubAPIClient,
        wsl_utils: WSLUtils,
        notification_manager: NotificationManager,
    ):
        """
        Schedulerを初期化

        Args:
            config: アプリケーション設定
            github_client: GitHub APIクライアント
            wsl_utils: WSLユーティリティ
            notification_manager: 通知マネージャー
        """
        self.config = config
        self.github_client = github_client
        self.wsl_utils = wsl_utils
        self.notification_manager = notification_manager
        self.logger = get_logger()

        # APSchedulerの初期化
        self.scheduler = BackgroundScheduler()
        self.scheduler.configure(timezone="Asia/Tokyo")

        # 監視状態の管理
        self._is_monitoring = False
        self._last_check_time: Optional[datetime] = None
        self._last_known_version: Optional[str] = None

        self.logger.info("スケジューラーを初期化しました")

    def start_monitoring(self) -> bool:
        """
        カーネル監視を開始

        設定されたチェック間隔で定期的に更新チェックを実行します。

        Returns:
            監視開始に成功した場合True
        """
        if self._is_monitoring:
            self.logger.warning("監視は既に開始されています")
            return True

        try:
            # 定期実行ジョブを追加
            trigger = IntervalTrigger(minutes=self.config.check_interval_minutes)
            self.scheduler.add_job(
                func=self.check_for_updates,
                trigger=trigger,
                id="kernel_update_check",
                name="WSLカーネル更新チェック",
                replace_existing=True,
            )

            # スケジューラーを開始
            self.scheduler.start()
            self._is_monitoring = True

            self.logger.info(
                f"カーネル監視を開始しました（チェック間隔: {self.config.check_interval_minutes}分）"
            )

            # 初回チェックを即座に実行
            self.check_for_updates()

            return True

        except Exception as e:
            self.logger.error(f"監視開始中にエラーが発生しました: {e}")
            return False

    def stop_monitoring(self) -> bool:
        """
        カーネル監視を停止

        Returns:
            監視停止に成功した場合True
        """
        if not self._is_monitoring:
            return True

        try:
            # スケジューラーが実行中の場合のみ停止
            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
            self._is_monitoring = False

            self.logger.info("カーネル監視を停止しました")
            return True

        except Exception as e:
            self.logger.error(f"監視停止中にエラーが発生しました: {e}")
            return False

    def check_for_updates(self, force_notify: bool = False) -> bool:
        """
        カーネル更新をチェック

        GitHub APIから最新リリースを取得し、現在のWSLカーネルバージョンと比較します。
        新しいバージョンが見つかった場合は通知を表示します。

        Returns:
            チェックが正常に完了した場合True
        """
        try:
            self.logger.info("カーネル更新チェックを開始します")
            self._last_check_time = datetime.now()
            self.logger.debug(f"チェック開始時刻: {self._last_check_time}")

            # 統合更新チェックロジックを実行
            self.logger.debug("統合更新チェックを実行中...")
            update_info = self._perform_integrated_update_check(force_notify)
            self.logger.debug(f"統合更新チェック結果: {update_info}")

            if not update_info:
                self.logger.warning("統合更新チェックに失敗しました")
                return False

            # 更新チェック結果に基づく処理
            self.logger.debug("更新チェック結果を処理中...")
            result = self._process_update_check_result(update_info)
            self.logger.debug(f"更新チェック処理結果: {result}")
            return result

        except Exception as e:
            self.logger.error(
                f"更新チェック中にエラーが発生しました: {e}", exc_info=True
            )
            self._handle_check_error(e)
            return False

    def _perform_integrated_update_check(
        self, force_notify: bool = False
    ) -> Optional[dict]:
        """
        GitHub API、WSL連携、通知を統合した更新チェック機能

        Returns:
            更新チェック結果の辞書。失敗した場合はNone
        """
        try:
            # Step 1: GitHub APIから最新リリース情報を取得
            self.logger.debug("GitHub APIから最新リリース情報を取得中...")
            latest_release = self.github_client.get_latest_stable_release()

            if not latest_release:
                self.logger.warning("最新リリース情報を取得できませんでした")
                return None

            latest_version = latest_release.tag_name
            self.logger.info(f"最新安定版リリース: {latest_version}")

            # Step 2: WSL環境から現在のカーネルバージョンを取得
            self.logger.debug("WSL環境から現在のカーネルバージョンを取得中...")
            current_version = self.wsl_utils.get_current_kernel_version()

            if not current_version:
                self.logger.warning("現在のWSLカーネルバージョンを取得できませんでした")
                return None

            self.logger.info(f"現在のWSLカーネルバージョン: {current_version}")

            # Step 3: バージョン比較結果に基づく通知判定ロジック
            comparison_result = self._compare_versions_for_notification(
                current_version, latest_version
            )

            # Step 4: 更新チェック結果を構築
            update_info = {
                "current_version": current_version,
                "latest_version": latest_version,
                "latest_release": latest_release,
                "comparison_result": comparison_result,
                "update_available": comparison_result == -1,
                "should_notify": False,
                "check_time": self._last_check_time,
            }

            # Step 5: 通知判定
            if update_info["update_available"]:
                update_info["should_notify"] = force_notify or self._should_notify(
                    latest_version
                )
                self.logger.info(
                    f"新しいカーネルバージョンが利用可能: {current_version} -> {latest_version}"
                )
            elif comparison_result == 0:
                self.logger.info("現在のカーネルは最新版です")
            else:
                self.logger.info(
                    f"現在のカーネルは最新版より新しい: {current_version} > {latest_version}"
                )

            return update_info

        except Exception as e:
            self.logger.error(f"統合更新チェック中にエラーが発生しました: {e}")
            return None

    def _process_update_check_result(self, update_info: dict) -> bool:
        """
        更新チェック結果を処理

        Args:
            update_info: 更新チェック結果の辞書

        Returns:
            処理が正常に完了した場合True
        """
        try:
            # 更新が利用可能で通知が必要な場合
            if update_info["update_available"] and update_info["should_notify"]:
                success = self._execute_notification_logic(update_info)

                if success:
                    self._last_known_version = update_info["latest_version"]
                    self.logger.info("更新通知処理が完了しました")
                    return True
                else:
                    self.logger.error("更新通知処理に失敗しました")
                    # 通知失敗でもチェック自体は成功とみなす
                    return True

            # 更新が利用可能だが通知不要の場合
            elif update_info["update_available"]:
                self.logger.debug("更新は利用可能ですが、通知条件を満たしていません")
                return True

            # 更新が利用可能でない場合
            else:
                self.logger.debug("更新チェック完了: 新しいバージョンはありません")
                return True

        except Exception as e:
            self.logger.error(f"更新チェック結果の処理中にエラーが発生しました: {e}")
            return False

    def _execute_notification_logic(self, update_info: dict) -> bool:
        """
        通知ロジックを実行

        Args:
            update_info: 更新チェック結果の辞書

        Returns:
            通知処理が成功した場合True
        """
        try:
            current_version = update_info["current_version"]
            latest_version = update_info["latest_version"]
            latest_release = update_info["latest_release"]

            # 通知内容の詳細情報を準備
            notification_details = {
                "current_version": current_version,
                "latest_version": latest_version,
                "release_url": latest_release.html_url,
                "published_at": latest_release.published_at,
                "release_name": latest_release.name,
            }

            self.logger.debug(f"通知詳細情報: {notification_details}")

            # 通知を表示
            success = self.notification_manager.show_update_notification(
                current_version, latest_version
            )

            if success:
                self.logger.info(
                    f"更新通知を表示しました: {current_version} -> {latest_version}"
                )

                # 通知クリックハンドラーを設定（まだ設定されていない場合）
                self._ensure_notification_click_handler()

                return True
            else:
                self.logger.error("更新通知の表示に失敗しました")
                return False

        except Exception as e:
            self.logger.error(f"通知ロジック実行中にエラーが発生しました: {e}")
            return False

    def _ensure_notification_click_handler(self) -> None:
        """
        通知クリックハンドラーが設定されていることを確認
        """
        try:
            # 通知クリック時のコールバック関数を定義
            def on_notification_click(
                current_version: str, latest_version: str
            ) -> None:
                self.logger.info(
                    f"通知クリックイベント: {current_version} -> {latest_version}"
                )

                # ビルドアクションが有効な場合の処理は NotificationManager で実行される
                # ここでは追加のログ記録やメトリクス収集などを行う
                self._record_notification_interaction(current_version, latest_version)

            # ハンドラーを登録
            self.notification_manager.register_click_handler(on_notification_click)
            self.logger.debug("通知クリックハンドラーを設定しました")

        except Exception as e:
            self.logger.error(
                f"通知クリックハンドラーの設定中にエラーが発生しました: {e}"
            )

    def _record_notification_interaction(
        self, current_version: str, latest_version: str
    ) -> None:
        """
        通知インタラクションを記録

        Args:
            current_version: 現在のバージョン
            latest_version: 最新のバージョン
        """
        try:
            interaction_info = {
                "timestamp": datetime.now(),
                "current_version": current_version,
                "latest_version": latest_version,
                "action": "notification_clicked",
                "build_action_enabled": self.config.enable_build_action,
            }

            self.logger.info(f"通知インタラクションを記録: {interaction_info}")

            # 将来的にはメトリクス収集システムに送信することも可能

        except Exception as e:
            self.logger.error(f"通知インタラクション記録中にエラーが発生しました: {e}")

    def _compare_versions_for_notification(self, current: str, latest: str) -> int:
        """
        通知用のバージョン比較

        WSLカーネルバージョンとGitHubリリースタグの形式の違いを考慮して比較します。

        Args:
            current: 現在のWSLカーネルバージョン
            latest: 最新のGitHubリリースタグ

        Returns:
            -1: current < latest (更新が利用可能)
             0: current == latest (同じバージョン)
             1: current > latest (現在の方が新しい)
        """
        try:
            # GitHubリリースタグからバージョン番号を抽出
            # 例: "linux-msft-wsl-5.15.90.1" -> "5.15.90.1"
            latest_clean = self._extract_version_from_tag(latest)

            # WSLカーネルバージョンからバージョン番号を抽出
            # 例: "5.15.90.1-microsoft-standard-WSL2" -> "5.15.90.1"
            current_clean = self._extract_version_from_kernel(current)

            self.logger.debug(f"バージョン比較: {current_clean} vs {latest_clean}")

            return self.wsl_utils.compare_versions(current_clean, latest_clean)

        except Exception as e:
            self.logger.error(f"バージョン比較でエラーが発生しました: {e}")
            # エラーの場合は更新なしとして扱う
            return 0

    def _extract_version_from_tag(self, tag: str) -> str:
        """
        GitHubリリースタグからバージョン番号を抽出

        Args:
            tag: GitHubリリースタグ（例: "linux-msft-wsl-5.15.90.1"）

        Returns:
            バージョン番号（例: "5.15.90.1"）
        """
        import re

        # "linux-msft-wsl-" プレフィックスを除去
        if tag.startswith("linux-msft-wsl-"):
            return tag[len("linux-msft-wsl-") :]

        # 数字とドットで構成されるバージョン番号を抽出
        version_match = re.search(r"(\d+(?:\.\d+)+)", tag)
        if version_match:
            return version_match.group(1)

        # フォールバック: タグをそのまま返す
        return tag

    def _extract_version_from_kernel(self, kernel_version: str) -> str:
        """
        WSLカーネルバージョンからバージョン番号を抽出

        Args:
            kernel_version: WSLカーネルバージョン（例: "5.15.90.1-microsoft-standard-WSL2"）

        Returns:
            バージョン番号（例: "5.15.90.1"）
        """
        import re

        # 先頭の数字とドットで構成される部分を抽出
        version_match = re.match(r"^(\d+(?:\.\d+)+)", kernel_version)
        if version_match:
            return version_match.group(1)

        # フォールバック: カーネルバージョンをそのまま返す
        return kernel_version

    def _should_notify(self, latest_version: str) -> bool:
        """
        通知を表示すべきかどうかを判定

        Args:
            latest_version: 最新のバージョン

        Returns:
            通知を表示すべき場合True
        """
        self.logger.debug(f"_should_notifyチェック: latest_version={latest_version}")
        self.logger.debug(f"notification_enabled: {self.config.notification_enabled}")
        self.logger.debug(f"_last_known_version: {self._last_known_version}")

        # 通知が無効の場合は通知しない
        if not self.config.notification_enabled:
            self.logger.debug("通知が無効のため、通知をスキップします")
            return False

        # 同じバージョンについて既に通知済みの場合は通知しない
        if self._last_known_version == latest_version:
            self.logger.debug(f"バージョン {latest_version} については既に通知済みです")
            return False

        self.logger.debug("通知を表示します")
        return True

    def _handle_check_error(self, error: Exception) -> None:
        """
        更新チェックエラーの処理

        Args:
            error: 発生したエラー
        """
        error_message = str(error)

        # エラーの種類に応じた処理
        if "GitHub API" in error_message or "requests" in error_message:
            self.logger.warning(
                "GitHub APIエラーが発生しました。次回チェック時に再試行します"
            )
        elif "WSL" in error_message:
            self.logger.warning("WSLエラーが発生しました。WSL環境を確認してください")
        else:
            self.logger.error(f"予期しないエラーが発生しました: {error}")

        # 必要に応じてエラー通知を表示
        if self.config.notification_enabled:
            try:
                self.notification_manager.show_error_notification(
                    "更新チェックエラー",
                    "カーネル更新チェック中にエラーが発生しました。ログを確認してください。",
                )
            except Exception as e:
                self.logger.error(f"エラー通知の表示に失敗しました: {e}")

    def is_monitoring(self) -> bool:
        """
        監視状態を取得

        Returns:
            監視中の場合True
        """
        return self._is_monitoring

    def get_last_check_time(self) -> Optional[datetime]:
        """
        最後のチェック時刻を取得

        Returns:
            最後のチェック時刻。チェックが実行されていない場合はNone
        """
        return self._last_check_time

    def get_monitoring_status(self) -> dict:
        """
        監視状況の詳細情報を取得

        Returns:
            監視状況を表す辞書
        """
        return {
            "is_monitoring": self._is_monitoring,
            "check_interval_minutes": self.config.check_interval_minutes,
            "last_check_time": self._last_check_time,
            "last_known_version": self._last_known_version,
            "notification_enabled": self.config.notification_enabled,
            "build_action_enabled": self.config.enable_build_action,
        }

    def update_check_interval(self, interval_minutes: int) -> bool:
        """
        チェック間隔を更新

        Args:
            interval_minutes: 新しいチェック間隔（分）

        Returns:
            更新に成功した場合True
        """
        if interval_minutes < 1 or interval_minutes > 1440:
            self.logger.error(
                f"無効なチェック間隔です: {interval_minutes}（1-1440分の範囲で指定してください）"
            )
            return False

        try:
            old_interval = self.config.check_interval_minutes
            self.config.check_interval_minutes = interval_minutes

            # 監視中の場合は再起動
            if self._is_monitoring:
                self.stop_monitoring()
                self.start_monitoring()

            self.logger.info(
                f"チェック間隔を更新しました: {old_interval}分 -> {interval_minutes}分"
            )
            return True

        except Exception as e:
            self.logger.error(f"チェック間隔の更新中にエラーが発生しました: {e}")
            return False
