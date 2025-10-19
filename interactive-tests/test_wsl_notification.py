#!/usr/bin/env python3
"""WSL経由通知確認テスト（Windows環境専用）"""

import subprocess
import sys
from pathlib import Path


def test_wsl_access():
    """WSLアクセステスト"""
    print("🐧 WSLアクセステスト開始...")
    
    project_root = Path(__file__).parent.parent
    
    # コンテナ名を動的に取得
    try:
        container_result = subprocess.run([
            "docker-compose", "ps", "-q", "wsl-kernel-watcher"
        ], cwd=project_root, capture_output=True, text=True)
        
        container_id = container_result.stdout.strip()
        if not container_id:
            print("❌ コンテナが起動していません")
            return False
    
        result = subprocess.run([
            "docker", "exec", container_id,
            "wsl.exe", "-e", "echo", "WSL接続テスト"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ WSLアクセス成功")
            print(f"📤 出力: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ WSLアクセス失敗: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ WSLアクセスタイムアウト")
        return False
    except Exception as e:
        print(f"❌ WSLアクセスエラー: {e}")
        return False


def test_powershell_execution():
    """PowerShell実行テスト"""
    print("💻 PowerShell実行テスト...")
    
    project_root = Path(__file__).parent.parent
    
    # コンテナ名を動的に取得
    try:
        container_result = subprocess.run([
            "docker-compose", "ps", "-q", "wsl-kernel-watcher"
        ], cwd=project_root, capture_output=True, text=True)
        
        container_id = container_result.stdout.strip()
        if not container_id:
            print("❌ コンテナが起動していません")
            return False
    
        result = subprocess.run([
            "docker", "exec", container_id,
            "wsl.exe", "-e", "powershell.exe", "-Command", "Write-Host 'PowerShellテスト成功'"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ PowerShell実行成功")
            print(f"📤 出力: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ PowerShell実行失敗: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ PowerShell実行エラー: {e}")
        return False


def test_notification_system():
    """通知システムテスト"""
    print("🔔 通知システムテスト...")
    
    project_root = Path(__file__).parent.parent
    
    test_script = '''
from src.docker_notifier import DockerNotifier
import logging
logging.basicConfig(level=logging.INFO)

notifier = DockerNotifier()
success = notifier.send_notification(
    "テスト通知", 
    "WSL Kernel Watcher通知テスト"
)

if success:
    print("✅ 通知送信成功")
else:
    print("❌ 通知送信失敗")
'''
    
    try:
        result = subprocess.run([
            "docker-compose", "run", "--rm",
            "wsl-kernel-watcher",
            "uv", "run", "python", "-c", test_script
        ], cwd=project_root, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(result.stdout)
            return "✅" in result.stdout
        else:
            print(f"❌ 通知システムテスト失敗: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 通知システムテストエラー: {e}")
        return False


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


if __name__ == "__main__":
    print("🔍 WSL経由通知テスト開始...")
    
    # Windows環境チェック
    if not check_windows_environment():
        print("\n⚠️ このテストはWindows/WSL環境でのみ実行可能です")
        print("Linux��境では通知機能をテストできません")
        sys.exit(0)
    
    success = True
    
    success &= test_wsl_access()
    success &= test_powershell_execution()
    success &= test_notification_system()
    
    if success:
        print("\n🎉 WSL経由通知テスト完了")
        sys.exit(0)
    else:
        print("\n💥 WSL経由通知テスト失敗")
        sys.exit(1)