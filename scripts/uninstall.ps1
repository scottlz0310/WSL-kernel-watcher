# WSL Kernel Watcher アンインストールスクリプト

param(
    [string]$InstallMethod = "",  # "uv", "pipx", または自動検出
    [switch]$RemoveConfig = $false,
    [switch]$Help = $false
)

function Show-Help {
    Write-Host "WSL Kernel Watcher アンインストールスクリプト" -ForegroundColor Green
    Write-Host ""
    Write-Host "使用方法:"
    Write-Host "  .\uninstall.ps1 [オプション]"
    Write-Host ""
    Write-Host "オプション:"
    Write-Host "  -InstallMethod <method>  インストール方法 ('uv', 'pipx', または空で自動検出)"
    Write-Host "  -RemoveConfig            設定ファイルとログも削除"
    Write-Host "  -Help                    このヘルプを表示"
    Write-Host ""
    Write-Host "例:"
    Write-Host "  .\uninstall.ps1                      # 自動検出してアンインストール"
    Write-Host "  .\uninstall.ps1 -InstallMethod pipx  # pipxからアンインストール"
    Write-Host "  .\uninstall.ps1 -RemoveConfig        # 設定ファイルも削除"
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Test-PipxInstallation {
    try {
        $pipxList = pipx list 2>&1
        return $pipxList -match "wsl-kernel-watcher"
    }
    catch {
        return $false
    }
}

function Test-UVInstallation {
    # uvでインストールされた場合、通常は特定のディレクトリに仮想環境がある
    return (Test-Path ".venv") -and (Test-Path "pyproject.toml")
}

function Detect-InstallMethod {
    Write-Host "インストール方法を検出しています..." -ForegroundColor Yellow
    
    if ((Test-Command "pipx") -and (Test-PipxInstallation)) {
        Write-Host "pipxでのインストールを検出しました。" -ForegroundColor Green
        return "pipx"
    }
    elseif (Test-UVInstallation) {
        Write-Host "uvでのインストールを検出しました。" -ForegroundColor Green
        return "uv"
    }
    else {
        Write-Host "インストール方法を自動検出できませんでした。" -ForegroundColor Yellow
        return ""
    }
}

function Uninstall-FromPipx {
    Write-Host "pipxからWSL Kernel Watcherをアンインストールしています..." -ForegroundColor Yellow
    
    try {
        pipx uninstall wsl-kernel-watcher
        Write-Host "pipxからのアンインストールが完了しました。" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "pipxからのアンインストールに失敗しました: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Uninstall-FromUV {
    Write-Host "uv環境からWSL Kernel Watcherをアンインストールしています..." -ForegroundColor Yellow
    
    try {
        # 仮想環境を削除
        if (Test-Path ".venv") {
            Remove-Item -Recurse -Force ".venv"
            Write-Host "仮想環境を削除しました。" -ForegroundColor Green
        }
        
        # ビルド成果物を削除
        if (Test-Path "dist") {
            Remove-Item -Recurse -Force "dist"
            Write-Host "ビルド成果物を削除しました。" -ForegroundColor Green
        }
        
        # キャッシュディレクトリを削除
        $cacheDirectories = @(".pytest_cache", ".mypy_cache", ".ruff_cache", "__pycache__")
        foreach ($dir in $cacheDirectories) {
            if (Test-Path $dir) {
                Remove-Item -Recurse -Force $dir
                Write-Host "キャッシュディレクトリ $dir を削除しました。" -ForegroundColor Green
            }
        }
        
        # カバレッジファイルを削除
        $coverageFiles = @(".coverage", "htmlcov")
        foreach ($file in $coverageFiles) {
            if (Test-Path $file) {
                Remove-Item -Recurse -Force $file
                Write-Host "カバレッジファイル $file を削除しました。" -ForegroundColor Green
            }
        }
        
        Write-Host "uv環境からのアンインストールが完了しました。" -ForegroundColor Green
        Write-Host "注意: プロジェクトディレクトリ自体は削除されていません。" -ForegroundColor Yellow
        return $true
    }
    catch {
        Write-Host "uv環境からのアンインストールに失敗しました: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Remove-ConfigFiles {
    Write-Host "設定ファイルとログを削除しています..." -ForegroundColor Yellow
    
    $filesToRemove = @()
    
    # ローカル設定ファイル
    if (Test-Path "config.toml") {
        $filesToRemove += "config.toml"
    }
    
    # AppDataディレクトリの設定とログ
    $appDataPath = "$env:APPDATA\wsl-kernel-watcher"
    if (Test-Path $appDataPath) {
        $filesToRemove += $appDataPath
    }
    
    # ローカルログファイル
    $logFiles = Get-ChildItem -Filter "*.log" -ErrorAction SilentlyContinue
    foreach ($logFile in $logFiles) {
        $filesToRemove += $logFile.FullName
    }
    
    if ($filesToRemove.Count -eq 0) {
        Write-Host "削除する設定ファイルやログが見つかりませんでした。" -ForegroundColor Yellow
        return $true
    }
    
    Write-Host "以下のファイル/ディレクトリを削除します:" -ForegroundColor Cyan
    foreach ($file in $filesToRemove) {
        Write-Host "  $file" -ForegroundColor White
    }
    
    $confirm = Read-Host "削除を続行しますか？ (y/N)"
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        try {
            foreach ($file in $filesToRemove) {
                if (Test-Path $file) {
                    Remove-Item -Recurse -Force $file
                    Write-Host "削除しました: $file" -ForegroundColor Green
                }
            }
            return $true
        }
        catch {
            Write-Host "設定ファイルの削除に失敗しました: $($_.Exception.Message)" -ForegroundColor Red
            return $false
        }
    }
    else {
        Write-Host "設定ファイルの削除をキャンセルしました。" -ForegroundColor Yellow
        return $true
    }
}

function Stop-RunningProcess {
    Write-Host "実行中のWSL Kernel Watcherプロセスを確認しています..." -ForegroundColor Yellow
    
    try {
        $processes = Get-Process -Name "*wsl-kernel-watcher*" -ErrorAction SilentlyContinue
        if ($processes) {
            Write-Host "実行中のプロセスが見つかりました:" -ForegroundColor Yellow
            foreach ($process in $processes) {
                Write-Host "  PID: $($process.Id), Name: $($process.ProcessName)" -ForegroundColor White
            }
            
            $confirm = Read-Host "これらのプロセスを終了しますか？ (y/N)"
            if ($confirm -eq "y" -or $confirm -eq "Y") {
                foreach ($process in $processes) {
                    $process.Kill()
                    Write-Host "プロセス $($process.Id) を終了しました。" -ForegroundColor Green
                }
            }
        }
        else {
            Write-Host "実行中のプロセスは見つかりませんでした。" -ForegroundColor Green
        }
        return $true
    }
    catch {
        Write-Host "プロセス確認中にエラーが発生しました: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# メイン処理
if ($Help) {
    Show-Help
    exit 0
}

Write-Host "WSL Kernel Watcher アンインストールスクリプト" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# 実行中のプロセスを停止
Stop-RunningProcess

# インストール方法の検出または指定
if ($InstallMethod -eq "") {
    $InstallMethod = Detect-InstallMethod
    if ($InstallMethod -eq "") {
        Write-Host "インストール方法を手動で指定してください:" -ForegroundColor Yellow
        Write-Host "1. pipx"
        Write-Host "2. uv"
        Write-Host "3. キャンセル"
        
        do {
            $choice = Read-Host "選択してください (1-3)"
            switch ($choice) {
                "1" { $InstallMethod = "pipx"; break }
                "2" { $InstallMethod = "uv"; break }
                "3" { 
                    Write-Host "アンインストールをキャンセルしました。" -ForegroundColor Yellow
                    exit 0
                }
                default { Write-Host "無効な選択です。1-3を入力してください。" -ForegroundColor Red }
            }
        } while ($InstallMethod -eq "")
    }
}

# アンインストール実行
$success = $false

switch ($InstallMethod) {
    "pipx" {
        if (-not (Test-Command "pipx")) {
            Write-Host "エラー: pipxがインストールされていません。" -ForegroundColor Red
            exit 1
        }
        $success = Uninstall-FromPipx
    }
    "uv" {
        $success = Uninstall-FromUV
    }
    default {
        Write-Host "エラー: 無効なインストール方法です。" -ForegroundColor Red
        Show-Help
        exit 1
    }
}

# 設定ファイルの削除
if ($success -and $RemoveConfig) {
    Remove-ConfigFiles
}

if ($success) {
    Write-Host ""
    Write-Host "アンインストールが正常に完了しました！" -ForegroundColor Green
    
    if (-not $RemoveConfig) {
        Write-Host ""
        Write-Host "注意: 設定ファイルとログは保持されています。" -ForegroundColor Cyan
        Write-Host "完全に削除したい場合は、-RemoveConfig オプションを使用してください。" -ForegroundColor Cyan
    }
    
    Write-Host ""
    Write-Host "WSL Kernel Watcherをご利用いただき、ありがとうございました。" -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "アンインストールに失敗しました。" -ForegroundColor Red
    Write-Host "エラーメッセージを確認し、手動で削除を行ってください。" -ForegroundColor Red
    exit 1
}