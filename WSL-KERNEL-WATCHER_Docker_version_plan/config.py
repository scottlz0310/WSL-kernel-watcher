import json
import os

from pydantic import BaseModel


class Config(BaseModel):
    mcp_github_url: str
    notification_url: str
    check_interval: int
    repositories: list[str]


def load_config() -> Config:
    # 環境変数から基本設定
    config_data = {
        "mcp_github_url": os.getenv("MCP_GITHUB_URL", "http://github-mcp:3000"),
        "notification_url": os.getenv(
            "NOTIFICATION_URL", "http://host.docker.internal:9999/notify"
        ),
        "check_interval": int(os.getenv("CHECK_INTERVAL", "1800")) // 60,  # 分に変換
        "repositories": [],
    }

    # リポジトリリストを設定ファイルから読み込み
    try:
        with open("/app/config/repositories.json") as f:
            repo_config = json.load(f)
            config_data["repositories"] = repo_config.get("repositories", [])
    except FileNotFoundError:
        config_data["repositories"] = ["microsoft/WSL2-Linux-Kernel"]

    return Config(**config_data)
