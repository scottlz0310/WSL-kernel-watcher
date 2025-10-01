# GitHub Repository Watcher Service for MCP-Docker

## 概要

MCP-DockerプロジェクトにGitHubリポジトリ監視機能を追加し、Docker環境からWindowsホストへのToast通知を実現するサービスです。

## アーキテクチャ

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Docker        │    │   Host           │    │   Windows       │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Repo Watcher│─┼────┼→│Notification  │─┼────┼→│Toast Popup  │ │
│ │   Service   │ │HTTP│ │   Server     │ │PS  │ │             │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
│        │        │    │                  │    │                 │
│ ┌─────────────┐ │    │                  │    │                 │
│ │ GitHub MCP  │ │    │                  │    │                 │
│ │   Server    │ │    │                  │    │                 │
│ └─────────────┘ │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## ディレクトリ構成

```
services/
├── github-watcher/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   ├── src/
│   │   ├── main.py
│   │   ├── watcher.py
│   │   ├── mcp_client.py
│   │   └── config.py
│   └── config/
│       └── repositories.json
├── notification-server/
│   ├── notification_server.py
│   ├── install.ps1
│   └── README.md
└── README.md
```

## 特徴

- ✅ Docker環境からWindows Toast通知
- ✅ MCP GitHub Server経由でAPI効率化
- ✅ 複数リポジトリ同時監視
- ✅ 設定ファイルによる柔軟な管理
- ✅ ヘルスチェック機能
- ✅ エラーハンドリング完備

## Quick Start

1. **Host側セットアップ**:
   ```powershell
   cd services/notification-server
   .\install.ps1
   .\start_notification_server.bat
   ```

2. **Docker側起動**:
   ```bash
   cd services/github-watcher
   docker-compose up -d
   ```

3. **監視リポジトリ設定**:
   ```bash
   # config/repositories.json を編集
   {
     "repositories": [
       "microsoft/WSL2-Linux-Kernel",
       "microsoft/terminal"
     ]
   }
   ```

## 動作確認

```bash
# 通知テスト
curl -X POST http://localhost:9999/notify \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","message":"Hello from Docker!"}'
```