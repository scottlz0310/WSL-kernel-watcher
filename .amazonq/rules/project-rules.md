# WSLカーネル監視ツール プロジェクトルール

## 基本方針
- 日本語での応答・ドキュメント・コメントを必須とする
- 責務分離の徹底（各モジュール・関数は単一の責務）
- 最小限のコード実装（冗長な実装を避ける）

## 技術スタック
- Python 3.9以上
- 仮想環境管理: uv
- パッケージ管理: pyproject.toml
- リンター: ruff
- 型チェック: mypy
- テスト: pytest
- 通知: windows-toasts
- タスクトレイ: pystray
- スケジューリング: APScheduler

## コーディング規約
- 命名: snake_case（ファイル・関数・変数）、PascalCase（クラス）、UPPER_SNAKE_CASE（定数）
- 型ヒントを必須とする（Anyの使用は例外的）
- print関数によるデバッグ出力は禁止（loggingモジュールを使用）
- 一時コードには _debug_ プレフィックスを付与

## ディレクトリ構成
```
src/                    # 実装コード
├── __init__.py
├── main.py            # エントリーポイント
├── config.py          # 設定管理
├── github_api.py      # GitHub APIクライアント
├── notification.py    # Windows通知
├── tray.py           # タスクトレイ管理
├── wsl_utils.py      # WSL連携機能
├── scheduler.py      # スケジューリング
└── logger.py         # ログ設定

tests/                 # テストコード
config.toml           # 設定ファイル
pyproject.toml        # プロジェクト設定
```

## 品質保証
- ruff check . && ruff format . を必須実行
- mypy src/ による型チェック
- pytest による全テスト実行
- pre-commit フックの使用
- カバレッジ最低基準の維持

## 機能要件
- GitHub APIでWSL2カーネルリリース監視
- プレリリース（RC版・プレビュー版）の除外
- WSLカーネルバージョン取得・比較
- Windowsトースト通知
- タスクトレイ常駐
- 設定ファイル（config.toml）による設定管理