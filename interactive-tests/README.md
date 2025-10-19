# 操作系テスト (Interactive Tests)

TEST_PLAN.mdに基づいた実際の動作確認テストです。

## テスト構成

### 1. Dockerビルド確認 (`test_docker_build.py`)
- Dockerイメージのビルド確認
- イメージサイズの確認
- 依存関係のインストール確認

### 2. コンテナ起動確認 (`test_container_startup.py`)
- docker-composeでの起動確認
- 環境変数の読み込み確認
- ログ出力の確認
- 自動クリーンアップ

### 3. GitHub API接続確認 (`test_github_api.py`)
- GitHub APIへの接続確認
- 最新リリース情報の取得確認
- レート制限処理の確認
- プレリリース除外機能の確認

### 4. WSL経由通知確認 (`test_wsl_notification.py`)
- WSLアクセスの確認（Windows環境のみ）
- PowerShell実行の確認
- Windows Toast通知の確認
- Linux環境では自動スキップ

### 5. エラーハンドリング確認 (`test_error_handling.py`)
- ネットワークエラー時の処理確認
- 設定エラー時の処理確認
- 通知エラー時の処理確認
- タイムアウト処理の確認

## 実行方法

### 全テスト実行
```bash
cd interactive-tests
python run_all_tests.py
```

### 個別テスト実行
```bash
cd interactive-tests
python test_docker_build.py
python test_container_startup.py
python test_github_api.py
python test_error_handling.py
python test_wsl_notification.py  # Windows環境のみ
```

## 実行環境

### 純粋Linux環境
- ✅ Dockerビルド確認
- ✅ コンテナ起動確認
- ✅ GitHub API接続確認
- ✅ エラーハンドリング確認
- ⚠️ WSL経由通知確認（スキップ）

### WSL環境（Windows上のLinux）
- ✅ 全テスト実行可能
- ✅ WSL経由通知の実際の動作確認

### Windows環境
- ✅ 全テスト実行可能
- ✅ WSL経由通知の実際の動作確認

## 注意事項

1. **GitHub APIレート制限**: 1時間60リクエストの制限があります
2. **Docker環境**: docker-composeが利用可能である必要があります
3. **Windows専用機能**: WSL経由通知はWindows環境でのみテスト可能です
4. **ネットワーク接続**: GitHub APIへの接続が必要です

## トラブルシューティング

### Dockerビルドエラー
```bash
# キャッシュクリアしてリビルド
docker-compose build --no-cache
```

### コンテナ起動エラー
```bash
# 既存コンテナの停止・削除
docker-compose down
docker system prune -f
```

### GitHub API接続エラー
```bash
# ネットワーク接続確認
curl -I https://api.github.com
```

## 期待される結果

### 純粋Linux環境
```
📊 テスト結果サマリー
============================================================
Dockerビルド確認: ✅ 成功
コンテナ起動確認: ✅ 成功
GitHub API接続確認: ✅ 成功
エラーハンドリング確認: ✅ 成功
WSL経由通知確認: ⚠️ スキップ（純粋Linux環境）

📈 成功率: 4/4 (100.0%)
🎉 実行可能テスト全て成功！
```

### WSL/Windows環境
```
📊 テスト結果サマリー
============================================================
Dockerビルド確認: ✅ 成功
コンテナ起動確認: ✅ 成功
GitHub API接続確認: ✅ 成功
エラーハンドリング確認: ✅ 成功
WSL経由通知確認: ✅ 成功

📈 成功率: 5/5 (100.0%)
🎉 全テスト成功！
```