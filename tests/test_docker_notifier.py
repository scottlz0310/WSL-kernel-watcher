"""Docker通知モジュールのテスト"""

from unittest.mock import Mock, patch

from src.docker_notifier import DockerNotifier


class TestDockerNotifier:
    """DockerNotifierクラスのテスト"""

    def setup_method(self):
        """テストセットアップ"""
        self.notifier = DockerNotifier()

    @patch("os.path.exists")
    @patch("os.chmod")
    @patch("builtins.open")
    @patch("time.sleep")
    def test_send_notification_success(
        self, mock_sleep, mock_open, mock_chmod, mock_exists
    ):
        """通知送信成功テスト"""
        # モック設定
        mock_exists.return_value = False  # スクリプトが削除された（実行完了）
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        # テスト実行
        result = self.notifier.send_notification("テストタイトル", "テストメッセージ")

        # 検証
        assert result is True
        mock_open.assert_called_once()
        mock_chmod.assert_called_once()
        mock_sleep.assert_called_once_with(2)
        mock_exists.assert_called_once()

    @patch("os.path.exists")
    @patch("os.chmod")
    @patch("builtins.open")
    @patch("time.sleep")
    def test_send_notification_failure(
        self, mock_sleep, mock_open, mock_chmod, mock_exists
    ):
        """通知送信失敗テスト"""
        # モック設定
        mock_exists.return_value = True  # スクリプトが残っている（実行失敗）
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        # テスト実行
        result = self.notifier.send_notification("テストタイトル", "テストメッセージ")

        # 検証
        assert result is False

    @patch("builtins.open")
    def test_send_notification_exception(self, mock_open):
        """通知送信例外テスト"""
        # モック設定
        mock_open.side_effect = OSError("ファイルアクセスエラー")

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
