import logging
import re
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)


class WSLUtils:
    @staticmethod
    def get_current_kernel_version() -> Optional[str]:
        """現在のWSLカーネルバージョンを取得"""
        try:
            # WSL内でカーネルバージョンを取得
            result = subprocess.run(
                ["wsl", "-e", "uname", "-r"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                kernel_info = result.stdout.strip()
                # バージョン番号を抽出 (例: 5.15.90.1-microsoft-standard-WSL2)
                version_match = re.search(r"(\d+\.\d+\.\d+\.\d+)", kernel_info)
                if version_match:
                    return version_match.group(1)

            logger.warning(f"Failed to parse kernel version: {result.stdout}")
            return None

        except subprocess.TimeoutExpired:
            logger.error("WSL command timed out")
            return None
        except Exception as e:
            logger.error(f"Error getting WSL kernel version: {e}")
            return None

    @staticmethod
    def compare_versions(current: str, latest: str) -> bool:
        """バージョン比較 (latest > current の場合 True)"""
        try:

            def version_tuple(v):
                return tuple(map(int, v.split(".")))

            return version_tuple(latest) > version_tuple(current)

        except Exception as e:
            logger.error(f"Error comparing versions {current} vs {latest}: {e}")
            return False
