#!/usr/bin/env python3
"""GitHub API接続確認テスト"""

import subprocess
import sys
from pathlib import Path


def test_github_connection():
    """GitHub API接続テスト"""
    print("🐙 GitHub API接続テスト開始...")
    
    project_root = Path(__file__).parent.parent
    
    test_script = '''
from src.github_watcher import GitHubWatcher
import logging
logging.basicConfig(level=logging.INFO)

try:
    watcher = GitHubWatcher()
    release = watcher.get_latest_stable_release()
    
    if release:
        print(f"✅ 最新リリース取得成功: {release.tag_name}")
        print(f"📅 公開日: {release.published_at}")
        print(f"🔗 URL: {release.html_url}")
    else:
        print("❌ リリース情報が取得できませんでした")
        
except Exception as e:
    print(f"❌ GitHub API接続エラー: {e}")
    raise
'''
    
    try:
        result = subprocess.run([
            "docker-compose", "run", "--rm",
            "wsl-kernel-watcher",
            "uv", "run", "python", "-c", test_script
        ], cwd=project_root, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ GitHub API接続失敗: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ GitHub APIテストタイムアウト")
        return False
    except Exception as e:
        print(f"❌ GitHub APIテストエラー: {e}")
        return False


def test_rate_limit_handling():
    """レート制限処理テスト"""
    print("⏱️ レート制限処理テスト...")
    
    project_root = Path(__file__).parent.parent
    
    test_script = '''
from src.github_watcher import GitHubWatcher
import requests

watcher = GitHubWatcher()
url = f"{watcher.base_url}/repos/{watcher.repository_url}/releases"

try:
    response = watcher.session.get(url)
    remaining = response.headers.get("X-RateLimit-Remaining", "不明")
    limit = response.headers.get("X-RateLimit-Limit", "不明")
    
    print(f"✅ レート制限情報取得成功")
    print(f"📊 制限: {limit}リクエスト/時間")
    print(f"📊 残り: {remaining}リクエスト")
    
    if int(remaining) < 10:
        print("⚠️ レート制限接近中")
    
except Exception as e:
    print(f"❌ レート制限確認エラー: {e}")
    raise
'''
    
    try:
        result = subprocess.run([
            "docker-compose", "run", "--rm",
            "wsl-kernel-watcher",
            "uv", "run", "python", "-c", test_script
        ], cwd=project_root, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ レート制限テスト失敗: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ レート制限テストエラー: {e}")
        return False


def test_prerelease_filtering():
    """プレリリース除外テスト"""
    print("🔍 プレリリース除外テスト...")
    
    project_root = Path(__file__).parent.parent
    
    test_script = '''
from src.github_watcher import GitHubWatcher

watcher = GitHubWatcher()

# テスト用のプレリリースデータ
test_releases = [
    {"tag_name": "v1.0.0-rc1", "prerelease": True},
    {"tag_name": "v1.0.0-beta", "prerelease": False},
    {"tag_name": "v1.0.0", "prerelease": False},
]

for release_data in test_releases:
    is_pre = watcher._is_prerelease(release_data)
    tag = release_data["tag_name"]
    
    if "rc" in tag or "beta" in tag:
        expected = True
    else:
        expected = False
        
    if is_pre == expected:
        print(f"✅ {tag}: 正しく判定 (プレリリース={is_pre})")
    else:
        print(f"❌ {tag}: 判定エラー (期待={expected}, 実際={is_pre})")
'''
    
    try:
        result = subprocess.run([
            "docker-compose", "run", "--rm",
            "wsl-kernel-watcher",
            "uv", "run", "python", "-c", test_script
        ], cwd=project_root, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ プレリリース除外テスト失敗: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ プレリリース除外テストエラー: {e}")
        return False


if __name__ == "__main__":
    success = True
    
    success &= test_github_connection()
    success &= test_rate_limit_handling()
    success &= test_prerelease_filtering()
    
    if success:
        print("\n🎉 GitHub APIテスト完了")
        sys.exit(0)
    else:
        print("\n💥 GitHub APIテスト失敗")
        sys.exit(1)