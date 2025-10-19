# Windows Toast通知テストガイド

## テスト方法

### 方法1: Dockerコンテナ内からテスト（推奨）

```bash
# 1. コンテナをビルド＆起動
docker-compose up -d

# 2. WSLアクセステスト
docker-compose exec wsl-kernel-watcher bash test-wsl-access.sh

# 3. 通知テスト実行
docker-compose exec wsl-kernel-watcher python test-notification.py
```

### 方法2: ローカル環境でテスト（WSL2内）

```bash
# WSL2内で実行
cd ~/WSL-kernel-watcher
uv run python test-notification.py
```

## 期待される動作

### 成功時

1. **コンソール出力**:
   ```
   ============================================================
   Windows Toast通知テスト
   ============================================================

   テスト通知を送信します...
   Windows側で通知が表示されるか確認してください

   1. シンプルな通知テスト
      結果: ✅ 成功

   2. カーネル更新通知テスト
      結果: ✅ 成功

   ============================================================
   ✅ 全てのテストが成功しました！
   Windows側で2つの通知が表示されているはずです
   ```

2. **Windows通知センター**:
   - 通知1: "WSL Kernel Watcher テスト"
   - 通知2: "WSL2カーネル更新通知"

### 失敗時のトラブルシューティング

#### エラー: wsl.exe が見つかりません

**原因**: Docker DesktopのWSL2統合が無効

**解決策**:
```bash
# Docker Desktop → Settings → Resources → WSL Integration
# 使用するディストリビューションを有効化
```

#### エラー: PowerShell実行失敗

**原因**: Windows側のPATHが通っていない

**解決策**:
```bash
# コンテナ内で確認
docker-compose exec wsl-kernel-watcher bash -c "which wsl.exe"
# /mnt/c/Windows/System32/wsl.exe が表示されるか確認

# 表示されない場合はDockerfileを確認
# ENV PATH="${PATH}:/mnt/c/Windows/System32" が設定されているか
```

#### 通知が表示されない（コマンドは成功）

**原因**: Windows通知設定が無効

**解決策**:
1. Windows設定 → システム → 通知
2. 通知を有効化
3. フォーカスアシスト（集中モード）を確認
   - 「重要な通知のみ」または「アラームのみ」になっていないか

## 手動テスト

### 最小限のテスト

```bash
# WSL2内で実行
wsl.exe -e powershell.exe -Command "
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null;
\$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02);
\$toastXml = [xml] \$template.GetXml();
\$toastXml.GetElementsByTagName('text')[0].AppendChild(\$toastXml.CreateTextNode('Test Title')) | Out-Null;
\$toastXml.GetElementsByTagName('text')[1].AppendChild(\$toastXml.CreateTextNode('Test Message')) | Out-Null;
\$toast = [Windows.UI.Notifications.ToastNotification]::new(\$toastXml);
\$notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('WSL.KernelWatcher');
\$notifier.Show(\$toast);
"
```

### Docker内から手動テスト

```bash
docker-compose exec wsl-kernel-watcher wsl.exe -e powershell.exe -Command "Write-Host 'Docker -> WSL -> Windows Test OK'"
```

## 確認チェックリスト

- [ ] Docker Desktop for Windowsがインストール済み
- [ ] Docker DesktopでWSL2バックエンドが有効
- [ ] Docker DesktopのWSL2統合が有効
- [ ] Windows通知設定が有効
- [ ] フォーカスアシストが無効または適切に設定
- [ ] `docker-compose up -d` でコンテナが起動
- [ ] `test-wsl-access.sh` が成功
- [ ] `test-notification.py` が成功
- [ ] Windows側で通知が表示される

## 次のステップ

通知テストが成功したら：

1. **実際の監視を開始**:
   ```bash
   docker-compose up -d
   docker-compose logs -f wsl-kernel-watcher
   ```

2. **自動起動設定**:
   - Docker Desktop → Settings → General
   - ✅ Start Docker Desktop when you sign in to your computer

3. **動作確認**:
   - PCを再起動
   - Docker Desktopが自動起動するか確認
   - コンテナが自動起動するか確認: `docker ps`