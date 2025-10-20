#!/usr/bin/env python3
"""WSL経由通知確認テスト（Windows環境専用）"""

import subprocess
import sys
from pathlib import Path


def test_wsl_access():
    """systemd監視サービス動作確認"""
    print("🐧 systemd監視サービス確認...")
    
    try:
        result = subprocess.run([
            "systemctl", "is-active", "wsl-kernel-watcher-monitor"
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip() == "active":
            print("✅ systemd監視サービス動作中")
            return True
        else:
            print(f"❌ systemd監視サービス停止中")
            return False
            
    except Exception as e:
        print(f"❌ systemd監視サービス確認エラー: {e}")
        return False


def test_powershell_execution():
    """ファイル監視システム経由通知テスト"""
    print("💻 ファイル監視システム経由通知テスト...")
    
    import time
    import os
    
    try:
        # テスト通知スクリプト作成
        timestamp = int(time.time() * 1000)
        script_path = f"/home/hiro/workspace/WSL-kernel-watcher/docker_notify_test_{timestamp}.sh"
        
        script_content = '''#!/bin/bash
/mnt/c/Windows/System32/wsl.exe -e /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "
\\$xml = @'
<toast>
    <visual>
        <binding template='ToastGeneric'>
            <text>テスト通知</text>
            <text>ファイル監視システムテスト</text>
        </binding>
    </visual>
</toast>
'@
\\$app = 'WSL.KernelWatcher'
\\$null = [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]
\\$null = [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime]
\\$doc = New-Object Windows.Data.Xml.Dom.XmlDocument
\\$doc.LoadXml(\\$xml)
\\$toast = New-Object Windows.UI.Notifications.ToastNotification(\\$doc)
\\$notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier(\\$app)
\\$notifier.Show(\\$toast)
"
'''
        
        with open(script_path, "w") as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        # ファイル監視システムが処理するまで待機
        time.sleep(3)
        
        # スクリプトが削除されたか確認（実行完了の証拠）
        if not os.path.exists(script_path):
            print("✅ ファイル監視システム経由通知成功")
            return True
        else:
            print("❌ ファイル監視システム未処理")
            # クリーンアップ
            if os.path.exists(script_path):
                os.remove(script_path)
            return False
            
    except Exception as e:
        print(f"❌ ファイル監視システムテストエラー: {e}")
        return False


def test_notification_system():
    """通知システムテスト（systemdログで判定）"""
    print("🔔 通知システムテスト...")
    
    import time
    
    project_root = Path(__file__).parent.parent
    
    test_script = '''
from src.docker_notifier import DockerNotifier
import logging
logging.basicConfig(level=logging.INFO)

notifier = DockerNotifier()
notifier.send_notification(
    "テスト通知", 
    "WSL Kernel Watcher通知テスト"
)
print("通知システム実行完了")
'''
    
    try:
        # Docker内部で通知システム実行
        result = subprocess.run([
            "docker-compose", "run", "--rm",
            "wsl-kernel-watcher",
            "uv", "run", "python", "-c", test_script
        ], cwd=project_root, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"❌ Docker実行失敗: {result.stderr}")
            return False
        
        # systemdログで実際の処理を確認
        time.sleep(3)
        log_result = subprocess.run([
            "sudo", "journalctl", "-u", "wsl-kernel-watcher-monitor", 
            "--since", "30 seconds ago", "--no-pager", "-n", "3"
        ], capture_output=True, text=True)
        
        if log_result.returncode == 0:
            log_output = log_result.stdout
            if "通知スクリプト検出" in log_output and "通知スクリプト実行完了・削除" in log_output:
                print("✅ 通知システム正常動作確認")
                return True
            else:
                print("❌ systemdログに通知処理が見つかりません")
                return False
        else:
            print("❌ systemdログ取得失敗")
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