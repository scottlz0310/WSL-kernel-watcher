# WSLカーネル安定版リリース監視ツール

> **⚠️ このリポジトリはアーカイブ化されました**  
> 機能は [Mcp-Docker/github_release_watcher](https://github.com/scottlz0310/Mcp-Docker) に移行しました。  
> 詳細は [ARCHIVE_NOTICE.md](ARCHIVE_NOTICE.md) をご確認ください。

[![CI](https://github.com/scottlz0310/WSL-kernel-watcher/workflows/CI/badge.svg)](https://github.com/scottlz0310/WSL-kernel-watcher/actions)
[![codecov](https://codecov.io/gh/scottlz0310/WSL-kernel-watcher/branch/main/graph/badge.svg)](https://codecov.io/gh/scottlz0310/WSL-kernel-watcher)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Microsoft公式のWSL2 Linuxカーネルリポジトリ（microsoft/WSL2-Linux-Kernel）を監視し、新しい安定版リリースが公開された際にWindowsトースト通知でユーザーに知らせる常駐型アプリケーションです。

## 機能

- GitHub APIを使用したWSL2カーネルリリースの自動監視
- プレリリース（RC版、プレビュー版）の除外
- 現在のWSLカーネルバージョンとの比較
- Windowsトースト通知による更新通知
- **🆕 ワンショットモード**: 一度だけチェックして終了（CI/CDやスケジュールタスク向け）
- タスクトレイでの常駐動作
- 設定ファイルによるカスタマイズ
- 包括的なログ機能

## 必要環境

- Windows 10/11
- Python 3.9以上
- WSL2がインストールされていること

## インストール

### 方法0: install.ps1 を使う (Windows)

```powershell
.\scripts\install.ps1
```

PowerShell スクリプトは uv / pipx の確認、`.venv` の作成、`config.toml` の生成まで自動化します。`-InstallPath` を指定すると、本番用に別フォルダへ展開できます。

```powershell
.\scripts\install.ps1 -InstallMethod uv -InstallPath "C:\Apps\WSLKernelWatcher"
```

`pipx` を選んだ場合の設定ファイルは `%APPDATA%\wsl-kernel-watcher\config.toml` に作成されます。

### 方法1: uvを使用したインストール（推奨）

#### 前提条件
- [uv](https://docs.astral.sh/uv/)がインストールされていること

```powershell
# uvのインストール（未インストールの場合）
irm https://astral.sh/uv/install.ps1 | iex
```

#### インストール手順

```powershell
# リポジトリをクローン
git clone https://github.com/scottlz0310/WSL-kernel-watcher.git
cd WSL-kernel-watcher

# 仮想環境を作成し、依存関係をインストール
uv sync

# アプリケーションを実行
uv run wsl-kernel-watcher
```

### 方法2: pipxを使用したグローバルインストール

#### 前提条件
- Python 3.9以上
- [pipx](https://pipx.pypa.io/)がインストールされていること

```powershell
# pipxのインストール（未インストールの場合）
python -m pip install --user pipx
python -m pipx ensurepath
```

#### インストール手順

```powershell
# GitHubから直接インストール
pipx install git+https://github.com/scottlz0310/WSL-kernel-watcher.git

# または、ローカルディレクトリからインストール
cd WSL-kernel-watcher
pipx install .

# アプリケーションを実行
wsl-kernel-watcher
```

### 方法3: 開発環境セットアップ

```powershell
# リポジトリをクローン
git clone https://github.com/scottlz0310/WSL-kernel-watcher.git
cd WSL-kernel-watcher

# 仮想環境を作成
uv venv

# 開発用依存関係をインストール
uv sync --group dev

# pre-commitフックをセットアップ
uv run pre-commit install

# アプリケーションを実行
uv run python -m src.main
```

## 使用方法

### 基本的な実行

```powershell
# 常駐モード（デフォルト）
uv run python -m src.main

# または
uv run wsl-kernel-watcher
```

### ワンショットモード 🆕

一度だけチェックして終了するモードです。CI/CDパイプラインやスケジュールタスクでの利用に適しています。

```powershell
# config.tomlでexecution_mode = "oneshot"に設定して実行
uv run wsl-kernel-watcher

# または直接実行（設定ファイルがワンショットモードに設定されている場合）
python -m src.main
```

### 設定

`config.toml`ファイルを編集して動作をカスタマイズできます：

```toml
[general]
# 実行モード: "continuous" (常駐) または "oneshot" (ワンショット)
execution_mode = "continuous"  # または "oneshot"

# チェック間隔（分）
check_interval_minutes = 30

# 監視対象リポジトリ
repository_url = "microsoft/WSL2-Linux-Kernel"

[notification]
# 通知機能の有効化
enabled = true

[notification.click_action]
# ビルドアクションの有効化
enable_build_action = false

[logging]
# ログレベル
level = "INFO"
```

#### ワンショットモード設定例

CI/CDパイプラインやスケジュールタスクでの利用時：

```toml
[general]
execution_mode = "oneshot"
check_interval_minutes = 30  # ワンショットモードでは無視されます

[notification]
enabled = true  # 更新がある場合は必ず通知します
```

### Windowsタスクスケジューラーでの自動実行（推奨）

ワンショットモードを使用して、メモリ効率的な定期実行を設定できます。

#### 1. 実行用スクリプトの準備

プロジェクトディレクトリに以下のファイルが自動生成されます：

- `run_wsl_watcher.bat` - 実行用バッチファイル
- `run_wsl_watcher_silent.vbs` - サイレント実行用VBSスクリプト

#### 2. タスクスケジューラーの設定

```powershell
# タスクスケジューラーを開く
taskschd.msc
```

**タスク作成手順**：

1. **基本タブ**：
   - 名前: `WSL Kernel Watcher`
   - 説明: `WSL2カーネル更新チェック`
   - ユーザーがログオンしているかどうかにかかわらず実行する

2. **トリガータブ**：
   - 新規 → 毎日
   - 開始時刻: 任意（例: 09:00）
   - 詳細設定 → 繰り返し間隔: 30分、継続時間: 無期限

3. **操作タブ**：
   - プログラム: `[プロジェクトパス]\run_wsl_watcher_silent.vbs`
   - 開始場所: `[プロジェクトパス]`

4. **条件タブ**：
   - ✅ ネットワーク接続が利用可能な場合のみ開始する

#### 3. 動作確認

```powershell
# サイレント実行のテスト
cscript run_wsl_watcher_silent.vbs
```

#### メリット

- **メモリ効率**: 実行時のみリソースを使用
- **サイレント実行**: ターミナルウィンドウが表示されない
- **信頼性**: Windowsの標準機能で管理
- **ログ記録**: 実行履歴を確認可能

## 実運用での注意事項

### Store版Pythonからの移行

Windows Store版Pythonは開発に制限があるため、公式版への移行を推奨します：

```powershell
# uvでPython環境を管理（推奨）
uv python install 3.13
uv python pin 3.13

# 環境の再構築
uv sync --group dev
```

## 開発

### 開発環境のセットアップ

```powershell
# 依存関係のインストール
uv sync --group dev

# pre-commitフックのセットアップ
uv run pre-commit install
```

### テストの実行

```powershell
# 全テストを実行
uv run pytest

# カバレッジ付きでテスト実行
uv run pytest --cov=src --cov-report=html
```

### コード品質チェック

```powershell
# Ruffによるリント・フォーマット
uv run ruff check .
uv run ruff format .

# MyPyによる型チェック
uv run mypy src/
```

## プロジェクト構造

```
WSL-kernel-watcher/
├── src/                    # ソースコード
│   ├── __init__.py
│   ├── main.py            # エントリーポイント
│   └── logger.py          # ログ設定
├── tests/                 # テストコード
├── config.toml           # 設定ファイル
├── pyproject.toml        # プロジェクト設定
└── README.md
```

## ライセンス

MIT License

## 貢献

プルリクエストやイシューの報告を歓迎します。詳細は[CONTRIBUTING.md](CONTRIBUTING.md)をご覧ください。

## リンク

- [Changelog](CHANGELOG.md) - 変更履歴
- [Contributing](CONTRIBUTING.md) - 開発ガイド
- [Security Policy](SECURITY.md) - セキュリティポリシー
- [License](LICENSE) - MITライセンス