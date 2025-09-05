# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-09-05

### Added
- GitHub APIクライアント（レート制限・リトライ対応）
- WSLカーネルバージョン取得・比較機能
- Windows通知システム（トースト通知）
- タスクトレイ常駐機能
- 設定管理システム（TOML形式）
- スケジューリング機能（定期チェック）
- 包括的なログ機能
- プレリリース除外機能
- CI/CDワークフロー（GitHub Actions）
- 194個のテストケース（カバレッジ87%）
- pre-commit設定
- Dependabot自動更新

### Technical Details
- Python 3.9以上対応
- uvによる依存関係管理
- Ruff + MyPy + Pytestによる品質保証
- Windows専用設計

[1.0.0]: https://github.com/scottlz0310/WSL-kernel-watcher/releases/tag/v1.0.0