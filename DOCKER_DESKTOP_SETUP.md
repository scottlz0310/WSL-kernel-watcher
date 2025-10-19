# Docker Desktop for Windows セットアップガイド

## アーキテクチャ

```
Docker Desktop for Windows (WSL2バックエンド)
  ↓
Docker Container (Linux)
  ↓ wsl.exe -e powershell.exe 実行
WSL2 (自動経由)
  ↓ powershell.exe 呼び出し
Windows Host
  ↓ Toast通知表示
```

## 必要なもの

- Windows 10/11
- Docker Desktop for Windows (WSL2バックエンド)
- **WSL2内へのインストールや常駐プロセスは不要**

## セットアップ手順

### 1. Docker Desktop for Windowsインストール

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/)をダウンロード
2. インストール時に「Use WSL 2 instead of Hyper-V」を選択
3. インストール後、Docker Desktopを起動

### 2. Docker Desktop設定

1. Docker Desktop → Settings → General
   - ✅ **Start Docker Desktop when you sign in to your computer**
   - ✅ **Use the WSL 2 based engine**

2. Docker Desktop → Settings → Resources → WSL Integration
   - ✅ **Enable integration with my default WSL distro**
   - 使用するディストリビューション（Ubuntu等）を有効化

### 3. プロジェクトをクローン

**Windows側（推奨）:**
```powershell
cd C:\Users\YourName\Projects
git clone https://github.com/scottlz0310/WSL-kernel-watcher.git
cd WSL-kernel-watcher
```

**または WSL2側:**
```bash
cd ~
git clone https://github.com/scottlz0310/WSL-kernel-watcher.git
cd WSL-kernel-watcher
```

### 4. 環境変数設定（オプション）

```bash
cp .env.example .env
# .envを編集して設定をカスタマイズ
```

### 5. Docker起動

```bash
# コンテナビルド＆起動
docker-compose up -d

# ログ確認
docker-compose logs -f wsl-kernel-watcher
```

### 6. 動作確認

```bash
# wsl.exeアクセステスト
docker-compose exec wsl-kernel-watcher bash test-wsl-access.sh

# 期待される出力:
# ✅ wsl.exe が見つかりました
# ✅ wsl.exe経由でコマンド実行成功
# ✅ PowerShell実行成功
```

## 自動起動設定

Docker Desktopの「Start Docker Desktop when you sign in」が有効なら、PC起動時に自動的にコンテナも起動します。

### 確認方法

```bash
# コンテナの再起動ポリシー確認
docker inspect wsl-kernel-watcher | grep -A 5 RestartPolicy

# 期待される出力:
# "RestartPolicy": {
#     "Name": "unless-stopped",
#     ...
# }
```

## トラブルシューティング

### wsl.exeが見つからない

**原因**: Docker DesktopのWSL2統合が無効

**解決策**:
1. Docker Desktop → Settings → Resources → WSL Integration
2. 使用するディストリビューションを有効化
3. Docker Desktopを再起動

### PowerShellが実行できない

**原因**: Windows側のPATHが通っていない

**解決策**:
```bash
# コンテナ内で確認
docker-compose exec wsl-kernel-watcher bash -c "echo \$PATH"
# /mnt/c/Windows/System32 が含まれているか確認
```

### 通知が表示されない

**原因**: Windows通知設定が無効

**解決策**:
1. Windows設定 → システム → 通知
2. 通知を有効化
3. フォーカスアシスト（集中モード）を無効化

### コンテナが自動起動しない

**原因**: Docker Desktopが自動起動していない

**解決策**:
1. Docker Desktop → Settings → General
2. ✅ Start Docker Desktop when you sign in to your computer
3. PCを再起動して確認

## 停止・削除

```bash
# コンテナ停止
docker-compose stop

# コンテナ削除
docker-compose down

# イメージも削除
docker-compose down --rmi all
```

## メリット

- ✅ **Windows側にインストール不要**
- ✅ **WSL2内に常駐プロセス不要**
- ✅ **Docker Desktopの自動起動で完結**
- ✅ **設定が簡単**
- ✅ **GUIで管理可能**

## 注意事項

- Docker Desktop for Windowsが起動していないとコンテナも動作しません
- WSL2バックエンドが必須です（Hyper-Vバックエンドでは動作しません）
- 初回起動時はイメージビルドに数分かかります