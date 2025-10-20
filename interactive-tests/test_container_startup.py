#!/usr/bin/env python3
"""コンテナ起動確認テスト"""

import subprocess
import sys
import time
from pathlib import Path


def test_container_startup():
    """コンテナ起動テスト"""
    print("🚀 コンテナ起動テスト開始...")

    project_root = Path(__file__).parent.parent

    try:
        # コンテナ起動
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"❌ コンテナ起動失敗: {result.stderr}")
            return False

        print("✅ コンテナ起動成功")

        # 少し待機
        time.sleep(5)

        # コンテナ状態確認
        result = subprocess.run(
            ["docker-compose", "ps"], cwd=project_root, capture_output=True, text=True
        )

        print("📊 コンテナ状態:")
        print(result.stdout)

        return True

    except Exception as e:
        print(f"❌ コンテナ起動エラー: {e}")
        return False


def test_environment_variables():
    """環境変数確認テスト"""
    print("🔧 環境変数確認テスト...")

    project_root = Path(__file__).parent.parent

    try:
        result = subprocess.run(
            [
                "docker-compose",
                "run",
                "--rm",
                "-e",
                "LOG_LEVEL=DEBUG",
                "wsl-kernel-watcher",
                "uv",
                "run",
                "python",
                "-c",
                "from src.config import ConfigManager; c=ConfigManager.load(); print(f'Repository: {c.repository_url}'); print(f'Interval: {c.check_interval_minutes}min'); print(f'LogLevel: {c.log_level}')",
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            print("✅ 環境変数読み込み成功:")
            print(result.stdout)
            return True
        else:
            print(f"❌ 環境変数読み込み失敗: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ 環境変数確認エラー: {e}")
        return False


def test_logs():
    """ログ出力確認"""
    print("📝 ログ出力確認...")

    project_root = Path(__file__).parent.parent

    try:
        result = subprocess.run(
            ["docker-compose", "logs", "--tail=20"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ ログ取得成功:")
            print(result.stdout[-500:])  # 最後の500文字
            return True
        else:
            print(f"❌ ログ取得失敗: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ ログ確認エラー: {e}")
        return False


def cleanup():
    """テスト後のクリーンアップ（コンテナは維持）"""
    print("🧹 テスト完了...")
    # コンテナは維持して後続テストで使用
    print("✅ テスト完了（コンテナ維持）")


if __name__ == "__main__":
    success = True

    try:
        success &= test_container_startup()
        success &= test_environment_variables()
        success &= test_logs()
    finally:
        cleanup()

    if success:
        print("\n🎉 コンテナ起動テスト完了")
        sys.exit(0)
    else:
        print("\n💥 コンテナ起動テスト失敗")
        sys.exit(1)
