# WSL2内でのDocker常駐セットアップ

## 前提条件

- Windows 10/11
- WSL2インストール済み
- WSL2ディストリビューション（Ubuntu推奨）
- Docker Desktop for Windows **または** WSL2内にDockerインストール

## セットアップ方法

### 方法1: Docker Desktop for Windows使用（推奨）

Docker Desktop for WindowsはWSL2統合機能があり、自動起動が簡単です。

#### 1. Docker Desktop設定

1. Docker Desktop起動
2. Settings → General
   - ✅ Start Docker Desktop when you sign in to your computer
   - ✅ Use the WSL 2 based engine
3. Settings → Resources → WSL Integration
   - ✅ Enable integration with my default WSL distro
   - ✅ 使用するディストリビューションを有効化

#### 2. WSL内でプロジェクト配置

```bash
# WSL内で実行
cd ~
git clone https://github.com/scottlz0310/WSL-kernel-watcher.git
cd WSL-kernel-watcher
```

#### 3. Docker起動

```bash
# コンテナ起動（Docker Desktopが起動していれば自動で動作）
docker-compose up -d

# ログ確認
docker-compose logs -f
```

#### 4. Windows起動時の自動起動

Docker Desktopが自動起動するように設定されていれば、コンテナも自動起動します：

```bash
# docker-compose.ymlでrestart: unless-stoppedが設定済み
# PC再起動後も自動的にコンテナが起動します
```

### 方法2: WSL2内にDocker直接インストール

Docker Desktop不要で、WSL2内で完結させる方法です。

#### 1. WSL2内にDockerインストール

```bash
# Ubuntu/Debianの場合
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker $USER

# 再ログイン
exit
# WSLを再起動
```

#### 2. Dockerサービス自動起動設定

```bash
# systemdが使える場合（Ubuntu 22.04以降）
sudo systemctl enable docker
sudo systemctl start docker

# systemdが使えない場合
# ~/.bashrcまたは~/.zshrcに追加
echo 'if ! pgrep -x dockerd > /dev/null; then sudo dockerd > /dev/null 2>&1 &; fi' >> ~/.bashrc
```

#### 3. Windows起動時にWSL自動起動

PowerShellスクリプトを作成：

**start-wsl-docker.ps1**
```powershell
# WSL起動とDocker起動
wsl -d Ubuntu -u $env:USERNAME bash -c "cd ~/WSL-kernel-watcher && docker-compose up -d"
```

**Windowsタスクスケジューラー設定：**
1. タスクスケジューラーを開く
2. 基本タスクの作成
   - 名前: WSL Docker Watcher
   - トリガー: ログオン時
   - 操作: プログラムの開始
   - プログラム: `powershell.exe`
   - 引数: `-WindowStyle Hidden -File "C:\path\to\start-wsl-docker.ps1"`

## 動作確認

### 1. WSL内でDockerが動作しているか確認

```bash
# WSL内で実行
docker ps
# wsl-kernel-watcherコンテナが表示されればOK
```

### 2. 通知テスト

```bash
# WSL内で実行
docker exec wsl-kernel-watcher wsl.exe -e powershell.exe -Command "Write-Host 'Test'"
# エラーが出なければWSL→Windows通信OK
```

### 3. ログ確認

```bash
docker-compose logs -f wsl-kernel-watcher
```

## トラブルシューティング

### Docker Desktopが起動しない

```powershell
# PowerShellで確認
Get-Service -Name com.docker.service
# 停止している場合は手動起動
Start-Service -Name com.docker.service
```

### WSL2からwsl.exeが実行できない

```bash
# WSL内で確認
which wsl.exe
# /mnt/c/Windows/System32/wsl.exe が表示されればOK

# PATHに追加されていない場合
echo 'export PATH=$PATH:/mnt/c/Windows/System32' >> ~/.bashrc
source ~/.bashrc
```

### コンテナが自動起動しない

```bash
# docker-compose.ymlのrestart設定確認
grep restart docker-compose.yml
# restart: unless-stopped が設定されているか確認

# 手動で再起動ポリシー設定
docker update --restart unless-stopped wsl-kernel-watcher
```

## 推奨構成

```
Windows 10/11
  ↓ 起動時自動起動
Docker Desktop for Windows
  ↓ WSL2統合
WSL2 (Ubuntu)
  ↓ docker-compose up -d
Docker Container (wsl-kernel-watcher)
  ↓ wsl.exe経由
Windows PowerShell
  ↓ Toast通知
Windows通知センター
```

## メリット・デメリット

### Docker Desktop使用
- ✅ 設定が簡単
- ✅ 自動起動が確実
- ✅ GUIで管理可能
- ❌ リソース消費が多い

### WSL2内Docker直接インストール
- ✅ 軽量
- ✅ Docker Desktop不要
- ❌ 自動起動設定が複雑
- ❌ 手動設定が必要