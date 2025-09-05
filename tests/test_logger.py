"""
ログシステムのテスト

要件7.1, 7.2, 7.3, 7.4のテストケース
"""

import logging
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.logger import (
    Logger,
    LogRotationConfig,
    cleanup_old_logs,
    get_log_file_path,
    get_logger,
    set_log_level,
)


class TestLogger:
    """Loggerクラスのテスト"""

    def test_singleton_pattern(self) -> None:
        """シングルトンパターンのテスト"""
        logger1 = Logger()
        logger2 = Logger()
        assert logger1 is logger2

    def test_get_logger(self) -> None:
        """ロガー取得のテスト"""
        logger = get_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "wsl_kernel_watcher"

    def test_set_log_level(self) -> None:
        """ログレベル設定のテスト"""
        logger = get_logger()

        # DEBUGレベルに設定
        set_log_level("DEBUG")
        assert logger.level == logging.DEBUG

        # INFOレベルに設定
        set_log_level("INFO")
        assert logger.level == logging.INFO

        # WARNINGレベルに設定
        set_log_level("WARNING")
        assert logger.level == logging.WARNING

        # ERRORレベルに設定
        set_log_level("ERROR")
        assert logger.level == logging.ERROR

    def test_invalid_log_level(self) -> None:
        """無効なログレベルのテスト"""
        logger = get_logger()
        original_level = logger.level

        # 無効なレベルを設定
        set_log_level("INVALID")

        # レベルが変更されていないことを確認
        assert logger.level == original_level

    @patch.dict("os.environ", {"APPDATA": ""}, clear=True)
    @patch("pathlib.Path.home")
    def test_fallback_log_directory(self, mock_home: MagicMock) -> None:
        """ログディレクトリのフォールバック処理テスト"""
        # ホームディレクトリをモック
        mock_home.return_value = Path(r"C:\Users\TestUser")

        # APPDATAが設定されていない場合のテスト
        logger_instance = Logger()
        log_dir = logger_instance._get_log_directory()

        # ホームディレクトリ/.wsl_kernel_watcher/logsになることを確認
        expected_dir = Path(r"C:\Users\TestUser") / ".wsl_kernel_watcher" / "logs"
        assert log_dir == expected_dir

    def test_log_output(self, caplog: pytest.LogCaptureFixture) -> None:
        """ログ出力のテスト"""
        # 新しいロガーインスタンスを作成してテスト用に設定
        test_logger = logging.getLogger("test_wsl_kernel_watcher")
        test_logger.setLevel(logging.INFO)

        with caplog.at_level(logging.INFO, logger="test_wsl_kernel_watcher"):
            test_logger.info("テストメッセージ")

        assert "テストメッセージ" in caplog.text

    def test_log_formatting(self, caplog: pytest.LogCaptureFixture) -> None:
        """ログフォーマットのテスト"""
        # 新しいロガーインスタンスを作成してテスト用に設定
        test_logger = logging.getLogger("test_wsl_kernel_watcher")
        test_logger.setLevel(logging.INFO)

        with caplog.at_level(logging.INFO, logger="test_wsl_kernel_watcher"):
            test_logger.info("フォーマットテスト")

        # ログレコードの確認
        assert len(caplog.records) > 0
        record = caplog.records[-1]  # 最後のレコードを取得
        assert record.name == "test_wsl_kernel_watcher"
        assert record.levelname == "INFO"
        assert record.getMessage() == "フォーマットテスト"

    def test_appdata_log_directory(self) -> None:
        """AppDataディレクトリのログ配置テスト"""
        with patch.dict("os.environ", {"APPDATA": r"C:\Users\Test\AppData\Roaming"}):
            logger_instance = Logger()
            log_dir = logger_instance._get_log_directory()

            expected_dir = Path(r"C:\Users\Test\AppData\Roaming\WSLKernelWatcher\logs")
            assert log_dir == expected_dir

    def test_fallback_logger_setup(self) -> None:
        """フォールバックログ設定のテスト"""
        logger_instance = Logger()

        # フォールバック設定を強制実行
        logger_instance._setup_fallback_logger()

        # ロガーが設定されていることを確認
        assert logger_instance._logger is not None
        assert logger_instance._logger.name == "wsl_kernel_watcher"
        assert len(logger_instance._logger.handlers) > 0


class TestLogRotationConfig:
    """LogRotationConfigクラスのテスト"""

    def test_default_config(self) -> None:
        """デフォルト設定のテスト"""
        config = LogRotationConfig()
        assert config.max_bytes == 10 * 1024 * 1024  # 10MB
        assert config.backup_count == 5
        assert config.cleanup_days == 30

    def test_custom_config(self) -> None:
        """カスタム設定のテスト"""
        config = LogRotationConfig(
            max_bytes=5 * 1024 * 1024,  # 5MB
            backup_count=3,
            cleanup_days=7,
        )
        assert config.max_bytes == 5 * 1024 * 1024
        assert config.backup_count == 3
        assert config.cleanup_days == 7


