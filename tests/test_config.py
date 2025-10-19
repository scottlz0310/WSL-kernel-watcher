"""設定管理モジュールのテスト"""

import os
from unittest.mock import patch

import pytest

from src.config import Config, ConfigManager


class TestConfig:
    """Configデータクラスのテスト"""

    def test_default_values(self):
        """デフォルト値テスト"""
        config = Config()

        assert config.repository_url == "microsoft/WSL2-Linux-Kernel"
        assert config.check_interval_minutes == 30
        assert config.log_level == "INFO"
        assert config.github_token is None


class TestConfigManager:
    """ConfigManagerクラスのテスト"""

    def test_load_default_config(self):
        """デフォルト設定読み込みテスト"""
        with patch.dict(os.environ, {}, clear=True):
            config = ConfigManager.load()

            assert config.repository_url == "microsoft/WSL2-Linux-Kernel"
            assert config.check_interval_minutes == 30
            assert config.log_level == "INFO"
            assert config.github_token is None

    def test_load_from_environment(self):
        """環境変数からの設定読み込みテスト"""
        env_vars = {
            "REPOSITORY_URL": "custom/repo",
            "CHECK_INTERVAL_MINUTES": "60",
            "LOG_LEVEL": "DEBUG",
            "GITHUB_TOKEN": "test_token_123",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConfigManager.load()

            assert config.repository_url == "custom/repo"
            assert config.check_interval_minutes == 60
            assert config.log_level == "DEBUG"
            assert config.github_token == "test_token_123"

    def test_load_partial_environment(self):
        """部分的な環境変数設定テスト"""
        env_vars = {"REPOSITORY_URL": "partial/repo", "LOG_LEVEL": "WARNING"}

        with patch.dict(os.environ, env_vars, clear=True):
            config = ConfigManager.load()

            assert config.repository_url == "partial/repo"
            assert config.check_interval_minutes == 30  # デフォルト値
            assert config.log_level == "WARNING"
            assert config.github_token is None  # デフォルト値

    def test_load_invalid_interval(self):
        """無効な間隔設定テスト"""
        env_vars = {"CHECK_INTERVAL_MINUTES": "invalid_number"}

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError):
                ConfigManager.load()
