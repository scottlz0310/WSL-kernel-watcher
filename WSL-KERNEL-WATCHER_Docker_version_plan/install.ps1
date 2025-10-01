# Windows Notification Server インストールスクリプト

Write-Host "Installing Windows Notification Server..." -ForegroundColor Green

# BurntToast モジュールのインストール
if (!(Get-Module -ListAvailable -Name BurntToast)) {
    Write-Host "Installing BurntToast module..." -ForegroundColor Yellow
    Install-Module -Name BurntToast -Force -Scope CurrentUser
    Write-Host "BurntToast module installed successfully" -ForegroundColor Green
} else {
    Write-Host "BurntToast module already installed" -ForegroundColor Green
}

# Python依存関係は不要（標準ライブラリのみ使用）

# サービス登録用バッチファイル作成
$batchContent = @"
@echo off
cd /d "%~dp0"
python notification_server.py
pause
"@

$batchContent | Out-File -FilePath "start_notification_server.bat" -Encoding ASCII

Write-Host "Installation completed!" -ForegroundColor Green
Write-Host "Run 'start_notification_server.bat' to start the notification server" -ForegroundColor Cyan