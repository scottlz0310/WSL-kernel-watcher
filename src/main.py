"""WSL Kernel Watcher v2 メインアプリケーション"""

import asyncio
import logging
import sys
from typing import Optional

from .config import ConfigManager
from .docker_notifier import DockerNotifier
from .github_watcher import GitHubWatcher


def setup_logging(log_level: str) -> None:
    """ログ設定"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


class WSLKernelWatcher:
    """WSLカーネル監視アプリケーション"""

    def __init__(self) -> None:
        self.config = ConfigManager.load()
        self.github_watcher = GitHubWatcher(self.config.repository_url)
        self.notifier = DockerNotifier()
        self.current_version: Optional[str] = None

        setup_logging(self.config.log_level)
        self.logger = logging.getLogger(__name__)

    async def run(self) -> None:
        """メイン実行ループ"""
        self.logger.info("WSL Kernel Watcher v2.1.0 開始")

        while True:
            try:
                await self.check_for_updates()
                await asyncio.sleep(self.config.check_interval_minutes * 60)
            except KeyboardInterrupt:
                self.logger.info("アプリケーション終了")
                break
            except Exception as e:
                self.logger.error(f"予期しないエラー: {e}")
                await asyncio.sleep(60)  # エラー時は1分待機

    async def check_for_updates(self) -> None:
        """更新チェック"""
        try:
            release = self.github_watcher.get_latest_stable_release()

            if not release:
                self.logger.warning("リリース情報を取得できませんでした")
                return

            latest_version = release.tag_name

            if self.current_version is None:
                self.current_version = latest_version
                self.logger.info(f"初期バージョン設定: {latest_version}")
                return

            if latest_version != self.current_version:
                self.logger.info(
                    f"新しいバージョン発見: {self.current_version} -> {latest_version}"
                )

                success = self.notifier.notify_kernel_update(
                    latest_version, self.current_version
                )

                if success:
                    self.current_version = latest_version
                    self.logger.info("通知送信完了")
                else:
                    self.logger.error("通知送信失敗")
            else:
                self.logger.debug(f"バージョン変更なし: {latest_version}")

        except Exception as e:
            self.logger.error(f"更新チェックエラー: {e}")


async def main() -> None:
    """エントリーポイント"""
    watcher = WSLKernelWatcher()
    await watcher.run()


if __name__ == "__main__":
    asyncio.run(main())
