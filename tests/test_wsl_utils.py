"""WSLUtilsクラスのテストモジュール."""

import subprocess
from unittest.mock import Mock, patch

import pytest

from src.wsl_utils import WSLCommandError, WSLUtils


class TestWSLUtils:
    """WSLUtilsクラスのテストクラス."""

    def setup_method(self):
        """各テストメソッドの前に実行される初期化処理."""
        self.wsl_utils = WSLUtils(timeout=10)

    @patch("subprocess.run")
    def test_get_current_kernel_version_success(self, mock_run):
        """カーネルバージョン取得の正常系テスト."""
        # モックの設定
        mock_result = Mock()
        mock_result.stdout = "5.15.90.1-microsoft-standard-WSL2\n"
        mock_run.return_value = mock_result

        # テスト実行
        result = self.wsl_utils.get_current_kernel_version()

        # 検証
        assert result == "5.15.90.1-microsoft-standard-WSL2"
        mock_run.assert_called_once_with(
            ["wsl", "uname", "-r"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )

    @patch("subprocess.run")
    def test_get_current_kernel_version_timeout(self, mock_run):
        """カーネルバージョン取得のタイムアウトテスト."""
        # モックの設定
        mock_run.side_effect = subprocess.TimeoutExpired(["wsl", "uname", "-r"], 10)

        # テスト実行と検証
        with pytest.raises(WSLCommandError, match="WSLコマンドがタイムアウトしました"):
            self.wsl_utils.get_current_kernel_version()

    @patch("subprocess.run")
    def test_get_current_kernel_version_command_error(self, mock_run):
        """カーネルバージョン取得のコマンドエラーテスト."""
        # モックの設定
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["wsl", "uname", "-r"], stderr="WSL not found"
        )

        # テスト実行と検証
        with pytest.raises(WSLCommandError, match="WSLコマンドの実行に失敗しました"):
            self.wsl_utils.get_current_kernel_version()

    @patch("subprocess.run")
    def test_get_current_kernel_version_file_not_found(self, mock_run):
        """カーネルバージョン取得のファイル未発見テスト."""
        # モックの設定
        mock_run.side_effect = FileNotFoundError()

        # テスト実行と検証
        with pytest.raises(WSLCommandError, match="WSLが見つかりません"):
            self.wsl_utils.get_current_kernel_version()

    def test_compare_versions_current_less_than_latest(self):
        """バージョン比較テスト: current < latest."""
        result = self.wsl_utils.compare_versions("5.15.90.1", "5.15.90.2")
        assert result == -1

    def test_compare_versions_current_greater_than_latest(self):
        """バージョン比較テスト: current > latest."""
        result = self.wsl_utils.compare_versions("5.15.91.1", "5.15.90.2")
        assert result == 1

    def test_compare_versions_equal(self):
        """バージョン比較テスト: current == latest."""
        result = self.wsl_utils.compare_versions("5.15.90.1", "5.15.90.1")
        assert result == 0

    def test_compare_versions_different_lengths(self):
        """バージョン比較テスト: 異なる長さのバージョン."""
        result = self.wsl_utils.compare_versions("5.15.90", "5.15.90.1")
        assert result == -1

        result = self.wsl_utils.compare_versions("5.15.90.1", "5.15.90")
        assert result == 1

    def test_compare_versions_with_suffix(self):
        """バージョン比較テスト: サフィックス付きバージョン."""
        result = self.wsl_utils.compare_versions(
            "5.15.90.1-microsoft-standard-WSL2", "5.15.90.2-microsoft-standard-WSL2"
        )
        assert result == -1

    def test_parse_version_normal(self):
        """バージョン解析テスト: 通常のバージョン."""
        result = self.wsl_utils._parse_version("5.15.90.1")
        assert result == (5, 15, 90, 1)

    def test_parse_version_with_suffix(self):
        """バージョン解析テスト: サフィックス付きバージョン."""
        result = self.wsl_utils._parse_version("5.15.90.1-microsoft-standard-WSL2")
        assert result == (5, 15, 90, 1)

    def test_parse_version_invalid_format(self):
        """バージョン解析テスト: 無効な形式."""
        with pytest.raises(ValueError, match="バージョン文字列の形式が不正です"):
            self.wsl_utils._parse_version("invalid-version")

    def test_parse_version_invalid_number(self):
        """バージョン解析テスト: 無効な数値."""
        with pytest.raises(ValueError, match="バージョン文字列の形式が不正です"):
            self.wsl_utils._parse_version("a.15.90.1")

    @patch("subprocess.run")
    def test_execute_build_script_success_default(self, mock_run):
        """ビルドスクリプト実行の正常系テスト（デフォルト）."""
        # モックの設定
        mock_result = Mock()
        mock_result.stdout = "ビルドが完了しました。"
        mock_run.return_value = mock_result

        # テスト実行
        result = self.wsl_utils.execute_build_script()

        # 検証
        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "wsl"
        assert args[1] == "bash"
        assert args[2] == "-c"

    @patch("subprocess.run")
    def test_execute_build_script_success_custom(self, mock_run):
        """ビルドスクリプト実行の正常系テスト（カスタム）."""
        # モックの設定
        mock_result = Mock()
        mock_result.stdout = "カスタムビルドが完了しました。"
        mock_run.return_value = mock_result

        # テスト実行
        result = self.wsl_utils.execute_build_script("/path/to/build.sh")

        # 検証
        assert result is True
        mock_run.assert_called_once_with(
            ["wsl", "bash", "/path/to/build.sh"],
            capture_output=True,
            text=True,
            timeout=200,  # timeout * 20
            check=True,
        )

    @patch("subprocess.run")
    def test_execute_build_script_with_progress_callback(self, mock_run):
        """ビルドスクリプト実行のプログレスコールバックテスト."""
        # モックの設定
        mock_result = Mock()
        mock_result.stdout = "ビルドが完了しました。"
        mock_run.return_value = mock_result

        progress_callback = Mock()

        # テスト実行
        result = self.wsl_utils.execute_build_script(
            progress_callback=progress_callback
        )

        # 検証
        assert result is True
        assert progress_callback.call_count == 3
        progress_callback.assert_any_call("ビルドスクリプトを開始しています...")
        progress_callback.assert_any_call("ビルドコマンドを実行中...")
        progress_callback.assert_any_call("ビルドが正常に完了しました")

    @patch("subprocess.run")
    def test_execute_build_script_timeout(self, mock_run):
        """ビルドスクリプト実行のタイムアウトテスト."""
        # モックの設定
        mock_run.side_effect = subprocess.TimeoutExpired(["wsl", "bash"], 200)

        # テスト実行
        result = self.wsl_utils.execute_build_script()

        # 検証
        assert result is False

    @patch("subprocess.run")
    def test_execute_build_script_command_error(self, mock_run):
        """ビルドスクリプト実行のコマンドエラーテスト."""
        # モックの設定
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["wsl", "bash"], stderr="Build failed"
        )

        # テスト実行
        result = self.wsl_utils.execute_build_script()

        # 検証
        assert result is False

    @patch("subprocess.run")
    def test_execute_build_script_file_not_found(self, mock_run):
        """ビルドスクリプト実行のファイル未発見テスト."""
        # モックの設定
        mock_run.side_effect = FileNotFoundError()

        # テスト実行
        result = self.wsl_utils.execute_build_script()

        # 検証
        assert result is False

    @patch("subprocess.run")
    def test_get_build_status_success(self, mock_run):
        """ビルド状況取得の正常系テスト."""
        # モックの設定
        mock_run.side_effect = [
            # uname -a の結果
            Mock(
                stdout="Linux DESKTOP-ABC 5.15.90.1-microsoft-standard-WSL2 #1 SMP x86_64 GNU/Linux\n"
            ),
            # which gcc の結果
            Mock(stdout="/usr/bin/gcc\n"),
            # which make の結果
            Mock(stdout="/usr/bin/make\n"),
            # which git の結果
            Mock(stdout="/usr/bin/git\n"),
        ]

        # テスト実行
        result = self.wsl_utils.get_build_status()

        # 検証
        assert result["wsl_available"] is True
        assert "Linux DESKTOP-ABC" in result["system_info"]
        assert result["build_tools_available"] is True
        assert result["last_check"] == "現在"

    @patch("subprocess.run")
    def test_get_build_status_error(self, mock_run):
        """ビルド状況取得のエラーテスト."""
        # モックの設定
        mock_run.side_effect = subprocess.CalledProcessError(1, ["wsl", "uname", "-a"])

        # テスト実行
        result = self.wsl_utils.get_build_status()

        # 検証
        assert result["wsl_available"] is False
        assert result["system_info"] is None
        assert result["build_tools_available"] is False
        assert "error" in result

    @patch("subprocess.run")
    def test_check_build_tools_success(self, mock_run):
        """ビルドツールチェックの正常系テスト."""
        # モックの設定
        mock_run.return_value = Mock(stdout="/usr/bin/tool\n")

        # テスト実行
        result = self.wsl_utils._check_build_tools()

        # 検証
        assert result is True
        assert mock_run.call_count == 3  # gcc, make, git

    @patch("subprocess.run")
    def test_check_build_tools_missing_tool(self, mock_run):
        """ビルドツールチェックのツール不足テスト."""
        # モックの設定
        mock_run.side_effect = subprocess.CalledProcessError(1, ["wsl", "which", "gcc"])

        # テスト実行
        result = self.wsl_utils._check_build_tools()

        # 検証
        assert result is False

    def test_get_default_build_commands(self):
        """デフォルトビルドコマンド取得テスト."""
        result = self.wsl_utils._get_default_build_commands()

        assert isinstance(result, list)
        assert result[0] == "wsl"
        assert result[1] == "bash"
        assert result[2] == "-c"
        assert "WSLカーネルビルドを開始します" in result[3]


class TestWSLCommandError:
    """WSLCommandErrorクラスのテストクラス."""

    def test_wsl_command_error_creation(self):
        """WSLCommandError例外の作成テスト."""
        error_message = "テストエラーメッセージ"
        error = WSLCommandError(error_message)

        assert str(error) == error_message
        assert isinstance(error, Exception)

    def test_wsl_command_error_inheritance(self):
        """WSLCommandError例外の継承テスト."""
        error = WSLCommandError("テスト")

        assert isinstance(error, Exception)
        assert isinstance(error, WSLCommandError)
