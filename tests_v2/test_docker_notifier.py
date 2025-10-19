"""Docker通知モジュールのテスト"""

import subprocess
from unittest.mock import Mock, patch

from src_v2.docker_notifier import DockerNotifier


class TestDockerNotifier:
    """DockerNotifierクラスのテスト"""

    def setup_method(self):
        """テストセットアップ"""
        self.notifier = DockerNotifier()

    @patch("subprocess.run")
    def test_send_notification_success(self, mock_run):
        """通知送信成功テスト"""
        # モック設定
        mock_run.return_value = Mock(returncode=0, stderr="")

        # テスト実行
        result = self.notifier.send_notification("テストタイトル", "テストメッセージ")

        # 検証
        assert result is True
        mock_run.assert_called_once()

        # コマンド引数の検証
        call_args = mock_run.call_args
        assert "wsl.exe" in call_args[0][0]
        assert "powershell.exe" in call_args[0][0]

    @patch("subprocess.run")
    def test_send_notification_failure(self, mock_run):
        """通知送信失敗テスト"""
        # モック設定
        mock_run.return_value = Mock(returncode=1, stderr="エラーメッセージ")

        # テスト実行
        result = self.notifier.send_notification("テストタイトル", "テストメッセージ")

        # 検証
        assert result is False

    @patch("subprocess.run")
    def test_send_notification_exception(self, mock_run):
        """通知送信例外テスト"""
        # モック設定
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)

        # テスト実行
        result = self.notifier.send_notification("テストタイトル", "テストメッセージ")

        # 検証
        assert result is False

    @patch.object(DockerNotifier, "send_notification")
    def test_notify_kernel_update(self, mock_send):
        """カーネル更新通知テスト"""
        # モック設定
        mock_send.return_value = True

        # テスト実行
        result = self.notifier.notify_kernel_update("5.15.95.1", "5.15.90.1")

        # 検証
        assert result is True
        mock_send.assert_called_once()

        # 引数の検証
        call_args = mock_send.call_args[0]
        assert "WSL2カーネル更新通知" in call_args[0]
        assert "5.15.95.1" in call_args[1]
        assert "5.15.90.1" in call_args[1]
