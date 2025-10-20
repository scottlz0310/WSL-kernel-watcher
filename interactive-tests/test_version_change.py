#!/usr/bin/env python3
"""バージョン変更通知テスト（模擬的なカーネルダウングレード）"""

import subprocess
import sys
from pathlib import Path


def test_version_change_notification():
    """バージョン変更通知テスト"""
    print("🔄 バージョン変更通知テスト開始...")
    print("📋 模擬的なカーネルダウングレードで通知動作を確認します")

    project_root = Path(__file__).parent.parent

    # 模擬的なバージョン変更スクリプト
    test_script = """
import asyncio
from src.main import WSLKernelWatcher

async def test_version_change():
    watcher = WSLKernelWatcher()

    # 初期バージョン設定（古いバージョンに設定）
    watcher.current_version = "linux-msft-wsl-6.6.36.8"
    print(f"📋 模擬初期バージョン: {watcher.current_version}")

    # 更新チェック実行（最新バージョンを検出）
    await watcher.check_for_updates()

    print("✅ バージョン変更通知テスト完了")

if __name__ == "__main__":
    asyncio.run(test_version_change())
"""

    try:
        print("🐳 Dockerコンテナでバージョン変更テスト実行中...")
        print("📱 通知ダイアログの表示を確認してください")

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
            timeout=120,
        )

        if result.returncode == 0:
            print("✅ Docker実行成功")

            response = (
                input(
                    "\n❓ 'WSL2カーネル更新通知' ダイアログが表示されましたか？ (y/N): "
                )
                .strip()
                .lower()
            )

            if response == "y":
                print("🎉 バージョン変更通知テスト成功！")
                print("✅ 実際のカーネル更新時にも同様に通知されます")
                return True
            else:
                print("❌ 通知に問題があります")
                return False
        else:
            print(f"❌ Docker実行失敗: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ テストタイムアウト")
        return False
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        return False


if __name__ == "__main__":
    print("🧪 バージョン変更通知テスト開始")
    print("=" * 60)

    success = test_version_change_notification()

    print("\n" + "=" * 60)
    if success:
        print("🎉 バージョン変更通知テスト完了")
        sys.exit(0)
    else:
        print("💥 バージョン変更通知テスト失敗")
        sys.exit(1)
