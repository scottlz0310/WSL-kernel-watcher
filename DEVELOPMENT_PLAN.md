# WSL Kernel Watcher v2 開発計画

## 概要
Docker常駐 → WSL経由PowerShell → Windows Toast通知の新アーキテクチャで再実装

## 技術フロー
```
Docker Container (Linux) 
    ↓ 検知
WSL経由でPowerShell実行
    ↓ 通知
Windows Toast通知
```

## ディレクトリ構成
```
src_v2/          # 新実装
├── __init__.py
├── docker_notifier.py    # WSL経由通知
├── github_watcher.py     # GitHub監視
├── main.py              # エントリーポイント
└── config.py            # 設定管理

tests_v2/        # 新テスト
├── __init__.py
├── test_docker_notifier.py
├── test_github_watcher.py
└── test_main.py

docker/          # Docker関連
├── Dockerfile
└── docker-compose.yml
```

## 実装ステップ

### Phase 1: 基盤実装 ✅
- [x] 作業ブランチ作成: `feature/docker-architecture-v2`
- [x] ディレクトリ構成作成: `src_v2/`, `tests_v2/`
- [x] Docker設定: `Dockerfile`, `docker-compose.yml`
- [x] 基本通知モジュール: `docker_notifier.py`

### Phase 2: コア機能実装 ✅
- [x] GitHub API監視モジュール
- [x] 設定管理モジュール
- [x] メインアプリケーション
- [x] ログ機能

### Phase 3: テスト実装 ✅
- [x] 単体テスト作成
- [x] 統合テスト作成
- [x] Docker環境テスト

### Phase 4: 統合・移行
- [ ] 既存機能との互換性確認
- [ ] ドキュメント更新
- [ ] 既存コード削除
- [ ] mainブランチマージ

## 技術仕様

### Docker Notifier
- WSL経由でPowerShell実行
- Windows Toast通知API使用
- エラーハンドリング・ログ出力

### GitHub Watcher
- 既存のGitHub APIクライアント流用
- Docker環境対応
- レート制限・リトライ機能

### 設定管理
- 環境変数とファイル設定の併用
- Docker環境での設定注入

## 現在の状況
- ブランチ: `feature/docker-architecture-v2`
- 完了: Phase 1, Phase 2, Phase 3
- 次のタスク: 統合・移行 (Phase 4)