#!/usr/bin/env python3
"""Windows Toast通知テストスクリプト"""

import logging
import sys

from src.docker_notifier import DockerNotifier

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    print("=" * 60)
    print("Windows Toast通知テスト")
    print("=" * 60)
    print()

    notifier = DockerNotifier()

    print("テスト通知を送信します...")
    print("Windows側で通知が表示されるか確認してください")
    print()

    # テスト通知1: シンプルな通知
    print("1. シンプルな通知テスト")
    result1 = notifier.send_notification(
        "WSL Kernel Watcher テスト", "通知システムが正常に動作しています"
    )
    print(f"   結果: {'✅ 成功' if result1 else '❌ 失敗'}")
    print()

    # テスト通知2: カーネル更新通知
    print("2. カーネル更新通知テスト")
    result2 = notifier.notify_kernel_update(
        "linux-msft-wsl-6.6.87.2", "linux-msft-wsl-6.6.36.3"
    )
    print(f"   結果: {'✅ 成功' if result2 else '❌ 失敗'}")
    print()

    print("=" * 60)
    if result1 and result2:
        print("✅ 全てのテストが成功しました！")
        print("Windows側で2つの通知が表示されているはずです")
        return 0
    else:
        print("❌ 一部のテストが失敗しました")
        print("トラブルシューティング:")
        print("1. Docker Desktop for WindowsのWSL2統合が有効か確認")
        print("2. wsl.exeにアクセスできるか確認: which wsl.exe")
        print(
            "3. PowerShellが実行できるか確認: wsl.exe -e powershell.exe -Command 'echo test'"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
