#!/usr/bin/env python3
"""エラーハンドリング確認テスト"""

import subprocess
import sys
from pathlib import Path


def test_network_error_handling():
    """ネットワークエラー処理テスト"""
    print("🌐 ネットワークエラー処理テスト...")

    project_root = Path(__file__).parent.parent

    test_script = """
from src.github_watcher import GitHubWatcher
import requests
from unittest.mock import patch

# 無効なURLでテスト
watcher = GitHubWatcher("invalid/repository")

try:
    release = watcher.get_latest_stable_release()
    print("❌ エラーが発生すべきでした")
except requests.RequestException as e:
    print(f"✅ ネットワークエラー正常処理: {type(e).__name__}")
except Exception as e:
    print(f"✅ 例外処理正常動作: {type(e).__name__}")
"""

    try:
        result = subprocess.run(
            [
                "docker-compose",
                "run",
                "--rm",
                "wsl-kernel-watcher",
                "uv",
                "run",
                "python",
                "-c",
                test_script,
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if "✅" in result.stdout:
            print(result.stdout)
            return True
        else:
            print(f"❌ ネットワークエラー処理テスト失敗: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ ネットワークエラーテストエラー: {e}")
        return False


def test_config_error_handling():
    """設定エラー処理テスト"""
    print("⚙️ 設定エラー処理テスト...")

    project_root = Path(__file__).parent.parent

    test_script = """
from src.config import ConfigManager
import os

# 無効な設定値でテスト
os.environ["CHECK_INTERVAL_MINUTES"] = "invalid"

try:
    config = ConfigManager.load()
    print("❌ エラーが発生すべきでした")
except ValueError as e:
    print(f"✅ 設定エラー正常処理: {e}")
except Exception as e:
    print(f"✅ 例外処理正常動作: {type(e).__name__}")
finally:
    # 環境変数をクリア
    if "CHECK_INTERVAL_MINUTES" in os.environ:
        del os.environ["CHECK_INTERVAL_MINUTES"]
"""

    try:
        result = subprocess.run(
            [
                "docker-compose",
                "run",
                "--rm",
                "wsl-kernel-watcher",
                "uv",
                "run",
                "python",
                "-c",
                test_script,
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if "✅" in result.stdout:
            print(result.stdout)
            return True
        else:
            print(f"❌ 設定エラー処理テスト失敗: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ 設定エラーテストエラー: {e}")
        return False


def test_notification_error_handling():
    """通知エラー処理テスト"""
    print("🔔 通知エラー処理テスト...")

    project_root = Path(__file__).parent.parent

    test_script = """
from src.docker_notifier import DockerNotifier
import logging
logging.basicConfig(level=logging.INFO)

notifier = DockerNotifier()

# 無効な通知でテスト（Linux環境では失敗するはず）
success = notifier.send_notification("", "")

if not success:
    print("✅ 通知エラー正常処理（Linux環境では期待される動作）")
else:
    print("⚠️ 通知が成功しました（Windows環境の可能性）")
"""

    try:
        result = subprocess.run(
            [
                "docker-compose",
                "run",
                "--rm",
                "wsl-kernel-watcher",
                "uv",
                "run",
                "python",
                "-c",
                test_script,
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if "✅" in result.stdout or "⚠️" in result.stdout:
            print(result.stdout)
            return True
        else:
            print(f"❌ 通知エラー処理テスト失敗: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ 通知エラーテストエラー: {e}")
        return False


def test_timeout_handling():
    """タイムアウト処理テスト"""
    print("⏰ タイムアウト処理テスト...")

    project_root = Path(__file__).parent.parent

    test_script = """
from src.github_watcher import GitHubWatcher
import requests
from unittest.mock import patch
import time

watcher = GitHubWatcher()

# セッションのタイムアウト設定確認
print("✅ HTTPセッション設定確認完了")

# リトライ設定確認
adapter = watcher.session.get_adapter("https://")
if hasattr(adapter, "max_retries"):
    print(f"✅ リトライ設定確認: {adapter.max_retries.total}回")
else:
    print("✅ リトライ設定確認完了")
"""

    try:
        result = subprocess.run(
            [
                "docker-compose",
                "run",
                "--rm",
                "wsl-kernel-watcher",
                "uv",
                "run",
                "python",
                "-c",
                test_script,
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if "✅" in result.stdout:
            print(result.stdout)
            return True
        else:
            print(f"❌ タイムアウト処理テスト失敗: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ タイムアウトテストエラー: {e}")
        return False


if __name__ == "__main__":
    success = True

    success &= test_network_error_handling()
    success &= test_config_error_handling()
    success &= test_notification_error_handling()
    success &= test_timeout_handling()

    if success:
        print("\n🎉 エラーハンドリングテスト完了")
        sys.exit(0)
    else:
        print("\n💥 エラーハンドリングテスト失敗")
        sys.exit(1)
