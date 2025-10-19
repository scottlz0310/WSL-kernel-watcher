#!/usr/bin/env python3
"""全操作系テスト実行スクリプト"""

import subprocess
import sys
from pathlib import Path


def run_test(test_name: str, test_file: str) -> bool:
    """個別テスト実行"""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name} 実行中...")
    print(f"{'='*60}")
    
    test_path = Path(__file__).parent / test_file
    
    try:
        result = subprocess.run([sys.executable, str(test_path)], timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {test_name} 成功")
            return True
        else:
            print(f"❌ {test_name} 失敗")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {test_name} タイムアウト")
        return False
    except Exception as e:
        print(f"💥 {test_name} エラー: {e}")
        return False


def main():
    """メイン実行関数"""
    print("🚀 WSL Kernel Watcher v2 操作系テスト開始")
    print("=" * 60)
    
    tests = [
        ("Dockerビルド確認", "test_docker_build.py"),
        ("コンテナ起動確認", "test_container_startup.py"),
        ("GitHub API接続確認", "test_github_api.py"),
        ("エラーハンドリング確認", "test_error_handling.py"),
        ("WSL経由通知確認", "test_wsl_notification.py"),
    ]
    
    results = {}
    
    for test_name, test_file in tests:
        results[test_name] = run_test(test_name, test_file)
    
    # 結果サマリー
    print(f"\n{'='*60}")
    print("📊 テスト結果サマリー")
    print(f"{'='*60}")
    
    success_count = 0
    total_count = len(results)
    
    for test_name, success in results.items():
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"{test_name}: {status}")
        if success:
            success_count += 1
    
    print(f"\n📈 成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("\n🎉 全テスト成功！")
        return 0
    else:
        print(f"\n💥 {total_count - success_count}個のテストが失敗しました")
        return 1


if __name__ == "__main__":
    sys.exit(main())