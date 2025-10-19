#!/usr/bin/env python3
"""WSL経由通知確認テスト（スタンドアロン版）"""

import subprocess
import sys
from pathlib import Path


def check_windows_environment():
    """Windows/WSL環境チェック"""
    print("🪟 Windows/WSL環境チェック...")
    
    # WSL環境チェック
    try:
        with open("/proc/version", "r") as f:
            version_info = f.read().lower()
            if "microsoft" in version_info or "wsl" in version_info:
                print("✅ WSL環境検出（Windows上のLinux）")
                return True
    except FileNotFoundError:
        pass
    
    # Windows環境チェック
    try:
        result = subprocess.run(
            ["wsl.exe", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Windows環境でWSL利用可能")
            return True
        else:
            print("❌ Windows/WSL環境ではありません")
            return False
            
    except FileNotFoundError:
        print("❌ Windows/WSL環境ではありません")
        return False
    except Exception as e:
        print(f"❌ 環境チェックエラー: {e}")
        return False


def test_direct_notification():
    """直接通知テスト"""
    print("🔔 直接通知テスト...")
    
    project_root = Path(__file__).parent.parent
    
    test_script = '''
from src.docker_notifier import DockerNotifier
import logging
logging.basicConfig(level=logging.INFO)

notifier = DockerNotifier()
success = notifier.send_notification(
    "WSLテスト通知", 
    "WSL Kernel Watcher 通知機能テスト"
)

if success:
    print("✅ 通知送信成功")
else:
    print("❌ 通知送信失敗")
'''
    
    try:
        result = subprocess.run([
            "uv", "run", "python", "-c", test_script
        ], cwd=project_root, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(result.stdout)
            return "✅" in result.stdout
        else:
            print(f"❌ 通知テスト失敗: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 通知テストエラー: {e}")
        return False


if __name__ == "__main__":
    print("🔍 WSL経由通知テスト（スタンドアロン版）開始...")
    
    # Windows/WSL環境チェック
    if not check_windows_environment():
        print("\n⚠️ このテストはWindows/WSL環境でのみ実行可能です")
        print("純粋Linux環境では通知機能をテストできません")
        sys.exit(0)
    
    success = test_direct_notification()
    
    if success:
        print("\n🎉 WSL経由通知テスト成功")
        sys.exit(0)
    else:
        print("\n💥 WSL経由通知テスト失敗")
        sys.exit(1)