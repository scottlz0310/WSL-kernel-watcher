"""設定管理モジュール - Docker環境対応版"""

import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """アプリケーション設定"""

    repository_url: str = "microsoft/WSL2-Linux-Kernel"
    check_interval_minutes: int = 30
    log_level: str = "INFO"
    github_token: str | None = None


class ConfigManager:
    """設定管理 - 環境変数優先"""

    @staticmethod
    def load() -> Config:
        """設定を環境変数から読み込み"""
        config = Config()

        # 環境変数から設定を読み込み
        config.repository_url = os.getenv("REPOSITORY_URL", config.repository_url)
        config.check_interval_minutes = int(
            os.getenv("CHECK_INTERVAL_MINUTES", config.check_interval_minutes)
        )
        config.log_level = os.getenv("LOG_LEVEL", config.log_level)
        config.github_token = os.getenv("GITHUB_TOKEN")

        logger.info(
            f"設定読み込み完了: {config.repository_url}, 間隔={config.check_interval_minutes}分"
        )

        return config
