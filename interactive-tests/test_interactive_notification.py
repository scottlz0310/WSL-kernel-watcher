#!/usr/bin/env python3
"""インタラクティブ通知テスト（通知クリック確認付き）"""

import subprocess
import sys
import time
import os
from pathlib import Path


def test_interactive_notification():
    """インタラクティブ通知テスト"""
    print("🔔 インタラクティブ通知テスト開始...")
    print("📋 このテストでは実際に通知をクリックして確認します")
    
    # ユーザー確認
    response = input("\n❓ 通知テストを実行しますか？ (y/N): ").strip().lower()
    if response != 'y':
        print("⏭️ テストをスキップしました")
        return True
    
    try:
        # クリック可能な通知スクリプト作成
        timestamp = int(time.time() * 1000)
        script_path = f"/home/hiro/workspace/WSL-kernel-watcher/docker_notify_interactive_{timestamp}.sh"
        
        # GitHub リリースページを開く通知
        script_content = '''#!/bin/bash
/mnt/c/Windows/System32/wsl.exe -e /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "
\\$xml = @'
<toast activationType='protocol' launch='https://github.com/microsoft/WSL2-Linux-Kernel/releases'>
    <visual>
        <binding template='ToastGeneric'>
            <text>WSL2カーネル更新通知</text>
            <text>新しいバージョンが利用可能です</text>
            <text>クリックしてリリースページを開く</text>
        </binding>
    </visual>
    <actions>
        <action content='リリースページを開く' arguments='https://github.com/microsoft/WSL2-Linux-Kernel/releases' activationType='protocol'/>
        <action content='後で確認' arguments='dismiss' activationType='system'/>
    </actions>
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
        
        print("🚀 通知を送信中...")
        print("📱 Windows通知エリアを確認してください")
        print("🖱️ 通知をクリックするとGitHubリリースページが開きます")
        
        # ファイル監視システムが処理するまで待機
        time.sleep(3)
        
        # スクリプトが削除されたか確認
        if not os.path.exists(script_path):
            print("✅ 通知送信完了")
            
            # ユーザーからの確認を待つ
            print("\n⏳ 通知の確認をお待ちしています...")
            print("📋 以下を確認してください：")
            print("   1. Windows通知が表示されたか")
            print("   2. 通知をクリックしてGitHubページが開いたか")
            
            response = input("\n❓ 通知は正常に表示され、クリックできましたか？ (y/N): ").strip().lower()
            
            if response == 'y':
                print("🎉 インタラクティブ通知テスト成功！")
                return True
            else:
                print("❌ 通知に問題があります")
                print("💡 Windows通知設定を確認してください")
                return False
        else:
            print("❌ ファイル監視システムが動作していません")
            # クリーンアップ
            if os.path.exists(script_path):
                os.remove(script_path)
            return False
            
    except Exception as e:
        print(f"❌ インタラクティブ通知テストエラー: {e}")
        return False


def test_notification_settings():
    """Windows通知設定確認"""
    print("⚙️ Windows通知設定確認...")
    
    try:
        # Windows通知設定確認スクリプト
        timestamp = int(time.time() * 1000)
        script_path = f"/home/hiro/workspace/WSL-kernel-watcher/docker_notify_settings_{timestamp}.sh"
        
        script_content = '''#!/bin/bash
/mnt/c/Windows/System32/wsl.exe -e /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "
# 通知設定確認
\\$notificationSettings = Get-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings' -ErrorAction SilentlyContinue
if (\\$notificationSettings) {
    Write-Host '✅ Windows通知設定: 有効'
} else {
    Write-Host '⚠️ Windows通知設定: 確認できません'
}

# フォーカスアシスト確認
\\$focusAssist = Get-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\Cache\\DefaultAccount' -ErrorAction SilentlyContinue
Write-Host '📋 フォーカスアシスト設定を確認してください'
"
'''
        
        with open(script_path, "w") as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        # ファイル監視システムが処理するまで待機
        time.sleep(3)
        
        if not os.path.exists(script_path):
            print("✅ 通知設定確認完了")
            return True
        else:
            print("❌ 設定確認失敗")
            if os.path.exists(script_path):
                os.remove(script_path)
            return False
            
    except Exception as e:
        print(f"❌ 通知設定確認エラー: {e}")
        return False


def check_systemd_service():
    """systemd監視サービス確認"""
    print("🔧 systemd監視サービス確認...")
    
    try:
        result = subprocess.run([
            "systemctl", "is-active", "wsl-kernel-watcher-monitor"
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip() == "active":
            print("✅ systemd監視サービス動作中")
            return True
        else:
            print("❌ systemd監視サービス停止中")
            print("💡 'sudo systemctl start wsl-kernel-watcher-monitor' で開始してください")
            return False
            
    except Exception as e:
        print(f"❌ systemd監視サービス確認エラー: {e}")
        return False


if __name__ == "__main__":
    print("🎯 インタラクティブ通知テスト開始")
    print("=" * 60)
    
    # 前提条件確認
    if not check_systemd_service():
        print("\n❌ systemd監視サービスが必要です")
        sys.exit(1)
    
    success = True
    
    # 通知設定確認
    success &= test_notification_settings()
    
    # インタラクティブ通知テスト
    success &= test_interactive_notification()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 インタラクティブ通知テスト完了")
        print("✅ 通知システムが正常に動作しています")
        sys.exit(0)
    else:
        print("💥 インタラクティブ通知テスト失敗")
        print("🔧 通知設定を確認してください")
        sys.exit(1)