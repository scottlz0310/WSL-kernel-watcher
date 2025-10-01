# Windows Notification Server

Docker containers can send HTTP requests to this server to display Windows toast notifications.

## Setup

1. Run the installation script:
   ```powershell
   .\install.ps1
   ```

2. Start the notification server:
   ```powershell
   .\start_notification_server.bat
   ```

## Usage

Send POST request to `http://localhost:9999/notify`:

```json
{
  "title": "Repository Update",
  "message": "New version v1.2.0 available",
  "url": "https://github.com/owner/repo/releases/latest"
}
```

## Health Check

```bash
curl http://localhost:9999/health
```

## Features

- ✅ Windows Toast notifications via BurntToast
- ✅ Fallback to MessageBox if BurntToast unavailable
- ✅ Health check endpoint
- ✅ Comprehensive error handling
- ✅ Logging support