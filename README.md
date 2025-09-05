# WSLカーネル安定版リリース監視ツール

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
- タスクトレイでの常駐動作
- 設定ファイルによるカスタマイズ
- 包括的なログ機能

## 必要環境

- Windows 10/11
- Python 3.9以上
- WSL2がインストールされていること

## インストール

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
uv sync --extra dev

# pre-commitフックをセットアップ
uv run pre-commit install

# アプリケーションを実行
uv run python -m src.main
```

## 使用方法

### 基本的な実行

```powershell
# 開発環境で実行
uv run python -m src.main

# または
uv run wsl-kernel-watcher
```

### 設定

`config.toml`ファイルを編集して動作をカスタマイズできます：

```toml
[general]
# チェック間隔（分）
check_interval_minutes = 30

# 監視対象リポジトリ
repository_url = "microsoft/WSL2-Linux-Kernel"

[notification]
# 通知機能の有効化
enabled = true

[logging]
# ログレベル
level = "INFO"
```

## 開発

### 開発環境のセットアップ

```powershell
# 依存関係のインストール
uv sync --extra dev

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