# WSL Kernel Watcher インストールガイド

このドキュメントでは、WSL Kernel Watcherの詳細なインストール手順を説明します。

## 目次

1. [前提条件](#前提条件)
2. [インストール方法](#インストール方法)
3. [設定](#設定)
4. [実行](#実行)
5. [アンインストール](#アンインストール)
6. [トラブルシューティング](#トラブルシューティング)

## 前提条件

### 必須要件

- **Windows 10/11**: Windows 10 バージョン 1903 以降、または Windows 11
- **Python 3.9以上**: [Python公式サイト](https://www.python.org/downloads/)からダウンロード
- **WSL2**: Microsoft Store または `wsl --install` コマンドでインストール

### 推奨要件

- **PowerShell 5.1以上**: Windows 10/11に標準搭載
- **Git**: [Git公式サイト](https://git-scm.com/downloads)からダウンロード

### 前提条件の確認

PowerShellで以下のコマンドを実行して、前提条件を確認してください：

```powershell
# Python バージョン確認
python --version

# WSL 確認
wsl --version

# PowerShell バージョン確認
$PSVersionTable.PSVersion
```

## インストール方法

### 方法1: 自動インストールスクリプト（推奨）

最も簡単な方法です。PowerShellスクリプトが自動的に環境を設定します。

```powershell
# リポジトリをクローン
git clone https://github.com/wsl-kernel-watcher/wsl-kernel-watcher.git
cd wsl-kernel-watcher

# インストールスクリプトを実行
.\scripts\install.ps1
```

#### インストールスクリプトの動作

PowerShell スクリプトでは次の処理を自動化します。

1. Python / WSL / uv または pipx の存在を確認し、必要に応じて導入を案内します。
2. `-InstallMethod uv` の場合は、プロジェクト一式を指定フォルダにコピーして `.venv` を作成し、`uv sync` で依存関係を解決します。
3. `-Dev` を指定すると開発用依存関係と pre-commit フックを追加でセットアップします。
4. `config.toml` が存在しない場合は `config.template.toml` から自動生成します。
5. 完了後に実行方法と設定ファイルのパスを表示します。

#### インストール先フォルダを指定する (uv)

`-InstallPath` オプションを使うと、リポジトリとは別のディレクトリに本番用のコピーを展開できます。

```powershell
.\scripts\install.ps1 -InstallMethod uv -InstallPath "C:\Apps\WSLKernelWatcher"
```

- フォルダが存在しない場合は自動作成されます。
- 指定したディレクトリにプロジェクトファイルと `.venv` が配置され、`config.toml` もそこに生成されます。
- パスには `~` や `%PROGRAMDATA%` などの環境変数を利用できます。
- 以降は `uv run wsl-kernel-watcher` でインストール先から直接起動できます。

#### pipx でインストールした場合

`pipx` を選択した場合はユーザーごとの pipx 管理ディレクトリにインストールされ、設定ファイルは `%APPDATA%\wsl-kernel-watcher\config.toml` に作成されます。

#### スクリプトオプション

```powershell
# uvを使用してインストール（デフォルト）
.\scripts\install.ps1 -InstallMethod uv

# pipxを使用してインストール
.\scripts\install.ps1 -InstallMethod pipx

# 開発環境としてセットアップ
.\scripts\install.ps1 -Dev

# ヘルプを表示
.\scripts\install.ps1 -Help
```

### 方法2: uvを使用した手動インストール

#### Step 1: uvのインストール

```powershell
# uvをインストール
irm https://astral.sh/uv/install.ps1 | iex

# パスを更新（新しいPowerShellセッションを開くか、以下を実行）
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "User") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "Machine")

# インストール確認
uv --version
```

#### Step 2: プロジェクトのセットアップ

```powershell
# リポジトリをクローン
git clone https://github.com/wsl-kernel-watcher/wsl-kernel-watcher.git
cd wsl-kernel-watcher

# 仮想環境を作成し、依存関係をインストール
uv sync

# 設定ファイルを作成
Copy-Item config.template.toml config.toml
```

### 方法3: pipxを使用したグローバルインストール

#### Step 1: pipxのインストール

```powershell
# pipxをインストール
python -m pip install --user pipx
python -m pipx ensurepath

# 新しいPowerShellセッションを開くか、パスを更新
refreshenv  # Chocolateyがインストールされている場合
# または新しいPowerShellウィンドウを開く

# インストール確認
pipx --version
```

#### Step 2: WSL Kernel Watcherのインストール

```powershell
# GitHubから直接インストール
pipx install git+https://github.com/wsl-kernel-watcher/wsl-kernel-watcher.git

# または、ローカルディレクトリからインストール
git clone https://github.com/wsl-kernel-watcher/wsl-kernel-watcher.git
cd wsl-kernel-watcher
pipx install .
```

### 方法4: 開発環境セットアップ

開発に参加する場合や、ソースコードを変更したい場合：

```powershell
# リポジトリをクローン
git clone https://github.com/wsl-kernel-watcher/wsl-kernel-watcher.git
cd wsl-kernel-watcher

# 開発用依存関係をインストール
uv sync --extra dev

# pre-commitフックをセットアップ
uv run pre-commit install

# 設定ファイルを作成
Copy-Item config.template.toml config.toml
```

## 設定

### 設定ファイルの作成

初回実行時に、アプリケーションは自動的に `config.toml` ファイルを作成します。手動で作成する場合：

```powershell
# テンプレートから設定ファイルを作成
Copy-Item config.template.toml config.toml
```

### 設定項目

`config.toml` ファイルを編集して、動作をカスタマイズできます：

```toml
# チェック間隔（分）
check_interval_minutes = 30

# 監視対象リポジトリ
repository_url = "microsoft/WSL2-Linux-Kernel"

# ビルドアクション有効化
enable_build_action = false

# 通知機能有効化
notification_enabled = true

# ログレベル
log_level = "INFO"
```

### 設定項目の詳細

| 項目 | デフォルト値 | 説明 |
|------|-------------|------|
| `execution_mode` | "continuous" | 実行モード（"continuous": 常駐, "oneshot": ワンショット） |
| `check_interval_minutes` | 30 | GitHub APIをチェックする間隔（分） |
| `repository_url` | "microsoft/WSL2-Linux-Kernel" | 監視対象のGitHubリポジトリ |
| `enable_build_action` | false | 通知クリック時にビルドスクリプトを実行するか |
| `notification_enabled` | true | Windowsトースト通知を表示するか |
| `log_level` | "INFO" | ログレベル（DEBUG, INFO, WARNING, ERROR） |

## 実行

### uvでインストールした場合

```powershell
# プロジェクトディレクトリで実行（常駐モード）
cd wsl-kernel-watcher
uv run wsl-kernel-watcher

# または
uv run python -m src.main

# ワンショットモード（config.tomlでexecution_mode = "oneshot"に設定）
uv run wsl-kernel-watcher  # 一度だけチェックして終了
```

### pipxでインストールした場合

```powershell
# どこからでも実行可能（常駐モード）
wsl-kernel-watcher

# または短縮形
wkw

# ワンショットモード（config.tomlでexecution_mode = "oneshot"に設定）
wsl-kernel-watcher  # CI/CDやスケジュールタスクでの利用に最適
```

### バックグラウンド実行

アプリケーションをバックグラウンドで実行する場合：

```powershell
# PowerShellジョブとして実行
Start-Job -ScriptBlock { uv run wsl-kernel-watcher }

# または、タスクスケジューラーに登録（推奨）
# Windows + R → taskschd.msc で開く
```

## アンインストール

### 自動アンインストールスクリプト

```powershell
# プロジェクトディレクトリで実行
.\scripts\uninstall.ps1

# 設定ファイルとログも削除
.\scripts\uninstall.ps1 -RemoveConfig

# インストール方法を指定
.\scripts\uninstall.ps1 -InstallMethod pipx
```

### 手動アンインストール

#### uvでインストールした場合

```powershell
cd wsl-kernel-watcher

# 仮想環境を削除
Remove-Item -Recurse -Force .venv

# プロジェクトディレクトリを削除（オプション）
cd ..
Remove-Item -Recurse -Force wsl-kernel-watcher
```

#### pipxでインストールした場合

```powershell
# pipxからアンインストール
pipx uninstall wsl-kernel-watcher

# 設定ファイルを削除（オプション）
Remove-Item -Recurse -Force "$env:APPDATA\wsl-kernel-watcher"
```

## トラブルシューティング

### よくある問題

#### 1. PowerShell実行ポリシーエラー

```powershell
# エラー: このシステムではスクリプトの実行が無効になっています
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. Python が見つからない

```powershell
# Microsoft Store版Pythonをインストール
# または python.org からダウンロード

# パスの確認
$env:PATH -split ';' | Where-Object { $_ -like '*Python*' }
```

#### 3. WSL が見つからない

```powershell
# WSL2をインストール
wsl --install

# または Microsoft Store から Ubuntu をインストール
```

#### 4. 通知が表示されない

- Windows 10/11の通知設定を確認
- フォーカスアシスト（集中モード）を無効化
- アプリケーションの通知許可を確認

#### 5. GitHub API レート制限

- Personal Access Token を設定（オプション）
- チェック間隔を長くする（60分以上推奨）

### ログの確認

```powershell
# ログファイルの場所
# uvインストール: プロジェクトディレクトリ
# pipxインストール: %APPDATA%\wsl-kernel-watcher\logs

# ログレベルをDEBUGに変更して詳細情報を取得
# config.toml で log_level = "DEBUG" に設定
```

### サポート

問題が解決しない場合：

1. [GitHub Issues](https://github.com/wsl-kernel-watcher/wsl-kernel-watcher/issues) で既存の問題を検索
2. 新しいIssueを作成（ログファイルとシステム情報を含める）
3. [README.md](README.md) の追加情報を確認

### システム情報の収集

問題報告時に以下の情報を含めてください：

```powershell
# システム情報
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, TotalPhysicalMemory

# Python バージョン
python --version

# WSL バージョン
wsl --version

# PowerShell バージョン
$PSVersionTable.PSVersion

# インストール方法
# uv --version または pipx --version
```