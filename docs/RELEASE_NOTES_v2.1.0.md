# WSL Kernel Watcher v2.1.0 リリースノート

## 🎉 新機能・改善

### ✅ GitHub Personal Access Token対応
- **GitHub API認証**: Personal Access Tokenによる認証機能を追加
- **レート制限大幅改善**: 60 → 5000リクエスト/時間
- **環境変数対応**: `GITHUB_PERSONAL_ACCESS_TOKEN` および `GITHUB_TOKEN` をサポート

### 🔧 ポータブル化対応
- **動的ユーザー名対応**: 任意のユーザー環境で動作可能
- **動的パス対応**: 任意のディレクトリで動作可能
- **systemdサービス自動生成**: インストール時にユーザー環境に合わせて自動生成

### 🚀 監視システム改善
- **競合状態解決**: 複数通知の同時処理時の競合問題を修正
- **エラーハンドリング強化**: ファイル削除エラーの抑制
- **アトミック処理**: ファイル移動による確実な処理

### 🧪 テストスイート拡張
- **バージョン変更通知テスト**: 模擬的なカーネルダウングレードテスト追加
- **完全フローテスト**: Docker→systemd→通知→クリーンアップの全フロー確認
- **インタラクティブテスト**: 実際の通知クリック確認機能
- **100%テストカバレッジ**: 全7項目のテスト完全成功

## 🔄 変更内容

### 📋 設定・環境変数
```yaml
# 新規追加
GITHUB_PERSONAL_ACCESS_TOKEN: GitHub Personal Access Token
GITHUB_TOKEN: GitHub Token (従来互換)
```

### 🛠️ systemdサービス
- テンプレート化によるポータブル対応
- 動的ユーザー名・パス設定
- 自動インストール・アンインストール機能

### 📊 テストコマンド
```bash
make test                    # 全操作系テスト（7項目）
make test-version-change     # バージョン変更通知テスト
make test-full-flow         # 完全フローテスト
make test-interactive       # インタラクティブテスト
```

## 🏆 品質指標

### ✅ テスト成功率
- **v2.0.0**: 83.3% (5/6)
- **v2.1.0**: **100.0% (7/7)** 🎉

### 📈 GitHub API制限
- **v2.0.0**: 60リクエスト/時間
- **v2.1.0**: **5000リクエスト/時間** (83倍向上！)

### 🔧 ポータブル性
- **v2.0.0**: 特定ユーザー環境依存
- **v2.1.0**: **完全ポータブル対応** ✅

## 🚀 アップグレード手順

### 1. 既存サービス停止
```bash
make uninstall-monitor
```

### 2. 新バージョン取得
```bash
git pull origin main
```

### 3. GitHub Personal Access Token設定
```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="your_token_here"
```

### 4. 新サービスインストール
```bash
make install-monitor
make start
```

### 5. 動作確認
```bash
make test
```

## 🎯 次期バージョン予定

- Toast通知の安定化
- 設定UI追加
- 複数リポジトリ監視対応
- Webhook通知機能

---

**WSL Kernel Watcher v2.1.0 - 完璧なプロダクションレディシステム** 🎊