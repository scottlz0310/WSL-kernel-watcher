import asyncio
import logging

import schedule
from watcher import GitHubWatcher

from config import load_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    config = load_config()
    watcher = GitHubWatcher(config)

    # スケジュール設定
    schedule.every(config.check_interval).minutes.do(
        lambda: asyncio.create_task(watcher.check_repositories())
    )

    logger.info("GitHub Repository Watcher started")

    # 初回実行
    await watcher.check_repositories()

    # スケジュール実行
    while True:
        schedule.run_pending()
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
