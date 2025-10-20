# WSL Kernel Watcher v2.1.0 - Docker常駐版
# 使用方法: make <target>

.PHONY: help start stop restart build clean logs status test test-notification dev-setup lint format check-all

# デフォルトターゲット
help: ## 使用可能なコマンドを表示
	@echo "WSL Kernel Watcher v2.0.0 - 使用可能なコマンド:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "クイックスタート:"
	@echo "  make start           # 監視開始"
	@echo "  make logs            # ログ確認"
	@echo "  make stop            # 監視停止"
	@echo ""
	@echo "テスト:"
	@echo "  make test               # 全操作系テスト"
	@echo "  make test-full-flow     # 完全フローテスト"
	@echo "  make test-version-change # バージョン変更通知テスト"
	@echo "  make test-interactive   # インタラクティブテスト"

# === 基本操作 ===
start: ## Docker常駐監視を開始
	@echo "🚀 WSL Kernel Watcher 開始中..."
	docker-compose up -d
	@echo "✅ 監視開始完了"
	@echo "📝 ログ確認: make logs"

stop: ## Docker常駐監視を停止
	@echo "🛑 WSL Kernel Watcher 停止中..."
	docker-compose down
	@echo "✅ 停止完了"

restart: ## Docker常駐監視を再起動
	@echo "🔄 WSL Kernel Watcher 再起動中..."
	docker-compose restart
	@echo "✅ 再起動完了"

# === ビルド・クリーンアップ ===
build: ## Dockerイメージをビルド
	@echo "🐳 Dockerイメージビルド中..."
	docker-compose build --no-cache
	@echo "✅ ビルド完了"

clean: ## 全てのDockerリソースをクリーンアップ
	@echo "🧹 クリーンアップ中..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "✅ クリーンアップ完了"

# === 監視・ログ ===
logs: ## リアルタイムログを表示
	@echo "📝 ログ表示中 (Ctrl+C で終了)..."
	docker-compose logs -f

status: ## コンテナ状態を確認
	@echo "📊 コンテナ状態:"
	docker-compose ps
	@echo ""
	@echo "💾 リソース使用量:"
	docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# === テスト ===
test: ## 操作系テスト実行（全テスト）
	@echo "🧪 操作系テスト実行中..."
	@echo "⚠️ systemd監視サービスが必要です: sudo systemctl status wsl-kernel-watcher-monitor"
	@echo "🐳 テスト用コンテナ準備中..."
	docker-compose up -d
	@sleep 3
	-cd interactive-tests && uv run python run_all_tests.py
	@echo "🧹 テスト後クリーンアップ..."
	docker-compose down
	@echo "✅ テスト完了（systemd監視サービスが必要）"
	@echo "🔄 完全フローテスト: make test-full-flow"

test-notification: ## 通知テストのみ実行
	@echo "🔔 通知テスト実行中..."
	cd interactive-tests && uv run python test_wsl_notification_standalone.py

test-interactive: ## インタラクティブ通知テスト（クリック確認付き）
	@echo "🎯 インタラクティブ通知テスト実行中..."
	@echo "⚠️ このテストでは実際に通知をクリックして確認します"
	cd interactive-tests && uv run python test_interactive_notification.py

test-full-flow: ## 完全フロー確認（Docker→systemd→通知→クリーンアップ）
	@echo "🔄 完全フロー確認テスト実行中..."
	@echo "⚠️ Docker→WSLホスト→systemd→通知の全フローを確認します"
	@echo "🐳 テスト用コンテナ準備中..."
	docker-compose up -d
	@sleep 3
	cd interactive-tests && uv run python test_full_flow.py
	@echo "🧹 テスト後クリーンアップ..."
	docker-compose down

test-version-change: ## バージョン変更通知テスト（模擬的カーネルダウングレード）
	@echo "🔄 バージョン変更通知テスト実行中..."
	@echo "⚠️ 模擬的なカーネルダウングレードで通知動作を確認します"
	@echo "🐳 テスト用コンテナ準備中..."
	docker-compose up -d
	@sleep 3
	cd interactive-tests && uv run python test_version_change.py
	@echo "🧹 テスト後クリーンアップ..."
	docker-compose down

test-quick: ## クイックテスト（コンテナ不要）
	@echo "⚡ クイックテスト実行中..."
	cd interactive-tests && uv run python test_quick.py

test-core: ## コア機能テスト（WSL通知以外）
	@echo "🔧 コア機能テスト実行中..."
	@echo "🐳 テスト用コンテナ準備中..."
	docker-compose up -d
	@sleep 3
	cd interactive-tests && uv run python test_core.py
	@echo "🧹 テスト後クリーンアップ..."
	docker-compose down

# === 開発用 ===
dev-setup: ## 開発環境セットアップ
	@echo "🔧 開発環境セットアップ中..."
	uv sync --group dev
	uv run pre-commit install
	@echo "✅ 開発環境準備完了"

lint: ## コードリント実行
	@echo "🔍 リント実行中..."
	uv run ruff check .
	uv run mypy src/

format: ## コードフォーマット実行
	@echo "✨ フォーマット実行中..."
	uv run ruff format .

check-all: ## 全品質チェック実行
	@echo "🔬 全品質チェック実行中..."
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy src/
	uv run pytest tests/ --cov=src
	@echo "✅ 全チェック完了"

# === 設定・情報 ===
config: ## 現在の設定を表示
	@echo "⚙️ 現在の設定:"
	@echo "REPOSITORY_URL: $$(printenv REPOSITORY_URL || echo 'microsoft/WSL2-Linux-Kernel')"
	@echo "CHECK_INTERVAL_MINUTES: $$(printenv CHECK_INTERVAL_MINUTES || echo '30')"
	@echo "LOG_LEVEL: $$(printenv LOG_LEVEL || echo 'INFO')"
	@echo "GITHUB_TOKEN: $$([ -n "$$GITHUB_TOKEN" ] && echo '設定済み' || echo '未設定')"

version: ## バージョン情報表示
	@echo "WSL Kernel Watcher v2.1.0 - Docker常駐版"
	@echo "Docker: $$(docker --version)"
	@echo "Docker Compose: $$(docker-compose --version)"

# === 便利コマンド ===
shell: ## コンテナ内でシェル実行
	@echo "🐚 コンテナシェル起動..."
	docker-compose exec wsl-kernel-watcher /bin/bash

install-monitor: ## systemd監視サービスをインストール
	@echo "🔧 systemd監視サービスインストール中..."
	@echo "⚠️ sudo権限が必要です"
	bash install-monitor.sh

uninstall-monitor: ## systemd監視サービスをアンインストール
	@echo "🗑️ systemd監視サービスアンインストール中..."
	@echo "⚠️ sudo権限が必要です"
	bash uninstall-monitor.sh

oneshot: ## 一回だけチェック実行
	@echo "🎯 ワンショット実行中..."
	docker-compose run --rm wsl-kernel-watcher uv run python -c "from src.github_watcher import GitHubWatcher; from src.config import ConfigManager; config = ConfigManager.load(); watcher = GitHubWatcher(config.repository_url); release = watcher.get_latest_stable_release(); print(f'最新版: {release.tag_name if release else \"取得失敗\"}')"