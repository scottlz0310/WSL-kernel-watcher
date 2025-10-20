#!/usr/bin/env python3
"""クイックテスト（コンテナ不要）"""

import subprocess
import sys
from pathlib import Path


def test_docker_available():
    """Docker利用可能性テスト"""
    print("🐳 Docker利用可能性テスト...")
    
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ Docker利用可能: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker利用不可")
            return False
            
    except Exception as e:
        print(f"❌ Dockerテストエラー: {e}")
        return False


def test_compose_available():
    """Docker Compose利用可能性テスト"""
    print("📦 Docker Compose利用可能性テスト...")
    
    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ Docker Compose利用可能: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker Compose利用不可")
            return False
            
    except Exception as e:
        print(f"❌ Docker Composeテストエラー: {e}")
        return False


def test_project_structure():
    """プロジェクト構造テスト"""
    print("📁 プロジェクト構造テスト...")
    
    project_root = Path(__file__).parent.parent
    required_files = [
        "src/main.py",
        "src/config.py", 
        "src/github_watcher.py",
        "src/docker_notifier.py",
        "docker-compose.yml",
        "Dockerfile",
        "pyproject.toml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (project_root / file_path).exists():
            missing_files.append(file_path)
    
    if not missing_files:
        print("✅ プロジェクト構造正常")
        return True
    else:
        print(f"❌ 不足ファイル: {missing_files}")
        return False


if __name__ == "__main__":
    print("⚡ クイックテスト開始...")
    
    success = True
    
    success &= test_docker_available()
    success &= test_compose_available()
    success &= test_project_structure()
    
    if success:
        print("\n🎉 クイックテスト完了")
        sys.exit(0)
    else:
        print("\n💥 クイックテスト失敗")
        sys.exit(1)