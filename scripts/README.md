# Scripts

このディレクトリには、WSL Kernel Watcherのインストール・開発環境セットアップ用のPowerShellスクリプトが含まれています。

## 開発者向けスクリプト

### setup-dev.ps1

開発環境をセットアップします。

```powershell
.\scripts\setup-dev.ps1
```

**機能**:
- pre-commitのインストール
- Gitフックの設定（コミット時・プッシュ時のチェック）
- NuGetパッケージの復元

**必要環境**:
- Python 3.8以降（pre-commit用）
- .NET 8.0 SDK

---

## エンドユーザー向けスクリプト

## install.ps1

WSL Kernel Watcherをタスクスケジューラに登録し、ユーザーログイン時に自動起動するように設定します。

### 機能

- タスクスケジューラへの自動登録
- 実行ファイルの自動検出
- ログイン時の自動起動設定
- トレイ最小化オプション
- 既存タスクの上書き確認
- インストール後の即時起動オプション

### 使用方法

#### 基本的な使い方

```powershell
# 実行ファイルを自動検出してインストール
.\install.ps1

# トレイに最小化して起動（推奨）
.\install.ps1 -StartMinimized
```

#### カスタムパスを指定

```powershell
# 特定の実行ファイルを指定
.\install.ps1 -ExePath "C:\MyApps\WSLKernelWatcher.WinUI3.exe"

# カスタムパス + トレイ最小化
.\install.ps1 -ExePath "C:\MyApps\WSLKernelWatcher.WinUI3.exe" -StartMinimized
```

#### ヘルプの表示

```powershell
Get-Help .\install.ps1 -Full
```

### パラメータ

- **ExePath** (オプション): 実行ファイルのパス。指定しない場合は自動検出されます。
- **StartMinimized** (スイッチ): 起動時にトレイに最小化します。

### 実行ファイルの検索順序

スクリプトは以下の順序で実行ファイルを検索します:

1. `winui3\WSLKernelWatcher.WinUI3\bin\x64\Release\net8.0-windows10.0.19041.0\`
2. `winui3\WSLKernelWatcher.WinUI3\bin\x64\Debug\net8.0-windows10.0.19041.0\`
3. `C:\Program Files\WSL Kernel Watcher\`
4. `%LOCALAPPDATA%\WSL Kernel Watcher\`

### タスク設定の詳細

登録されるタスクの設定:

- **タスク名**: WSL Kernel Watcher
- **トリガー**: ユーザーログイン時
- **実行アカウント**: 現在のユーザー
- **特権**: 制限付き（管理者権限不要）
- **バッテリー設定**: バッテリー使用時も動作
- **ネットワーク**: ネットワーク不要
- **再起動設定**: 異常終了時に3回まで自動再起動（1分間隔）

---

## uninstall.ps1

タスクスケジューラからWSL Kernel Watcherを削除します。

### 機能

- タスクスケジューラからの削除
- 実行中のプロセス停止オプション
- ユーザー設定の削除/保持選択
- 安全な削除確認

### 使用方法

#### 基本的な使い方

```powershell
# タスクを削除（設定削除の確認あり）
.\uninstall.ps1

# タスクを削除して設定を保持
.\uninstall.ps1 -KeepSettings
```

#### ヘルプの表示

```powershell
Get-Help .\uninstall.ps1 -Full
```

### パラメータ

- **KeepSettings** (スイッチ): ユーザー設定を保持します。指定しない場合は削除の確認が表示されます。

### 削除される項目

1. **タスクスケジューラ**:
   - "WSL Kernel Watcher" タスク

2. **実行中のプロセス** (オプション):
   - WSLKernelWatcher.WinUI3.exe

3. **ユーザー設定** (オプション):
   - `%LOCALAPPDATA%\WSLKernelWatcher\settings.json`
   - ログファイルなど

---

## トラブルシューティング

### スクリプトの実行ポリシーエラー

PowerShellスクリプトが実行できない場合:

```powershell
# 現在のユーザーのみに対して実行ポリシーを変更
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# または、一時的にバイパス
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

### タスクが起動しない

1. タスクスケジューラを開いて確認:
   ```powershell
   taskschd.msc
   ```

2. タスクのプロパティを確認し、実行履歴を確認

3. 手動でタスクを実行してエラーをチェック

### 実行ファイルが見つからない

1. プロジェクトをビルドしてください:
   ```powershell
   # Visual Studio Developer Command Prompt で実行
   msbuild winui3\WSLKernelWatcher.WinUI3\WSLKernelWatcher.WinUI3.csproj /p:Configuration=Release /p:Platform=x64
   ```

2. または、`-ExePath` パラメータで手動指定:
   ```powershell
   .\install.ps1 -ExePath "完全なパス\WSLKernelWatcher.WinUI3.exe"
   ```

### 管理者権限が必要ですか？

いいえ、これらのスクリプトは管理者権限不要です。現在のユーザーのタスクスケジューラにのみ登録されます。

---

## セキュリティ

- スクリプトは現在のユーザーのタスクスケジューラのみを変更します
- システム全体には影響しません
- 管理者権限は不要です
- 実行ファイルのパスは検証されます

## ライセンス

MIT License