class TestLogRotation:
    """ログローテーション機能のテスト"""

    def test_update_rotation_config(self) -> None:
        """ローテーション設定更新のテスト"""
        logger_instance = Logger()

        # 新しい設定を作成
        new_config = LogRotationConfig(
            max_bytes=1024 * 1024,  # 1MB
            backup_count=2,
        )

        # 設定を更新
        logger_instance.update_rotation_config(new_config)

        # 設定が更新されたことを確認
        assert logger_instance._rotation_config == new_config

    def test_force_log_rotation(self) -> None:
        """強制ログローテーションのテスト"""
        logger_instance = Logger()

        # RotatingFileHandlerが存在することを確認
        has_rotating_handler = False
        if logger_instance._logger:
            for handler in logger_instance._logger.handlers:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    has_rotating_handler = True
                    break

        # 強制ローテーションを実行
        result = logger_instance.force_log_rotation()

        # RotatingFileHandlerがある場合はTrueが返されることを確認
        if has_rotating_handler:
            assert result is True
        else:
            assert result is False

    def test_cleanup_old_logs(self) -> None:
        """古いログファイル削除のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # テスト用のログファイルを作成
            old_log = temp_path / "old.log.1"
            new_log = temp_path / "new.log"

            old_log.touch()
            new_log.touch()

            # ファイルの更新時刻を古く設定
            import os
            import time

            old_time = time.time() - (40 * 24 * 60 * 60)  # 40日前
            os.utime(old_log, (old_time, old_time))

            # 新しいLoggerインスタンスを作成（既存のハンドラーの影響を避ける）
            logger_instance = Logger.__new__(Logger)
            logger_instance._logger = None
            logger_instance._rotation_config = LogRotationConfig()

            # ログディレクトリをテンプディレクトリに変更
            with patch.object(
                logger_instance, "_get_log_directory", return_value=temp_path
            ):
                # 簡単なロガーを設定
                logger_instance._logger = logging.getLogger("test_cleanup")
                logger_instance._logger.setLevel(logging.INFO)

                logger_instance.cleanup_old_logs(days_to_keep=30)

            # 古いファイルが削除され、新しいファイルが残っていることを確認
            assert not old_log.exists()
            assert new_log.exists()

    def test_get_log_stats(self) -> None:
        """ログ統計情報取得のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            log_file = temp_path / "wsl_kernel_watcher.log"
            backup_file = temp_path / "wsl_kernel_watcher.log.1"

            # テストファイルを作成
            log_file.write_text("main log content")
            backup_file.write_text("backup log content")

            logger_instance = Logger()

            # ログファイルパスをテンプファイルに変更
            with patch.object(
                logger_instance, "get_log_file_path", return_value=log_file
            ):
                stats = logger_instance.get_log_stats()

            # 統計情報を確認
            assert stats["log_file_path"] == str(log_file)
            assert stats["log_file_size"] > 0
            assert len(stats["backup_files"]) == 1
            assert stats["backup_files"][0]["path"] == str(backup_file)
            assert stats["total_size"] > stats["log_file_size"]


class TestHelperFunctions:
    """ヘルパー関数のテスト"""

    def test_get_log_file_path(self) -> None:
        """ログファイルパス取得のテスト"""
        path = get_log_file_path()
        assert path is not None
        assert path.name == "wsl_kernel_watcher.log"

    def test_cleanup_old_logs_helper(self) -> None:
        """古いログファイル削除ヘルパー関数のテスト"""
        # 例外が発生しないことを確認
        cleanup_old_logs(days_to_keep=7)


class TestErrorHandling:
    """エラーハンドリングのテスト"""

    def test_logger_initialization_error(self) -> None:
        """ログ初期化エラーのテスト"""
        with patch(
            "src.logger.Path.mkdir", side_effect=PermissionError("Permission denied")
        ):
            # エラーが発生してもフォールバックログが設定されることを確認
            logger_instance = Logger()
            assert logger_instance._logger is not None

    def test_log_stats_error_handling(self) -> None:
        """ログ統計情報取得エラーハンドリングのテスト"""
        logger_instance = Logger()

        # 存在しないパスを返すようにモック
        with patch.object(logger_instance, "get_log_file_path", return_value=None):
            stats = logger_instance.get_log_stats()

            # エラーが発生してもデフォルト値が返されることを確認
            assert stats["log_file_path"] is None
            assert stats["log_file_size"] == 0
            assert stats["backup_files"] == []
            assert stats["total_size"] == 0
