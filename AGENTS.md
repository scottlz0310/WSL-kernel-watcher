# Repository Guidelines

## Use Japanese Language
このリポジトリのドキュメントとコードコメントは日本語で記述してください。英語の使用は避け、すべてのコミュニケーションを日本語で行うことを徹底してください。

## Project Structure & Module Organization
WSL Kernel Watcher lives under `winui3/WSLKernelWatcher.WinUI3`, with features split into `Services/` (interval logic, settings), `ViewModels/`, and `Helpers/`. Tests sit beside the app in `winui3/WSLKernelWatcher.WinUI3.Tests`. Deployment tooling and hooks are in `scripts/` (PowerShell) and `.ci-helper/`, while assets such as `wsl_watcher_icon.png` and supplemental notes in `docs/` support packaging. Keep experimental notebooks or OS-specific plans inside `windows_only_plan/` to avoid polluting the solution.

## Build, Test, and Development Commands
Run `pwsh -File .\scripts\setup-dev.ps1` once to install pre-commit hooks and restore NuGet packages. Build the WinUI 3 app via a Visual Studio Developer PowerShell using:
```powershell
msbuild winui3\WSLKernelWatcher.WinUI3\WSLKernelWatcher.WinUI3.csproj /p:Configuration=Release /p:Platform=x64
```
Skip `dotnet build`; WinUI 3 requires full MSBuild. Run `dotnet test winui3/WSLKernelWatcher.WinUI3.sln` for the xUnit suite, and `dotnet format winui3/WSLKernelWatcher.WinUI3.sln` before committing to match CI. Use `.\scripts\install.ps1 -StartMinimized` to register the built binary with Task Scheduler; `.\scripts\uninstall.ps1` cleans it.

## Coding Style & Naming Conventions
The solution enforces `.editorconfig`: UTF-8, CRLF, 4-space indentation (2 for XML/JSON/YAML), file-scoped namespaces, and braces on new lines. Interfaces start with `I`, private fields use a leading underscore, and warnings fail builds because `TreatWarningsAsErrors=true`. Prefer explicit types except when the type is obvious, `using` directives belong outside namespaces, and StyleCop/Roslyn analyzers plus `SecurityCodeScan` run in CI.

## Testing Guidelines
xUnit and FluentAssertions power the suite under `winui3/WSLKernelWatcher.WinUI3.Tests`. Follow the pattern `MethodName_ShouldExpectation` and favor `[Theory]` data rows when validating ranges (see `SettingsServiceTests.cs`). Coverage must stay at or above 80% line/branch/method; Codecov reports gate PRs. When tests create temp files, clean them in `IDisposable.Dispose` like existing fixtures.

## Commit & Pull Request Guidelines
Adopt the existing Conventional Commit shorthand (`feat:`, `chore:`, `fix:`, `docs:`) visible in `git log`. Each commit should be scoped to a logical unit and pass hooks; use `--no-verify` only when justified in the PR. PRs need: clear summary, linked GitHub issue or discussion, screenshots/GIFs for UX changes, and notes on testing (`dotnet test`, manual tray smoke test). Ensure CI is green and reference `SECURITY.md` for disclosure-sensitive fixes before requesting review.

## Security & Configuration Tips
Secrets never belong in source; prefer user-level settings at `%LocalAppData%\WSLKernelWatcher\settings.json`. Scripts assume a Windows host—call them from an elevated PowerShell when editing Task Scheduler entries. Keep dependencies updated via Renovate, but review manifest changes in `winui3/Directory.Packages.props` to avoid breaking WinUI SDK compatibility.
