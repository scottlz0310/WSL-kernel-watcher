#!/usr/bin/env python3
"""完全フロー確認テスト（Docker→systemd→通知→クリーンアップ）"""

import os
import subprocess
import sys
import time
from pathlib import Path


def test_docker_to_notification_flow():
    """Docker→WSLホスト→systemd→通知→クリーンアップの完全フロー確認"""
    print("🔄 完全フロー確認テスト開始...")
    print("📋 Docker内部からWSLホスト側への通知フロー全体を確認します")

    project_root = Path(__file__).parent.parent

    try:
        # 1. Docker内部から通知システムを実行
        print("\n1️⃣ Docker内部から通知システム実行...")

        test_script = """
from src.docker_notifier import DockerNotifier
import logging
logging.basicConfig(level=logging.INFO)

notifier = DockerNotifier()
success = notifier.send_notification(
    "完全フローテスト", 
    "Docker→systemd→通知の完全フロー確認"
)

if success:
    print("✅ Docker通知システム実行成功")
else:
    print("❌ Docker通知システム実行失敗")
"""

        print("🐳 Dockerコンテナ内で通知システム実行中...")
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

        if result.returncode == 0:
            print("✅ Docker内部実行成功")
            # systemdログで実際の処理を後で確認するため、ここでは成功と判定
            print("📤 Docker通知システム実行成功（systemdログで確認予定）")
        else:
            print(f"❌ Docker内部実行失敗: {result.stderr}")
            return False

        # 2. systemdログでファイル検知・実行を確認
        print("\n2️⃣ systemdログでファイル検知・実行確認...")

        time.sleep(2)  # systemd処理待機

        log_result = subprocess.run(
            [
                "sudo",
                "journalctl",
                "-u",
                "wsl-kernel-watcher-monitor",
                "--since",
                "30 seconds ago",
                "--no-pager",
                "-n",
                "5",
            ],
            capture_output=True,
            text=True,
        )

        if log_result.returncode == 0:
            log_output = log_result.stdout
            if (
                "通知スクリプト検出" in log_output
                and "通知スクリプト実行完了・削除" in log_output
            ):
                print("✅ systemd検知・実行・削除確認")
                print("📝 ログ抜粋:")
                for line in log_output.split("\n")[-3:]:
                    if line.strip():
                        print(f"   {line}")
            else:
                print("❌ systemdログに期待する内容が見つかりません")
                print(f"📝 実際のログ: {log_output}")
                return False
        else:
            print(f"❌ systemdログ取得失敗: {log_result.stderr}")
            return False

        # 3. ホスト側にスクリプトファイルが残っていないことを確認
        print("\n3️⃣ クリーンアップ確認...")

        script_files = list(
            Path("/home/hiro/workspace/WSL-kernel-watcher").glob("docker_notify_*.sh")
        )
        if not script_files:
            print("✅ スクリプトファイル完全削除確認")
        else:
            print(f"❌ スクリプトファイルが残存: {script_files}")
            # 残存ファイルをクリーンアップ
            for file in script_files:
                file.unlink()
            return False

        # 4. クリック可能な通知でテスト
        print("\n4️⃣ クリック確認用通知送信...")

        click_test_script = """
from src.docker_notifier import DockerNotifier
import logging
logging.basicConfig(level=logging.INFO)

notifier = DockerNotifier()
success = notifier.send_notification(
    "クリックテスト - WSL Kernel Watcher", 
    "この通知をクリックしてGitHubページを開いてください"
)

if success:
    print("✅ クリック確認用通知送信成功")
else:
    print("❌ クリック確認用通知送信失敗")
"""

        print("🖱️ クリック確認用通知送信中...")
        click_result = subprocess.run(
            [
                "docker-compose",
                "run",
                "--rm",
                "wsl-kernel-watcher",
                "uv",
                "run",
                "python",
                "-c",
                click_test_script,
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if click_result.returncode != 0:
            print(f"❌ クリック確認用通知送信失敗: {click_result.stderr}")
            return False

        time.sleep(3)  # 通知処理待機

        print("\n📋 通知確認手順:")
        print(
            "   1. 'クリックテスト - WSL Kernel Watcher' ダイアログが表示されたか確認"
        )
        print("   2. ダイアログの 'OK' ボタンをクリック")
        print("   3. 通知が表示されない場合は 'n' を入力")
        print("   ※ 現在はMessageBoxダイアログ形式（Toast通知ではありません）")

        response = (
            input(
                "\n❓ 通知ダイアログが表示され、OKボタンをクリックできましたか？ (y/N): "
            )
            .strip()
            .lower()
        )

        if response == "y":
            print("🎉 完全フロー確認テスト成功！")
            print("✅ Docker→systemd→通知→ユーザー確認 の全フローが正常動作")
            return True
        else:
            print("❌ 通知に問題があります")
            print("\n🔧 トラブルシューティング実行...")
            troubleshoot_notification_issues()
            return False

    except subprocess.TimeoutExpired:
        print("⏰ Docker実行タイムアウト")
        return False
    except Exception as e:
        print(f"❌ 完全フロー確認テストエラー: {e}")
        return False


def check_prerequisites():
    """前提条件確認"""
    print("🔧 前提条件確認...")

    # systemd監視サービス確認
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "wsl-kernel-watcher-monitor"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0 and result.stdout.strip() == "active":
            print("✅ systemd監視サービス動作中")
        else:
            print("❌ systemd監視サービス停止中")
            return False
    except Exception as e:
        print(f"❌ systemd確認エラー: {e}")
        return False

    # Docker環境確認
    try:
        result = subprocess.run(
            ["docker-compose", "ps", "-q", "wsl-kernel-watcher"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        if result.stdout.strip():
            print("✅ Dockerコンテナ動作中")
        else:
            print("❌ Dockerコンテナ未起動")
            return False
    except Exception as e:
        print(f"❌ Docker確認エラー: {e}")
        return False

    return True


def troubleshoot_notification_issues():
    """通知問題のトラブルシューティング"""
    print("\n🔍 通知問題の診断中...")

    # 1. Windows通知設定確認
    print("\n1️⃣ Windows通知設定確認...")
    try:
        timestamp = int(time.time() * 1000)
        script_path = (
            f"/home/hiro/workspace/WSL-kernel-watcher/docker_notify_diag_{timestamp}.sh"
        )

        diag_script = """#!/bin/bash
/mnt/c/Windows/System32/wsl.exe -e /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "
# 通知設定確認
Write-Host '=== Windows通知設定診断 ==='

# フォーカスアシスト確認
\\$focusAssist = Get-ItemProperty -Path 'HKCU:\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\CloudStore\\\\Store\\\\Cache\\\\DefaultAccount' -Name '*QuietHours*' -ErrorAction SilentlyContinue
if (\\$focusAssist) {
    Write-Host '⚠️ フォーカスアシストが有効の可能性があります'
} else {
    Write-Host '✅ フォーカスアシスト設定確認'
}

# 通知とアクション設定確認
Write-Host '📋 通知設定を確認してください:'
Write-Host '   設定 > システム > 通知とアクション'
Write-Host '   アプリからの通知を取得する: オン'
Write-Host '   集中モード: オフ'

# Toast通知テスト
Write-Host '\n🔔 Toast通知テスト送信中...'
\\$xml = @'
<toast>
    <visual>
        <binding template='ToastGeneric'>
            <text>診断テスト - WSL Kernel Watcher</text>
            <text>このToast通知が表示されれば設定正常</text>
        </binding>
    </visual>
</toast>
'@
\\$app = 'WSL.KernelWatcher.Diagnostic'
\\$null = [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]
\\$null = [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime]
\\$doc = New-Object Windows.Data.Xml.Dom.XmlDocument
\\$doc.LoadXml(\\$xml)
\\$toast = New-Object Windows.UI.Notifications.ToastNotification(\\$doc)
\\$notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier(\\$app)
\\$notifier.Show(\\$toast)
Write-Host '✅ Toast通知送信完了'
"
"""

        with open(script_path, "w") as f:
            f.write(diag_script)

        os.chmod(script_path, 0o755)
        time.sleep(3)

        if not os.path.exists(script_path):
            print("✅ 診断スクリプト実行完了")

            # 診断通知の確認
            diag_response = (
                input(
                    "\n❓ '診断テスト - WSL Kernel Watcher' Toast通知が表示されましたか？ (y/N): "
                )
                .strip()
                .lower()
            )

            if diag_response == "y":
                print("✅ Toast通知システムは正常動作 - アプリ固有の問題の可能性")
            else:
                print("❌ Windows通知設定に問題あり - 下記対処法を実行してください")
        else:
            print("❌ 診断スクリプト未処理")
            os.remove(script_path)

    except Exception as e:
        print(f"❌ 診断エラー: {e}")

    # 2. 推奨対処法
    print("\n💡 Windows通知設定確認手順:")
    print("   1. Windowsキー + I で設定を開く")
    print("   2. 'システム' > '通知とアクション' をクリック")
    print("   3. 以下を確認/変更:")
    print("      ✅ '通知' をオン")
    print("      ✅ 'アプリからの通知を取得する' をオン")
    print("      ❌ '集中モード' をオフ")
    print("   4. タスクバー右下の通知アイコンをクリック")
    print("   5. '通知の管理' > 'すべての通知を表示' をオン")
    print("\n🔄 再テスト手順:")
    print("   1. 上記設定変更後、WSLターミナルを最小化")
    print("   2. 'make test-interactive' で個別テスト")
    print("   3. 問題が続く場合はWindows再起動")


if __name__ == "__main__":
    print("🔄 完全フロー確認テスト開始")
    print("=" * 60)
    print("📋 このテストは以下の完全フローを確認します：")
    print(
        "   Docker内部 → ファイル作成 → systemd検知 → 通知実行 → クリック確認 → クリーンアップ"
    )
    print("⚠️ 通知が表示されない場合は自動診断を実行します")
    print("=" * 60)

    # 前提条件確認
    if not check_prerequisites():
        print("\n❌ 前提条件が満たされていません")
        sys.exit(1)

    # 完全フロー確認
    success = test_docker_to_notification_flow()

    print("\n" + "=" * 60)
    if success:
        print("🎉 完全フロー確認テスト成功")
        print("✅ Docker→systemd→通知→クリーンアップの全フローが正常動作")
        sys.exit(0)
    else:
        print("💥 完全フロー確認テスト失敗")
        print("🔧 システム設定を確認してください")
        sys.exit(1)
