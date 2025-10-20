#!/usr/bin/env python3
"""Dockerビルド確認テスト"""

import subprocess
import sys
from pathlib import Path


def test_docker_build():
    """Dockerイメージビルドテスト"""
    print("🐳 Dockerイメージビルドテスト開始...")

    project_root = Path(__file__).parent.parent

    try:
        result = subprocess.run(
            ["docker-compose", "build"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            print("✅ Dockerビルド成功")
            return True
        else:
            print(f"❌ Dockerビルド失敗: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Dockerビルドタイムアウト")
        return False
    except Exception as e:
        print(f"❌ Dockerビルドエラー: {e}")
        return False


def test_image_size():
    """イメージサイズ確認"""
    print("📏 イメージサイズ確認...")

    try:
        result = subprocess.run(
            [
                "docker",
                "images",
                "wsl-kernel-watcher-wsl-kernel-watcher",
                "--format",
                "table {{.Size}}",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            size = result.stdout.strip().split("\n")[-1]
            print(f"📦 イメージサイズ: {size}")
            return True
        else:
            print("❌ イメージサイズ取得失敗")
            return False

    except Exception as e:
        print(f"❌ イメージサイズ確認エラー: {e}")
        return False


if __name__ == "__main__":
    success = True

    success &= test_docker_build()
    success &= test_image_size()

    if success:
        print("\n🎉 Dockerビルドテスト完了")
        sys.exit(0)
    else:
        print("\n💥 Dockerビルドテスト失敗")
        sys.exit(1)
