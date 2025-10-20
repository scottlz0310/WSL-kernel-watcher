# Windows完結型WSLカーネル監視ツール実装プラン

## 🎯 アプローチ比較

### 現在の実装 vs Windows完結型

| 項目 | 現在の実装 | Windows完結型 |
|------|------------|---------------|
| 言語 | Python | PowerShell |
| 依存関係 | 多数のPythonパッケージ | Windows標準機能のみ |
| 配布 | pip/uv/pipx | .ps1ファイル1つ |
| 実行環境 | Python仮想環境 | Windows標準 |
| 通知 | windows-toasts | BurntToast |
| 常駐 | Pythonプロセス | タスクスケジューラ |

## 📋 実装プラン

### プラン A: 単一PowerShellスクリプト
```
wsl-kernel-notifier.ps1  # 1ファイル完結
├── WSLバージョン取得
├── GitHub API呼び出し
├── バージョン比較
├── トースト通知
└── ログ記録
```

**メリット**: 最もシンプル、配布が容易
**デメリット**: 機能拡張が困難

### プラン B: モジュール化PowerShell
```
WSL-Kernel-Notifier/
├── WSL-Kernel-Notifier.psm1    # メインモジュール
├── Install.ps1                 # インストールスクリプト
├── Uninstall.ps1              # アンインストールスクリプト
└── Config.json                # 設定ファイル
```

**メリット**: 保守性が高い、設定可能
**デメリット**: 複数ファイル管理

### プラン C: Windows Service + PowerShell
```
WSL-Kernel-Service/
├── Service.ps1               # サービス本体
├── Install-Service.ps1       # サービス登録
├── Uninstall-Service.ps1     # サービス削除
└── Config.xml               # 設定ファイル
```

**メリット**: 真の常駐、システム統合
**デメリット**: 管理者権限必要

## 🚀 推奨実装: プラン B

### ファイル構成
```powershell
# WSL-Kernel-Notifier.psm1
function Get-WSLKernelVersion { }
function Get-LatestKernelVersion { }
function Compare-Versions { }
function Send-UpdateNotification { }
function Write-NotificationLog { }

# Install.ps1
- BurntToastモジュールインストール
- タスクスケジューラ登録
- 設定ファイル作成

# Config.json
{
  "CheckIntervalHours": 24,
  "Repository": "microsoft/WSL2-Linux-Kernel",
  "LogPath": "$env:TEMP\\WSL-Kernel-Notifier.log"
}
```

### 実装手順
1. **PowerShellモジュール作成**
2. **GitHub API統合**
3. **BurntToast通知実装**
4. **タスクスケジューラ統合**
5. **インストーラー作成**

### 配布方法
- **GitHub Releases**: .zip配布
- **PowerShell Gallery**: `Install-Module`
- **Chocolatey**: パッケージ化
- **Microsoft Store**: MSIX形式

## 💡 技術的考慮点

### PowerShell実装の利点
- Windows標準搭載
- .NET Framework活用
- WMI/CIM統合
- タスクスケジューラ連携

### 課題と対策
- **実行ポリシー**: `Set-ExecutionPolicy RemoteSigned`
- **依存関係**: BurntToastの自動インストール
- **エラーハンドリング**: Try-Catch-Finally
- **ログ管理**: ローテーション機能

## 🔄 移行戦略

### 段階的実装
1. **Phase 1**: 基本機能（バージョンチェック・通知）
2. **Phase 2**: 設定管理・ログ機能
3. **Phase 3**: インストーラー・配布準備
4. **Phase 4**: 高度な機能（フィルタリング等）

### 既存実装との関係
- **並行開発**: 別リポジトリで開発
- **機能比較**: 両方のメリット活用
- **ユーザー選択**: 用途に応じて選択可能