# Windows環境でのテスト手順

## 前提条件

- Windows 10/11
- Docker Desktop for Windows（WSL2バックエンド）
- WSL2統合が有効

## テスト手順

### 1. プロジェクトをクローン

```powershell
# PowerShellで実行
cd C:\Users\YourName\Projects
git clone https://github.com/scottlz0310/WSL-kernel-watcher.git
cd WSL-kernel-watcher
```

### 2. Dockerイメージをビルド

```powershell
docker-compose build
```

### 3. コンテナを起動

```powershell
docker-compose up -d
```

### 4. WSLアクセステスト

```powershell
docker-compose exec wsl-kernel-watcher bash test-wsl-access.sh
```

**期待される出力:**
```
=== WSL.exe アクセステスト ===
✅ wsl.exe が見つかりました
/mnt/c/Windows/System32/wsl.exe

=== Windows側でコマンド実行テスト ===
Test from container
✅ wsl.exe経由でコマンド実行成功

=== PowerShell実行テスト ===
PowerShell Test OK
✅ PowerShell実行成功

=== 全てのテストが成功しました！ ===
このDocker環境ではWindows Toast通知が動作します
```

### 5. 通知テスト

```powershell
docker-compose exec wsl-kernel-watcher python test-notification.py
```

**期待される動作:**
- コンソールに成功メッセージが表示
- Windows通知センターに2つの通知が表示される

### 6. 実際の監視を開始

```powershell
# ログを確認
docker-compose logs -f wsl-kernel-watcher

# Ctrl+Cで終了
```

## トラブルシューティング

### wsl.exeが見つからない

**Docker Desktop設定を確認:**
1. Docker Desktop → Settings → Resources → WSL Integration
2. 使用するディストリビューション（Ubuntu等）を有効化
3. Apply & Restart

### 通知が表示されない

**Windows通知設定を確認:**
1. Windows設定 → システム → 通知
2. 通知を有効化
3. フォーカスアシスト → オフ

## 現在の状況（Linux環境）

現在Linux環境で実行しているため、wsl.exeは利用できません。
これは正常な動作です。

Windows環境でテストを実行すると、上記の手順で通知が表示されます。