"""設定管理モジュール

WSLカーネル監視ツールの設定ファイル（config.toml）の読み込み、
検証、デフォルト値管理を行うモジュール。
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import tomllib

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """アプリケーション設定を格納するデータクラス

    Attributes:
        check_interval_minutes: GitHub APIのチェック間隔（分）
        repository_url: 監視対象のGitHubリポジトリ
        enable_build_action: 通知クリック時のビルドアクション有効化
        notification_enabled: トースト通知の有効化
        log_level: ログレベル（DEBUG, INFO, WARNING, ERROR）
    """

    check_interval_minutes: int = 30
    repository_url: str = "microsoft/WSL2-Linux-Kernel"
    enable_build_action: bool = False
    notification_enabled: bool = True
    log_level: str = "INFO"


class ConfigManager:
    """設定ファイル管理クラス

    config.tomlファイルの読み込み、作成、検証を行う。
    設定ファイルが存在しない場合はデフォルト設定で作成する。
    """

    def __init__(self, config_path: Optional[Path] = None):
        """ConfigManagerを初期化

        Args:
            config_path: 設定ファイルのパス。Noneの場合はカレントディレクトリのconfig.tomlを使用
        """
        self.config_path = config_path or Path("config.toml")

    def load_config(self) -> Config:
        """設定ファイルを読み込んでConfigオブジェクトを返す

        設定ファイルが存在しない場合はデフォルト設定で作成する。
        設定ファイルの形式が不正な場合はエラーログを出力してデフォルト設定を返す。

        Returns:
            Config: 設定オブジェクト
        """
        if not self.config_path.exists():
            logger.info(
                f"設定ファイル {self.config_path} が存在しません。デフォルト設定で作成します。"
            )
            self.create_default_config()
            return Config()

        try:
            with open(self.config_path, "rb") as f:
                config_data = tomllib.load(f)

            # 設定値を検証してConfigオブジェクトを作成
            config = self._create_config_from_dict(config_data)

            if not self.validate_config(config):
                logger.warning(
                    "設定ファイルの検証に失敗しました。デフォルト設定を使用します。"
                )
                return Config()

            logger.info(f"設定ファイル {self.config_path} を正常に読み込みました。")
            return config

        except toml.TomlDecodeError as e:
            logger.error(f"設定ファイルの形式が不正です: {e}")
            logger.info("デフォルト設定で動作を継続します。")
            return Config()
        except Exception as e:
            logger.error(f"設定ファイルの読み込み中にエラーが発生しました: {e}")
            logger.info("デフォルト設定で動作を継続します。")
            return Config()

    def create_default_config(self) -> None:
        """デフォルト設定でconfig.tomlファイルを作成

        Raises:
            OSError: ファイル作成に失敗した場合
        """
        default_config = Config()
        config_dict = {
            "check_interval_minutes": default_config.check_interval_minutes,
            "repository_url": default_config.repository_url,
            "enable_build_action": default_config.enable_build_action,
            "notification_enabled": default_config.notification_enabled,
            "log_level": default_config.log_level,
        }

        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                self._write_toml_config(f, config_dict)
            logger.info(f"デフォルト設定ファイル {self.config_path} を作成しました。")
        except Exception as e:
            logger.error(f"設定ファイルの作成に失敗しました: {e}")
            raise

    def _write_toml_config(self, file, config_dict: dict) -> None:
        """TOML形式で設定を書き込む"""
        file.write("# WSL Kernel Watcher 設定ファイル\n")
        file.write("# このファイルはアプリケーションの動作を制御します\n\n")
        
        for key, value in config_dict.items():
            if isinstance(value, str):
                file.write(f'{key} = "{value}"\n')
            elif isinstance(value, bool):
                file.write(f'{key} = {str(value).lower()}\n')
            elif isinstance(value, (int, float)):
                file.write(f'{key} = {value}\n')
            else:
                file.write(f'{key} = "{str(value)}"\n')

    def validate_config(self, config: Config) -> bool:
        """設定値の妥当性を検証

        Args:
            config: 検証対象の設定オブジェクト

        Returns:
            bool: 設定が妥当な場合True、そうでなければFalse
        """
        # チェック間隔の検証（1分以上、1440分（24時間）以下）
        if (
            not isinstance(config.check_interval_minutes, int)
            or config.check_interval_minutes < 1
            or config.check_interval_minutes > 1440
        ):
            logger.error(
                f"チェック間隔が不正です: {config.check_interval_minutes}（1-1440分の範囲で指定してください）"
            )
            return False

        # リポジトリURLの検証（基本的な形式チェック）
        if (
            not isinstance(config.repository_url, str)
            or not config.repository_url.strip()
        ):
            logger.error(f"リポジトリURLが不正です: {config.repository_url}")
            return False

        # リポジトリURLの形式チェック（owner/repo形式）
        if "/" not in config.repository_url or config.repository_url.count("/") != 1:
            logger.error(
                f"リポジトリURLの形式が不正です: {config.repository_url}（owner/repo形式で指定してください）"
            )
            return False

        # ブール値の検証
        if not isinstance(config.enable_build_action, bool):
            logger.error(
                f"enable_build_actionの値が不正です: {config.enable_build_action}"
            )
            return False

        if not isinstance(config.notification_enabled, bool):
            logger.error(
                f"notification_enabledの値が不正です: {config.notification_enabled}"
            )
            return False

        # ログレベルの検証
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if (
            not isinstance(config.log_level, str)
            or config.log_level.upper() not in valid_log_levels
        ):
            logger.error(
                f"ログレベルが不正です: {config.log_level}（{', '.join(valid_log_levels)}のいずれかを指定してください）"
            )
            return False

        return True

    def _create_config_from_dict(self, config_data: dict) -> Config:
        """辞書からConfigオブジェクトを作成

        Args:
            config_data: 設定データの辞書

        Returns:
            Config: 設定オブジェクト
        """
        return Config(
            check_interval_minutes=config_data.get(
                "check_interval_minutes", Config().check_interval_minutes
            ),
            repository_url=config_data.get("repository_url", Config().repository_url),
            enable_build_action=config_data.get(
                "enable_build_action", Config().enable_build_action
            ),
            notification_enabled=config_data.get(
                "notification_enabled", Config().notification_enabled
            ),
            log_level=config_data.get("log_level", Config().log_level),
        )
