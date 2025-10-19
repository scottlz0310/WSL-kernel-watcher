# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-19

### Added
- 🐳 **Docker常駐アーキテクチャ**: 完全新設計による軽量化
  - Linuxコンテナで24/7監視
  - WSL経由でWindows Toast通知
  - 環境変数による簡単設定
  - 自動再起動機能
- 🔧 **操作系テストスイート**: 包括的な動作確認
  - Dockerビルド・起動確認
  - GitHub API接続テスト
  - WSL経由通知テスト（WSL環境自動検知）
  - エラーハンドリング確認
- 🌐 **WSL環境自動検知**: `/proc/version`からMicrosoft/WSL検出
- ⚙️ **環境変数設定**: docker-compose.ymlで全設定管理

### Changed
- 🏗️ **破壊的変更**: タスクトレイ常駐からDocker常駐に完全移行
- 📦 **依存関係最小化**: Docker環境に最適化
- 🔄 **非同期処理**: リソース効率的な実装

### Removed
- ❌ **タスクトレイ機能**: Docker常駐により不要
- ❌ **config.toml**: 環境変数に統一
- ❌ **Windows専用依存**: Linuxコンテナで動作

### Technical
- Docker + docker-compose対応
- WSL経由PowerShell実行
- 環境変数による設定管理
- 操作系テスト完備

## [1.2.0] - 2025-01-10

### Added
- 🔧 **Pre-commitフック強化**: 開発品質向上のための包括的なフック設定
  - ruff check --fix: 自動コード修正
  - ruff format: コードフォーマット統一
  - mypy: 型チェック強化
  - pytest: テスト実行の自動化
- 🏗️ **uv対応**: 最新のPythonパッケージマネージャーに完全対応
  - dependency-groupsによる開発依存関係管理
  - 高速な依存関係解決とインストール
  - CI/CD環境での最適化
- 📦 **自動インストールスクリプト**: install.ps1による簡単セットアップ
  - uv/pipx の自動検出とインストール
  - 仮想環境の自動作成
  - config.toml の自動生成
  - カスタムインストールパス対応

### Changed
- 📦 **依存関係管理の現代化**
  - requirements.txtからpyproject.toml + dependency-groupsに移行
  - 開発用依存関係の明確な分離
- 🔍 **コード品質チェックの強化**
  - MyPy型チェックの厳格化
  - Ruffによる包括的なリント設定
  - pytest-timeoutによるハングアップ対策
- 🚀 **CI/CD最適化**
  - GitHub ActionsでのWindows環境最適化
  - プラグイン競合問題の解決
  - ローカル・CI環境の設定統一

### Fixed
- 🐛 **Windows環境での問題解決**
  - pytest-timeoutプラグインの重複登録エラー修正
  - Windows-Toastsインポートエラー処理改善
  - パス処理のWindows互換性向上
- 🔧 **設定ファイルの整合性**
  - Pre-commit設定とCI設定の完全同期
  - プラグイン明示指定の最適化

### Technical
- Python 3.9-3.13 対応継続
- uv 0.8.22+ 対応
- 新しい開発依存関係: pytest-timeout, pre-commit
- Windows Server 2025 CI環境対応

## [1.1.0] - 2025-01-05

### Added
- 🆕 **ワンショットモード**: 一度だけチェックして終了する新しい実行モード
  - CI/CDパイプラインやスケジュールタスクでの利用に最適
  - `config.toml`で`execution_mode = "oneshot"`に設定
  - 常駐せずに即座に終了するため、軽量で効率的
- 階層構造対応の設定ファイル形式
  - `[general]`, `[notification]`, `[logging]`セクションに分離
  - 既存のフラット構造との互換性も維持
- 包括的なテストカバレッジ（86.29%達成）
  - ワンショットモード専用テストスイート
  - エンドツーエンド統合テスト
  - エラーハンドリングテスト

### Changed
- 設定ファイル構造の改善（階層化）
- コード品質の向上（Ruff lint 100%通過）
- 型アノテーションの完全対応
- 例外処理の改善（適切なfrom句の追加）

### Fixed
- 設定ファイル読み込み時の階層構造対応
- テストケースの安定性向上
- 型チェックエラーの解消

### Technical
- Python 3.9+ 対応
- 新しい依存関係: types-requests, types-toml
- CI/CD対応の完了（全リントチェック通過）

## [1.0.0] - 2024-12-XX

### Added
- 初回リリース
- GitHub APIを使用したWSL2カーネルリリース監視
- プレリリース除外機能
- Windowsトースト通知
- タスクトレイ常駐機能
- 設定ファイル管理
- 包括的なログ機能
- レート制限対応
- リトライ機能

[2.0.0]: https://github.com/scottlz0310/WSL-kernel-watcher/compare/v1.2.0...v2.0.0
[1.2.0]: https://github.com/scottlz0310/WSL-kernel-watcher/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/scottlz0310/WSL-kernel-watcher/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/scottlz0310/WSL-kernel-watcher/releases/tag/v1.0.0