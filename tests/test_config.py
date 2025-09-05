"""設定管理システムのテストモジュール

ConfigクラスとConfigManagerクラスの単体テストを実装。
設定ファイルの読み込み、作成、検証機能をテストする。
"""

import logging
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import toml

from src.config import Config, ConfigManager


class TestConfig:
    """Configデータクラスのテスト"""

    def test_config_default_values(self):
        """デフォルト値が正しく設定されることをテスト"""
        config = Config()

        assert config.check_interval_minutes == 30
        assert config.repository_url == "microsoft/WSL2-Linux-Kernel"
        assert config.enable_build_action is False
        assert config.notification_enabled is True
        assert config.log_level == "INFO"

    def test_config_custom_values(self):
        """カスタム値が正しく設定されることをテスト"""
        config = Config(
            check_interval_minutes=60,
            repository_url="custom/repo",
            enable_build_action=True,
            notification_enabled=False,
            log_level="DEBUG",
        )

        assert config.check_interval_minutes == 60
        assert config.repository_url == "custom/repo"
        assert config.enable_build_action is True
        assert config.notification_enabled is False
        assert config.log_level == "DEBUG"


class TestConfigManager:
    """ConfigManagerクラスのテスト"""

    def test_init_with_default_path(self):
        """デフォルトパスでの初期化をテスト"""
        manager = ConfigManager()
        assert manager.config_path == Path("config.toml")

    def test_init_with_custom_path(self):
        """カスタムパスでの初期化をテスト"""
        custom_path = Path("custom_config.toml")
        manager = ConfigManager(custom_path)
        assert manager.config_path == custom_path

    def test_create_default_config(self):
        """デフォルト設定ファイルの作成をテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.toml"
            manager = ConfigManager(config_path)

            manager.create_default_config()

            # ファイルが作成されたことを確認
            assert config_path.exists()

            # ファイル内容を確認
            with open(config_path, encoding="utf-8") as f:
                config_data = toml.load(f)

            expected_config = Config()
            assert (
                config_data["check_interval_minutes"]
                == expected_config.check_interval_minutes
            )
            assert config_data["repository_url"] == expected_config.repository_url
            assert (
                config_data["enable_build_action"]
                == expected_config.enable_build_action
            )
            assert (
                config_data["notification_enabled"]
                == expected_config.notification_enabled
            )
            assert config_data["log_level"] == expected_config.log_level

    def test_create_default_config_file_error(self):
        """設定ファイル作成時のエラーハンドリングをテスト"""
        # 存在しないディレクトリにファイルを作成しようとする
        invalid_path = Path("/invalid/path/config.toml")
        manager = ConfigManager(invalid_path)

        with pytest.raises(Exception):
            manager.create_default_config()

    def test_load_config_file_not_exists(self, caplog):
        """設定ファイルが存在しない場合のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nonexistent_config.toml"
            manager = ConfigManager(config_path)

            with caplog.at_level(logging.INFO):
                config = manager.load_config()

            # デフォルト設定が返されることを確認
            expected_config = Config()
            assert (
                config.check_interval_minutes == expected_config.check_interval_minutes
            )
            assert config.repository_url == expected_config.repository_url
            assert config.enable_build_action == expected_config.enable_build_action
            assert config.notification_enabled == expected_config.notification_enabled
            assert config.log_level == expected_config.log_level

            # ログメッセージを確認
            assert "が存在しません。デフォルト設定で作成します。" in caplog.text

            # ファイルが作成されたことを確認
            assert config_path.exists()

    def test_load_config_valid_file(self):
        """有効な設定ファイルの読み込みをテスト"""
        config_data = {
            "check_interval_minutes": 60,
            "repository_url": "test/repo",
            "enable_build_action": True,
            "notification_enabled": False,
            "log_level": "DEBUG",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.toml"

            # テスト用設定ファイルを作成
            with open(config_path, "w", encoding="utf-8") as f:
                toml.dump(config_data, f)

            manager = ConfigManager(config_path)
            config = manager.load_config()

            assert config.check_interval_minutes == 60
            assert config.repository_url == "test/repo"
            assert config.enable_build_action is True
            assert config.notification_enabled is False
            assert config.log_level == "DEBUG"

    def test_load_config_partial_file(self):
        """部分的な設定ファイルの読み込みをテスト（不足項目はデフォルト値を使用）"""
        config_data = {
            "check_interval_minutes": 120,
            "repository_url": "partial/repo",
            # 他の項目は省略
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "partial_config.toml"

            with open(config_path, "w", encoding="utf-8") as f:
                toml.dump(config_data, f)

            manager = ConfigManager(config_path)
            config = manager.load_config()

            # 指定された値
            assert config.check_interval_minutes == 120
            assert config.repository_url == "partial/repo"

            # デフォルト値
            assert config.enable_build_action is False
            assert config.notification_enabled is True
            assert config.log_level == "INFO"

    def test_load_config_invalid_toml(self, caplog):
        """不正なTOML形式のファイルの処理をテスト"""
        invalid_toml = "invalid toml content [[[["

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "invalid_config.toml"

            with open(config_path, "w", encoding="utf-8") as f:
                f.write(invalid_toml)

            manager = ConfigManager(config_path)

            with caplog.at_level(logging.ERROR):
                config = manager.load_config()

            # デフォルト設定が返されることを確認
            expected_config = Config()
            assert (
                config.check_interval_minutes == expected_config.check_interval_minutes
            )

            # エラーログが出力されることを確認
            assert "設定ファイルの形式が不正です" in caplog.text

    def test_load_config_file_read_error(self, caplog):
        """ファイル読み込みエラーの処理をテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.toml"

            # 設定ファイルを作成
            with open(config_path, "w", encoding="utf-8") as f:
                f.write("check_interval_minutes = 30\n")

            manager = ConfigManager(config_path)

            # toml.loadでエラーを発生させる
            with patch("toml.load", side_effect=PermissionError("Permission denied")):
                with caplog.at_level(logging.ERROR):
                    config = manager.load_config()

                # デフォルト設定が返されることを確認
                expected_config = Config()
                assert (
                    config.check_interval_minutes
                    == expected_config.check_interval_minutes
                )

                # エラーログが出力されることを確認
                assert "設定ファイルの読み込み中にエラーが発生しました" in caplog.text

    def test_validate_config_valid(self):
        """有効な設定の検証をテスト"""
        manager = ConfigManager()

        valid_config = Config(
            check_interval_minutes=60,
            repository_url="owner/repo",
            enable_build_action=True,
            notification_enabled=False,
            log_level="DEBUG",
        )

        assert manager.validate_config(valid_config) is True

    def test_validate_config_invalid_interval(self, caplog):
        """無効なチェック間隔の検証をテスト"""
        manager = ConfigManager()

        # 0分（無効）
        invalid_config = Config(check_interval_minutes=0)
        with caplog.at_level(logging.ERROR):
            assert manager.validate_config(invalid_config) is False
        assert "チェック間隔が不正です" in caplog.text

        caplog.clear()

        # 1441分（無効、24時間を超える）
        invalid_config = Config(check_interval_minutes=1441)
        with caplog.at_level(logging.ERROR):
            assert manager.validate_config(invalid_config) is False
        assert "チェック間隔が不正です" in caplog.text

        caplog.clear()

        # 文字列（無効）
        invalid_config = Config()
        invalid_config.check_interval_minutes = "invalid"  # type: ignore
        with caplog.at_level(logging.ERROR):
            assert manager.validate_config(invalid_config) is False
        assert "チェック間隔が不正です" in caplog.text

    def test_validate_config_invalid_repository_url(self, caplog):
        """無効なリポジトリURLの検証をテスト"""
        manager = ConfigManager()

        # 空文字列
        invalid_config = Config(repository_url="")
        with caplog.at_level(logging.ERROR):
            assert manager.validate_config(invalid_config) is False
        assert "リポジトリURLが不正です" in caplog.text

        caplog.clear()

        # スラッシュなし
        invalid_config = Config(repository_url="invalid-repo")
        with caplog.at_level(logging.ERROR):
            assert manager.validate_config(invalid_config) is False
        assert "リポジトリURLの形式が不正です" in caplog.text

        caplog.clear()

        # 複数のスラッシュ
        invalid_config = Config(repository_url="owner/repo/extra")
        with caplog.at_level(logging.ERROR):
            assert manager.validate_config(invalid_config) is False
        assert "リポジトリURLの形式が不正です" in caplog.text

    def test_validate_config_invalid_boolean_values(self, caplog):
        """無効なブール値の検証をテスト"""
        manager = ConfigManager()

        # enable_build_actionが文字列
        invalid_config = Config()
        invalid_config.enable_build_action = "true"  # type: ignore
        with caplog.at_level(logging.ERROR):
            assert manager.validate_config(invalid_config) is False
        assert "enable_build_actionの値が不正です" in caplog.text

        caplog.clear()

        # notification_enabledが数値
        invalid_config = Config()
        invalid_config.notification_enabled = 1  # type: ignore
        with caplog.at_level(logging.ERROR):
            assert manager.validate_config(invalid_config) is False
        assert "notification_enabledの値が不正です" in caplog.text

    def test_validate_config_invalid_log_level(self, caplog):
        """無効なログレベルの検証をテスト"""
        manager = ConfigManager()

        # 無効なログレベル
        invalid_config = Config(log_level="INVALID")
        with caplog.at_level(logging.ERROR):
            assert manager.validate_config(invalid_config) is False
        assert "ログレベルが不正です" in caplog.text

        caplog.clear()

        # 数値
        invalid_config = Config()
        invalid_config.log_level = 123  # type: ignore
        with caplog.at_level(logging.ERROR):
            assert manager.validate_config(invalid_config) is False
        assert "ログレベルが不正です" in caplog.text

    def test_validate_config_valid_log_levels(self):
        """有効なログレベルの検証をテスト"""
        manager = ConfigManager()

        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]

        for level in valid_levels:
            config = Config(log_level=level)
            assert manager.validate_config(config) is True

    def test_create_config_from_dict(self):
        """辞書からConfigオブジェクトの作成をテスト"""
        manager = ConfigManager()

        config_dict = {
            "check_interval_minutes": 90,
            "repository_url": "test/repo",
            "enable_build_action": True,
            "notification_enabled": False,
            "log_level": "WARNING",
        }

        config = manager._create_config_from_dict(config_dict)

        assert config.check_interval_minutes == 90
        assert config.repository_url == "test/repo"
        assert config.enable_build_action is True
        assert config.notification_enabled is False
        assert config.log_level == "WARNING"

    def test_create_config_from_dict_missing_keys(self):
        """不完全な辞書からConfigオブジェクトの作成をテスト（デフォルト値使用）"""
        manager = ConfigManager()

        config_dict = {
            "check_interval_minutes": 45,
            # 他のキーは省略
        }

        config = manager._create_config_from_dict(config_dict)

        # 指定された値
        assert config.check_interval_minutes == 45

        # デフォルト値
        assert config.repository_url == "microsoft/WSL2-Linux-Kernel"
        assert config.enable_build_action is False
        assert config.notification_enabled is True
        assert config.log_level == "INFO"

    def test_create_config_from_empty_dict(self):
        """空の辞書からConfigオブジェクトの作成をテスト（全てデフォルト値）"""
        manager = ConfigManager()

        config = manager._create_config_from_dict({})
        expected_config = Config()

        assert config.check_interval_minutes == expected_config.check_interval_minutes
        assert config.repository_url == expected_config.repository_url
        assert config.enable_build_action == expected_config.enable_build_action
        assert config.notification_enabled == expected_config.notification_enabled
        assert config.log_level == expected_config.log_level
