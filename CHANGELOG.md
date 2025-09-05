# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[1.1.0]: https://github.com/scottlz0310/WSL-kernel-watcher/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/scottlz0310/WSL-kernel-watcher/releases/tag/v1.0.0