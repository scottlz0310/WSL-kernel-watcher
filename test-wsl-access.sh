#!/bin/bash
# Docker Desktop for Windowsでwsl.exeアクセステスト

echo "=== WSL.exe アクセステスト ==="

# 1. wsl.exeが存在するか確認
if command -v wsl.exe &> /dev/null; then
    echo "✅ wsl.exe が見つかりました"
    which wsl.exe
else
    echo "❌ wsl.exe が見つかりません"
    echo "Docker Desktop for WindowsのWSL2統合を確認してください"
    exit 1
fi

# 2. wsl.exe経由でコマンド実行テスト
echo ""
echo "=== Windows側でコマンド実行テスト ==="
if wsl.exe -e echo "Test from container"; then
    echo "✅ wsl.exe経由でコマンド実行成功"
else
    echo "❌ wsl.exe経由でコマンド実行失敗"
    exit 1
fi

# 3. PowerShell実行テスト
echo ""
echo "=== PowerShell実行テスト ==="
if wsl.exe -e powershell.exe -Command "Write-Host 'PowerShell Test OK'"; then
    echo "✅ PowerShell実行成功"
else
    echo "❌ PowerShell実行失敗"
    exit 1
fi

echo ""
echo "=== 全てのテストが成功しました！ ==="
echo "このDocker環境ではWindows Toast通知が動作します"