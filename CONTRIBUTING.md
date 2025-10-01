# Contributing to WSL Kernel Watcher

## 開発環境のセットアップ

### 前提条件
- Windows 10/11
- Python 3.9以上
- [uv](https://docs.astral.sh/uv/)がインストール済み

### セットアップ手順
```powershell
# リポジトリをクローン
git clone https://github.com/scottlz0310/WSL-kernel-watcher.git
cd WSL-kernel-watcher

# 依存関係をインストール
uv sync --group dev

# pre-commitフックをセットアップ
uv run pre-commit install
```

## 開発ワークフロー

### コード品質チェック
```powershell
# リント・フォーマット
uv run ruff check .
uv run ruff format .

# 型チェック
uv run mypy src/

# テスト実行
uv run pytest --cov=src
```

### コミット規約
- `feat:` 新機能
- `fix:` バグ修正
- `docs:` ドキュメント更新
- `test:` テスト追加・修正
- `chore:` その他の変更

### プルリクエスト
1. フィーチャーブランチを作成
2. 変更を実装
3. テストを追加・更新
4. CIが通ることを確認
5. プルリクエストを作成

## コーディング規約
- 日本語でのコメント・ドキュメント
- 型ヒント必須
- 単一責務の原則
- 最小限のコード実装