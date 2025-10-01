# WSL Kernel Watcher - Makefile
# パッケージングと開発タスクの自動化

.PHONY: help install install-dev build clean test lint format check-format type-check pre-commit dist upload-test upload requirements lock sync

# デフォルトターゲット
help:
	@echo "WSL Kernel Watcher - 利用可能なコマンド:"
	@echo ""
	@echo "開発環境:"
	@echo "  install      - 本番用依存関係をインストール"
	@echo "  install-dev  - 開発用依存関係をインストール"
	@echo "  requirements - requirements.txtファイルを生成"
	@echo "  lock         - uv.lockファイルを更新"
	@echo "  sync         - 依存関係を同期"
	@echo ""
	@echo "コード品質:"
	@echo "  test         - テストを実行"
	@echo "  lint         - ruffでリントチェック"
	@echo "  format       - ruffとblackでコードフォーマット"
	@echo "  check-format - フォーマットチェック（CI用）"
	@echo "  type-check   - mypyで型チェック"
	@echo "  pre-commit   - pre-commitフックを実行"
	@echo ""
	@echo "ビルドと配布:"
	@echo "  build        - パッケージをビルド"
	@echo "  clean        - ビルド成果物を削除"
	@echo "  dist         - 配布用パッケージを作成"
	@echo "  upload-test  - TestPyPIにアップロード"
	@echo "  upload       - PyPIにアップロード"
	@echo ""
	@echo "実行:"
	@echo "  run          - アプリケーションを実行"

# 依存関係管理
install:
	uv sync --no-dev

install-dev:
	uv sync

requirements:
	uv pip compile pyproject.toml -o requirements.txt
	uv pip compile pyproject.toml --group dev -o requirements-dev.txt

lock:
	uv lock

sync:
	uv sync

# コード品質
test:
	uv run pytest

test-cov:
	uv run pytest --cov=src --cov-report=html --cov-report=term-missing

test-e2e:
	uv run pytest tests/test_e2e_*.py -v

test-notification:
	uv run pytest tests/test_e2e_notification.py -v -s

lint:
	uv run ruff check .

format:
	uv run ruff format .
	uv run black .

check-format:
	uv run ruff format --check .
	uv run black --check .

type-check:
	uv run mypy src/

pre-commit:
	uv run pre-commit run --all-files

# ビルドと配布
build: clean
	uv build

clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

dist: build
	@echo "配布用パッケージが dist/ ディレクトリに作成されました"
	@ls -la dist/

upload-test: build
	uv run twine upload --repository testpypi dist/*

upload: build
	uv run twine upload dist/*

# 実行
run:
	uv run python -m src.main

# インストール・アンインストール
install-script:
	@echo "自動インストールスクリプトを実行します..."
	@powershell -ExecutionPolicy Bypass -File scripts/install.ps1

uninstall-script:
	@echo "自動アンインストールスクリプトを実行します..."
	@powershell -ExecutionPolicy Bypass -File scripts/uninstall.ps1

install-pipx:
	pipx install .

uninstall-pipx:
	pipx uninstall wsl-kernel-watcher

# 設定ファイル
config:
	@if not exist config.toml (copy config.template.toml config.toml && echo "設定ファイル config.toml を作成しました。")

# 開発用ショートカット
dev-setup: install-dev config
	uv run pre-commit install

check-all: lint check-format type-check test

# CI用ターゲット
ci-test: install-dev check-all

# バージョン確認
version:
	@python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"

# パッケージ情報
info:
	@echo "WSL Kernel Watcher v$(shell python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")"
	@echo "Python: $(shell python --version)"
	@echo "Platform: Windows"
	@echo "Dependencies: $(shell uv pip list --format=freeze | wc -l) packages"