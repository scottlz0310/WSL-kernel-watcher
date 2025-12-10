## リポジトリガイドライン

### 日本語を使用すること
このリポジトリにおけるドキュメントおよびコードコメントは日本語で記述してください。英語の使用は避け、すべてのコミュニケーションを日本語で行うよう徹底してください。

### プロジェクト構造とモジュール分割
WSL Kernel Watcher は `winui3/WSLKernelWatcher.WinUI3` 配下に含まれます。主な機能は `Services/`（間隔ロジックや設定）、`ViewModels/`、`Helpers/` に分割されています。テストは `winui3/WSLKernelWatcher.WinUI3.Tests` に配置されています。デプロイ用スクリプトや CI フックは `scripts/`（PowerShell）と `.ci-helper/` にあります。`wsl_watcher_icon.png` のようなアセットや、パッケージングに関する補足は `docs/` に置いてください。OS 固有の実験ノートは `windows_only_plan/` にまとめて、ソリューション直下が散らからないようにしてください。

### ビルド、テスト、および開発コマンド
一度だけ次のコマンドを実行して、pre-commit フックをインストールし NuGet パッケージを復元してください:
```powershell
pwsh -File .\scripts\setup-dev.ps1
```
WinUI 3 アプリは Visual Studio の Developer PowerShell から MSBuild でビルドしてください（`dotnet build` は使用しない）:
```powershell
msbuild winui3\WSLKernelWatcher.WinUI3\WSLKernelWatcher.WinUI3.csproj /p:Configuration=Release /p:Platform=x64
```
テストは xUnit で `dotnet test winui3/WSLKernelWatcher.WinUI3.sln` を実行します。CI と同じフォーマットルールを適用するためにコミット前に `dotnet format winui3/WSLKernelWatcher.WinUI3.sln` を実行してください。ビルド済みバイナリをタスクスケジューラーに登録するには:
```powershell
.\scripts\install.ps1 -StartMinimized
```
登録解除は `.\scripts\uninstall.ps1` を使用します。

### コーディングスタイルと命名規則
このソリューションは `.editorconfig` を適用しています：文字コード UTF-8、改行 CRLF、インデントは 4 スペース（XML/JSON/YAML は 2 スペース）、ファイルスコープの名前空間、波括弧は改行に置く、などです。インターフェイス名は `I` で始め、プライベートフィールドは先頭にアンダースコアを付けます。`TreatWarningsAsErrors=true` のため、警告はビルド失敗につながります。型推論が明確な場合を除き明示的な型を使用してください。`using` ディレクティブは名前空間外に置き、StyleCop/Roslyn アナライザや `SecurityCodeScan` を CI で有効にしています。

### テストガイドライン
xUnit と FluentAssertions を用いて `winui3/WSLKernelWatcher.WinUI3.Tests` でテストを実行します。テスト名のパターンは `MethodName_ShouldExpectation` を踏襲し、範囲検証には `[Theory]` とデータ行を活用してください（例: `SettingsServiceTests.cs`）。カバレッジは行/分岐/メソッドの各項目で 80% 以上を維持する必要があります（Codecov が PR をゲートします）。テストが一時ファイルを作成する場合は `IDisposable.Dispose` で必ずクリーンアップしてください。

### コミットとプルリクエストのガイドライン
コミットメッセージは既存の Conventional Commit（例: `feat:`, `chore:`, `fix:`, `docs:`） に従ってください。各コミットは論理的なスコープにまとめ、フックが通ることを確認してください。`--no-verify` は PR 内で正当化できる場合のみ使用してください。PR には次を含めてください: 明確な概要、関連する GitHub issue や議論へのリンク、UX 変更の場合はスクリーンショットや GIF、そしてテスト（`dotnet test`、手動のトレイ動作確認など）の説明。CI がグリーンであることを確認し、機密修正は `SECURITY.md` に従っているか確認した上でレビューを依頼してください。

### セキュリティと設定のヒント
シークレット（API トークン等）はソースコードに含めないでください。ユーザ固有の設定は `%LocalAppData%\WSLKernelWatcher\settings.json` を使用することを推奨します。スクリプトは Windows ホストを前提としているため、タスクスケジューラーへ登録・変更する場合は管理者権限の PowerShell から実行してください。依存関係は Renovate 等で最新化してください。ただし、`winui3/Directory.Packages.props` でのマニフェスト変更は WinUI SDK の互換性を壊す恐れがあるため慎重にレビューしてください。
