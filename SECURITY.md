# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

セキュリティ脆弱性を発見した場合は、以下の手順で報告してください：

1. **公開しない**: GitHubのIssueやPRでは報告しないでください
2. **直接連絡**: リポジトリオーナーに直接連絡してください
3. **詳細情報**: 以下の情報を含めてください：
   - 脆弱性の詳細な説明
   - 再現手順
   - 影響範囲
   - 可能であれば修正案

## Security Considerations

このツールは以下のセキュリティ対策を実装しています：

- **GitHub API**: レート制限とリトライ機能
- **ローカル実行**: ネットワーク通信は最小限
- **設定ファイル**: 機密情報は含まない
- **依存関係**: Dependabotによる自動更新

## Response Timeline

- **確認**: 48時間以内
- **初期対応**: 1週間以内
- **修正リリース**: 重要度に応じて1-4週間以内
