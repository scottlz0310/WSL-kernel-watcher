# Docker単独実行例

## 前提条件

1. **Host側通知サーバー起動**:
   ```powershell
   python notification_server_enhanced.py
   ```

2. **WSLカーネルバージョン確認**:
   ```bash
   wsl -e uname -r
   # 例: 5.15.90.1-microsoft-standard-WSL2
   ```

## 実行方法

### **方法1: 環境変数でWSLバージョン指定（推奨）**
```bash
# WSLバージョンを環境変数で指定
docker run --rm \
  -e WSL_KERNEL_VERSION="5.15.90.1" \
  -e NOTIFICATION_URL="http://host.docker.internal:9999/notify" \
  -e GITHUB_TOKEN="your_token_here" \
  wsl-watcher
```

### **方法2: 通知サーバー経由でWSLバージョン取得**
```bash
# 通知サーバーがWSLバージョンも提供
docker run --rm \
  -e NOTIFICATION_URL="http://host.docker.internal:9999/notify" \
  -e GITHUB_TOKEN="your_token_here" \
  wsl-watcher
```

### **方法3: MCP Server使用**
```bash
# 既存のMCP Serverを活用
docker run --rm \
  -e MCP_GITHUB_URL="http://host.docker.internal:3000" \
  -e WSL_KERNEL_VERSION="5.15.90.1" \
  -e NOTIFICATION_URL="http://host.docker.internal:9999/notify" \
  wsl-watcher
```

## 動作確認

1. **通知サーバーヘルスチェック**:
   ```bash
   curl http://localhost:9999/health
   ```

2. **WSLバージョン取得テスト**:
   ```bash
   curl http://localhost:9999/wsl-version
   ```

3. **通知テスト**:
   ```bash
   curl -X POST http://localhost:9999/notify \
     -H "Content-Type: application/json" \
     -d '{"title":"Test","message":"Docker notification test"}'
   ```

## 設定例

```json
{
  "repositories": [
    "microsoft/WSL2-Linux-Kernel"
  ]
}
```

これで**5分で動かせる**状態になります！