"""
ログ設定モジュール

WSLカーネル監視ツール用のログ設定を提供します。
要件7.1, 7.2, 7.3, 7.4に対応。
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional, TypedDict


class LogRotationConfig:
    """ログローテーション設定クラス"""

    def __init__(
        self,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        cleanup_days: int = 30,
    ):
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.cleanup_days = cleanup_days


class LogBackupInfo(TypedDict):
    path: str
    size: int


class LogStats(TypedDict):
    log_file_path: Optional[str]
    log_file_size: int
    backup_files: list[LogBackupInfo]
    total_size: int


class Logger:
    """ログ管理クラス"""

    _instance: Optional["Logger"] = None
    _logger: Optional[logging.Logger] = None
    _rotation_config: Optional[LogRotationConfig] = None

    def __new__(cls) -> "Logger":
        """シングルトンパターンでインスタンスを作成"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, rotation_config: Optional[LogRotationConfig] = None) -> None:
        """ログ設定を初期化"""
        if self._logger is None:
            self._rotation_config = rotation_config or LogRotationConfig()
            self._setup_logger()

    def _setup_logger(self) -> None:
        """ログ設定をセットアップ"""
        try:
            # ログディレクトリの作成（AppDataディレクトリ内）
            log_dir = self._get_log_directory()
            log_dir.mkdir(parents=True, exist_ok=True)

            # ログファイルパス
            log_file = log_dir / "wsl_kernel_watcher.log"

            # ロガーの作成
            self._logger = logging.getLogger("wsl_kernel_watcher")
            self._logger.setLevel(logging.INFO)

            # 既存のハンドラーをクリア（重複防止）
            self._logger.handlers.clear()

            # フォーマッターの作成
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            # ファイルハンドラーの作成（ローテーション対応）
            assert self._rotation_config is not None
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self._rotation_config.max_bytes,
                backupCount=self._rotation_config.backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)

            # コンソールハンドラーの作成
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)

            # ハンドラーをロガーに追加
            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)

            # 初期化完了ログ
            self._logger.info("ログシステムが初期化されました")
            self._logger.info(f"ログファイル: {log_file}")
            self._logger.debug(f"ログディレクトリ: {log_dir}")

        except Exception:
            # ログ初期化に失敗した場合のフォールバック
            self._setup_fallback_logger()

    def _setup_fallback_logger(self) -> None:
        """フォールバック用の基本ログ設定"""
        self._logger = logging.getLogger("wsl_kernel_watcher")
        self._logger.setLevel(logging.INFO)

        # コンソールハンドラーのみ設定
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)

        self._logger.addHandler(console_handler)
        self._logger.warning("フォールバックログ設定を使用しています")

    def _get_log_directory(self) -> Path:
        """ログディレクトリのパスを取得"""
        # Windows AppDataディレクトリを取得
        appdata = os.getenv("APPDATA")
        if appdata:
            log_dir = Path(appdata) / "WSLKernelWatcher" / "logs"
        else:
            # フォールバック: ユーザーホームディレクトリ
            home = Path.home()
            log_dir = home / ".wsl_kernel_watcher" / "logs"

        return log_dir

    def get_logger(self) -> logging.Logger:
        """ロガーインスタンスを取得"""
        if self._logger is None:
            self._setup_logger()
        assert self._logger is not None  # MyPy用のアサーション
        return self._logger

    def set_log_level(self, level: str) -> None:
        """ログレベルを動的に変更"""
        if self._logger is None:
            self._setup_logger()

        assert self._logger is not None  # MyPy用のアサーション

        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        if level.upper() in level_map:
            old_level = self._logger.level
            new_level = level_map[level.upper()]
            self._logger.setLevel(new_level)

            # ハンドラーのレベルも更新
            for handler in self._logger.handlers:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    handler.setLevel(logging.DEBUG)  # ファイルは常にDEBUGレベル
                elif isinstance(handler, logging.StreamHandler):
                    handler.setLevel(new_level)  # コンソールは設定されたレベル

            self._logger.info(
                f"ログレベルを {logging.getLevelName(old_level)} から {level.upper()} に変更しました"
            )
        else:
            self._logger.warning(f"無効なログレベル: {level}")

    def cleanup_old_logs(self, days_to_keep: int = 30) -> None:
        """古いログファイルを削除"""
        if self._logger is None:
            return

        try:
            log_dir = self._get_log_directory()
            if not log_dir.exists():
                return

            import time

            current_time = time.time()
            cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)

            deleted_count = 0
            for log_file in log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time:
                    try:
                        log_file.unlink()
                        deleted_count += 1
                    except OSError as e:
                        self._logger.warning(
                            f"ログファイル削除に失敗: {log_file} - {e}"
                        )

            if deleted_count > 0:
                self._logger.info(f"{deleted_count}個の古いログファイルを削除しました")

        except Exception as e:
            self._logger.error(f"ログファイルクリーンアップ中にエラーが発生: {e}")

    def get_log_file_path(self) -> Optional[Path]:
        """現在のログファイルパスを取得"""
        try:
            log_dir = self._get_log_directory()
            return log_dir / "wsl_kernel_watcher.log"
        except Exception:
            return None

    def update_rotation_config(self, rotation_config: LogRotationConfig) -> None:
        """ログローテーション設定を動的に更新"""
        if self._logger is None:
            return

        self._rotation_config = rotation_config

        # 既存のファイルハンドラーを探して更新
        for handler in self._logger.handlers[:]:  # コピーを作成してイテレート
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                # 古いハンドラーを削除
                self._logger.removeHandler(handler)
                handler.close()

                # 新しい設定でハンドラーを再作成
                log_file = self.get_log_file_path()
                if log_file:
                    new_handler = logging.handlers.RotatingFileHandler(
                        log_file,
                        maxBytes=rotation_config.max_bytes,
                        backupCount=rotation_config.backup_count,
                        encoding="utf-8",
                    )
                    new_handler.setLevel(logging.DEBUG)

                    # フォーマッターを設定
                    formatter = logging.Formatter(
                        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                    )
                    new_handler.setFormatter(formatter)

                    # 新しいハンドラーを追加
                    self._logger.addHandler(new_handler)

                    self._logger.info(
                        f"ログローテーション設定を更新しました: "
                        f"最大サイズ={rotation_config.max_bytes}bytes, "
                        f"バックアップ数={rotation_config.backup_count}"
                    )
                break

    def force_log_rotation(self) -> bool:
        """ログローテーションを強制実行"""
        if self._logger is None:
            return False

        try:
            for handler in self._logger.handlers:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    handler.doRollover()
                    self._logger.info("ログローテーションを強制実行しました")
                    return True
            return False
        except Exception as e:
            if self._logger:
                self._logger.error(f"ログローテーション強制実行中にエラー: {e}")
            return False

    def get_log_stats(self) -> LogStats:
        """ログファイルの統計情報を取得"""
        stats: LogStats = {
            "log_file_path": None,
            "log_file_size": 0,
            "backup_files": [],
            "total_size": 0,
        }

        try:
            log_file = self.get_log_file_path()
            if log_file and log_file.exists():
                log_file_size = log_file.stat().st_size
                stats["log_file_path"] = str(log_file)
                stats["log_file_size"] = log_file_size
                total_size = log_file_size

                # バックアップファイルを収集
                log_dir = log_file.parent
                backup_pattern = f"{log_file.name}.*"
                for backup_file in log_dir.glob(backup_pattern):
                    if backup_file != log_file:
                        backup_size = backup_file.stat().st_size
                        stats["backup_files"].append(
                            {
                                "path": str(backup_file),
                                "size": backup_size,
                            }
                        )
                        total_size += backup_size

                stats["total_size"] = total_size

        except Exception as e:
            if self._logger:
                self._logger.error(f"ログ統計取得中にエラー: {e}")

        return stats

def get_logger() -> logging.Logger:
    """グローバルロガーを取得するヘルパー関数"""
    logger_instance = Logger()
    return logger_instance.get_logger()


def set_log_level(level: str) -> None:
    """ログレベルを設定するヘルパー関数"""
    logger_instance = Logger()
    logger_instance.set_log_level(level)


def cleanup_old_logs(days_to_keep: int = 30) -> None:
    """古いログファイルを削除するヘルパー関数"""
    logger_instance = Logger()
    logger_instance.cleanup_old_logs(days_to_keep)


def get_log_file_path() -> Optional[Path]:
    """ログファイルパスを取得するヘルパー関数"""
    logger_instance = Logger()
    return logger_instance.get_log_file_path()


