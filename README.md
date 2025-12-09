# WSL Kernel Watcher
WSL Kernel Watcherは、Windows上でWSL（Windows Subsystem for Linux）のカーネルバージョンを監視し、更新があった場合に通知を行う常駐型軽量アプリケーションです。

## 機能

- WSLカーネルバージョンの定期監視
- カーネル更新時のトースト通知
- ログファイルへの記録

## WinUI3版

### 必要環境

- Windows 10 (19041) 以降
- .NET 8.0 SDK
- Visual Studio 2022/2026 (WinUI3ワークロード含む)
- Windows App SDK 1.7

### ビルド方法

#### Visual Studioから
1. `winui3/WSLKernelWatcher.WinUI3.sln` をVisual Studioで開く
2. 構成を `Release` / `x64` に設定
3. ビルド → ソリューションのビルド (`Ctrl+Shift+B`)

#### コマンドラインから（VS Developer Command Prompt）
```powershell
# VS2026のMSBuildを使用
$vswhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
$msbuild = & $vswhere -latest -prerelease -requires Microsoft.Component.MSBuild -find "MSBuild\**\Bin\MSBuild.exe" | Select-Object -First 1
& $msbuild winui3\WSLKernelWatcher.WinUI3\WSLKernelWatcher.WinUI3.csproj /p:Configuration=Release /p:Platform=x64
```

> **注意:** `dotnet build` は WinUI3 に必要な MSBuild タスクが不足しているため使用できません。

### 起動方法

```powershell
# ビルド後の実行ファイルを起動
.\winui3\WSLKernelWatcher.WinUI3\bin\x64\Release\net8.0-windows10.0.19041.0\WSLKernelWatcher.WinUI3.exe
```

または、Visual Studioから `F5` でデバッグ実行できます。

## ライセンス

MIT License
