"""WSL連携機能を提供するモジュール."""

import re
import subprocess
from typing import Callable, Optional, Tuple

from .logger import get_logger

logger = get_logger()


class WSLUtils:
    """WSL環境との連携機能を提供するクラス."""

    def __init__(self, timeout: int = 30):
        """WSLUtilsを初期化する.

        Args:
            timeout: WSLコマンドのタイムアウト時間（秒）
        """
        self.timeout = timeout

    def get_current_kernel_version(self) -> Optional[str]:
        """現在のWSLカーネルバージョンを取得する.

        Returns:
            カーネルバージョン文字列。取得に失敗した場合はNone

        Raises:
            WSLCommandError: WSLコマンドの実行に失敗した場合
        """
        try:
            logger.info("WSLカーネルバージョンを取得中...")
            result = subprocess.run(
                ["wsl", "uname", "-r"],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=True,
            )

            kernel_version = result.stdout.strip()
            logger.info(f"現在のWSLカーネルバージョン: {kernel_version}")
            return kernel_version

        except subprocess.TimeoutExpired:
            error_msg = f"WSLコマンドがタイムアウトしました（{self.timeout}秒）"
            logger.error(error_msg)
            raise WSLCommandError(error_msg)

        except subprocess.CalledProcessError as e:
            error_msg = f"WSLコマンドの実行に失敗しました: {e.stderr}"
            logger.error(error_msg)
            raise WSLCommandError(error_msg)

        except FileNotFoundError:
            error_msg = (
                "WSLが見つかりません。WSLがインストールされているか確認してください"
            )
            logger.error(error_msg)
            raise WSLCommandError(error_msg)

        except Exception as e:
            error_msg = f"予期しないエラーが発生しました: {str(e)}"
            logger.error(error_msg)
            raise WSLCommandError(error_msg)

    def compare_versions(self, current: str, latest: str) -> int:
        """セマンティックバージョニングに基づいてバージョンを比較する.

        Args:
            current: 現在のバージョン
            latest: 最新のバージョン

        Returns:
            -1: current < latest
             0: current == latest
             1: current > latest

        Raises:
            ValueError: バージョン文字列の解析に失敗した場合
        """
        try:
            logger.debug(f"バージョン比較: {current} vs {latest}")

            current_version = self._parse_version(current)
            latest_version = self._parse_version(latest)

            # バージョン番号を順番に比較
            for i in range(max(len(current_version), len(latest_version))):
                current_part = current_version[i] if i < len(current_version) else 0
                latest_part = latest_version[i] if i < len(latest_version) else 0

                if current_part < latest_part:
                    logger.debug(f"比較結果: {current} < {latest}")
                    return -1
                elif current_part > latest_part:
                    logger.debug(f"比較結果: {current} > {latest}")
                    return 1

            logger.debug(f"比較結果: {current} == {latest}")
            return 0

        except Exception as e:
            error_msg = f"バージョン比較に失敗しました: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _parse_version(self, version_string: str) -> Tuple[int, ...]:
        """バージョン文字列を解析して数値のタプルに変換する.

        Args:
            version_string: バージョン文字列（例: "5.15.90.1-microsoft-standard-WSL2"）

        Returns:
            バージョン番号のタプル（例: (5, 15, 90, 1)）

        Raises:
            ValueError: バージョン文字列の解析に失敗した場合
        """
        try:
            # WSLカーネルバージョンから数値部分を抽出
            # 例: "5.15.90.1-microsoft-standard-WSL2" -> "5.15.90.1"
            version_match = re.match(r"^(\d+(?:\.\d+)*)", version_string)
            if not version_match:
                raise ValueError(f"バージョン文字列の形式が不正です: {version_string}")

            version_numbers = version_match.group(1)
            parts = version_numbers.split(".")

            # 各部分を整数に変換
            return tuple(int(part) for part in parts)

        except ValueError as e:
            if "invalid literal for int()" in str(e):
                raise ValueError(
                    f"バージョン文字列に無効な文字が含まれています: {version_string}"
                )
            raise

    def execute_build_script(
        self,
        script_path: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> bool:
        """WSL環境でカーネルビルドスクリプトを実行する.

        Args:
            script_path: ビルドスクリプトのパス。Noneの場合はデフォルトのビルド手順を実行
            progress_callback: ビルド進行状況を通知するコールバック関数

        Returns:
            ビルドが成功した場合True、失敗した場合False
        """
        try:
            logger.info("WSLカーネルビルドスクリプトを実行中...")

            if progress_callback:
                progress_callback("ビルドスクリプトを開始しています...")

            if script_path:
                # カスタムスクリプトを実行
                command = ["wsl", "bash", script_path]
                logger.info(f"カスタムビルドスクリプトを実行: {script_path}")
            else:
                # デフォルトのビルド手順を実行
                command = self._get_default_build_commands()
                logger.info("デフォルトビルド手順を実行")

            if progress_callback:
                progress_callback("ビルドコマンドを実行中...")

            # ビルドは時間がかかるのでタイムアウトを延長
            build_timeout = self.timeout * 20

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=build_timeout,
                check=True,
            )

            if progress_callback:
                progress_callback("ビルドが正常に完了しました")

            logger.info("ビルドスクリプトが正常に完了しました")
            logger.debug(f"ビルド出力: {result.stdout}")
            return True

        except subprocess.TimeoutExpired:
            error_msg = f"ビルドスクリプトがタイムアウトしました（{build_timeout}秒）"
            logger.error(error_msg)
            if progress_callback:
                progress_callback(f"エラー: {error_msg}")
            return False

        except subprocess.CalledProcessError as e:
            error_msg = f"ビルドスクリプトの実行に失敗しました: {e.stderr}"
            logger.error(error_msg)
            if progress_callback:
                progress_callback(f"エラー: {error_msg}")
            return False

        except FileNotFoundError:
            error_msg = (
                "WSLが見つかりません。WSLがインストールされているか確認してください"
            )
            logger.error(error_msg)
            if progress_callback:
                progress_callback(f"エラー: {error_msg}")
            return False

        except Exception as e:
            error_msg = (
                f"ビルドスクリプト実行中に予期しないエラーが発生しました: {str(e)}"
            )
            logger.error(error_msg)
            if progress_callback:
                progress_callback(f"エラー: {error_msg}")
            return False

    def _get_default_build_commands(self) -> list[str]:
        """デフォルトのビルドコマンドを取得する.

        Returns:
            デフォルトビルドコマンドのリスト
        """
        # 実際のWSLカーネルビルド手順の例
        # 注意: これは簡略化された例です。実際のビルドはより複雑になります
        return [
            "wsl",
            "bash",
            "-c",
            """
            echo "WSLカーネルビルドを開始します..." && \
            echo "必要な依存関係をチェック中..." && \
            echo "ビルド環境を準備中..." && \
            echo "カーネルソースをダウンロード中..." && \
            echo "カーネルをコンパイル中..." && \
            echo "ビルドが完了しました。" && \
            echo "注意: これはデモ用の簡略化されたビルドプロセスです。"
            """,
        ]

    def get_build_status(self) -> dict:
        """現在のビルド状況を取得する.

        Returns:
            ビルド状況を表す辞書
        """
        try:
            # WSL環境の基本情報を取得
            result = subprocess.run(
                ["wsl", "uname", "-a"],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=True,
            )

            system_info = result.stdout.strip()

            return {
                "wsl_available": True,
                "system_info": system_info,
                "build_tools_available": self._check_build_tools(),
                "last_check": "現在",
            }

        except Exception as e:
            logger.error(f"ビルド状況の取得に失敗しました: {str(e)}")
            return {
                "wsl_available": False,
                "system_info": None,
                "build_tools_available": False,
                "error": str(e),
                "last_check": "現在",
            }

    def _check_build_tools(self) -> bool:
        """ビルドに必要なツールが利用可能かチェックする.

        Returns:
            ビルドツールが利用可能な場合True
        """
        try:
            # 基本的なビルドツールの存在確認
            tools = ["gcc", "make", "git"]

            for tool in tools:
                subprocess.run(
                    ["wsl", "which", tool],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=True,
                )

            logger.debug("必要なビルドツールが利用可能です")
            return True

        except subprocess.CalledProcessError:
            logger.warning("一部のビルドツールが見つかりません")
            return False
        except Exception as e:
            logger.error(f"ビルドツールのチェックに失敗しました: {str(e)}")
            return False


class WSLCommandError(Exception):
    """WSLコマンド実行時のエラーを表す例外クラス."""

    pass
