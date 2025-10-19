# WSL Kernel Watcher v2 動作確認計画

## 確認項目

### 1. Dockerビルド確認
- [ ] Dockerイメージが正常にビルドできるか
- [ ] 依存関係が正しくインストールされるか
- [ ] イメージサイズが適切か

### 2. コンテナ起動確認
- [ ] docker-composeで起動できるか
- [ ] 環境変数が正しく読み込まれるか
- [ ] ログが正常に出力されるか

### 3. GitHub API接続確認
- [ ] GitHub APIに接続できるか
- [ ] 最新リリース情報を取得できるか
- [ ] レート制限が正しく処理されるか

### 4. WSL経由通知確認（Windows環境のみ）
- [ ] Docker内からWSLにアクセスできるか
- [ ] PowerShellが実行できるか
- [ ] Windows Toast通知が表示されるか

### 5. エラーハンドリング確認
- [ ] ネットワークエラー時の挙動
- [ ] API制限時の挙動
- [ ] 通知失敗時の挙動

## 実行手順

### Linux環境での確認（現在の環境）

```bash
# 1. Dockerイメージビルド
docker-compose build

# 2. 依存関係確認
docker-compose run --rm wsl-kernel-watcher uv run python -c "import src_v2; print('OK')"

# 3. GitHub API接続テスト
docker-compose run --rm wsl-kernel-watcher uv run python -c "
from src_v2.github_watcher import GitHubWatcher
watcher = GitHubWatcher()
release = watcher.get_latest_stable_release()
print(f'Latest: {release.tag_name if release else None}')
"

# 4. 設定読み込みテスト
docker-compose run --rm -e LOG_LEVEL=DEBUG wsl-kernel-watcher uv run python -c "
from src_v2.config import ConfigManager
config = ConfigManager.load()
print(f'Config: {config.repository_url}, {config.check_interval_minutes}min')
"
```

### Windows環境での確認（WSL経由通知テスト）

```powershell
# 1. コンテナ起動
docker-compose up -d

# 2. ログ確認
docker-compose logs -f

# 3. WSL経由通知テスト
docker exec wsl-kernel-watcher wsl.exe -e powershell.exe -Command "Write-Host 'Test'"

# 4. 停止
docker-compose down
```

## 確認結果

### Linux環境（2025-10-12）
- [x] Dockerビルド: ✅ 成功
- [x] GitHub API接続: ✅ 成功（最新版: linux-msft-wsl-6.6.87.2）
- [x] 設定読み込み: ✅ 成功（環境変数正常動作） 

### Windows環境（未実施）
- [ ] WSL経由通知: 
- [ ] 実運用テスト: 

## 既知の問題

1. Linux環境ではWSL経由通知はテストできない（Windows専用機能）
2. GitHub APIレート制限に注意（1時間60リクエスト）

## 次のステップ

- [ ] Linux環境での基本動作確認
- [ ] Windows環境での完全動作確認
- [ ] 問題があれば修正
- [ ] 問題なければPhase 6（既存コード削除・マージ）へ