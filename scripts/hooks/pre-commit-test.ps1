<#
.SYNOPSIS
    Pre-push hook to run tests with coverage.

.DESCRIPTION
    This script runs all tests with code coverage before push.
    Tests must pass and coverage must meet the 80% threshold.
#>

$ErrorActionPreference = "Stop"

$solutionPath = "winui3/WSLKernelWatcher.WinUI3.sln"

Write-Host "Running tests with coverage..." -ForegroundColor Cyan

try {
    # Run tests with coverage
    $output = dotnet test $solutionPath `
        --configuration Release `
        --no-build `
        --nologo `
        --verbosity quiet `
        /p:CollectCoverage=true `
        /p:Threshold=80 `
        /p:ThresholdType=line,branch,method 2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Tests failed or coverage is below 80%!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Output:" -ForegroundColor Yellow
        Write-Host $output
        Write-Host ""
        Write-Host "Please fix the failing tests or increase coverage before pushing." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To run tests locally:" -ForegroundColor Cyan
        Write-Host "  dotnet test $solutionPath --configuration Release" -ForegroundColor White
        exit 1
    }

    Write-Host "✓ All tests passed with sufficient coverage" -ForegroundColor Green
    exit 0

} catch {
    Write-Host "ERROR: Failed to run tests" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
