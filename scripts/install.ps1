<#
.SYNOPSIS
    Install WSL Kernel Watcher to start automatically at user logon.

.DESCRIPTION
    This script registers WSL Kernel Watcher with Windows Task Scheduler to start automatically
    when the user logs in. The application will start minimized to the system tray.

.PARAMETER ExePath
    Path to the WSL Kernel Watcher executable. If not specified, the script will search for it
    in common locations.

.PARAMETER StartMinimized
    If specified, the application will start minimized to the system tray.

.EXAMPLE
    .\install.ps1
    Installs using auto-detected executable path.

.EXAMPLE
    .\install.ps1 -ExePath "C:\Program Files\WSLKernelWatcher\WSLKernelWatcher.WinUI3.exe"
    Installs using the specified executable path.

.EXAMPLE
    .\install.ps1 -StartMinimized
    Installs with the application starting minimized to system tray.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$ExePath,

    [Parameter(Mandatory=$false)]
    [switch]$StartMinimized
)

$ErrorActionPreference = "Stop"

# Task name
$TaskName = "WSL Kernel Watcher"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "WSL Kernel Watcher Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to find the executable
function Find-Executable {
    $searchPaths = @(
        # Build output paths
        "$PSScriptRoot\..\winui3\WSLKernelWatcher.WinUI3\bin\x64\Release\net8.0-windows10.0.19041.0\WSLKernelWatcher.WinUI3.exe",
        "$PSScriptRoot\..\winui3\WSLKernelWatcher.WinUI3\bin\x64\Debug\net8.0-windows10.0.19041.0\WSLKernelWatcher.WinUI3.exe",
        # Common installation paths
        "$env:ProgramFiles\WSL Kernel Watcher\WSLKernelWatcher.WinUI3.exe",
        "$env:LOCALAPPDATA\WSL Kernel Watcher\WSLKernelWatcher.WinUI3.exe"
    )

    foreach ($path in $searchPaths) {
        if (Test-Path $path) {
            return (Resolve-Path $path).Path
        }
    }

    return $null
}

# Determine executable path
if ([string]::IsNullOrWhiteSpace($ExePath)) {
    Write-Host "Searching for WSL Kernel Watcher executable..." -ForegroundColor Yellow
    $ExePath = Find-Executable

    if ($null -eq $ExePath) {
        Write-Host "ERROR: Could not find WSL Kernel Watcher executable." -ForegroundColor Red
        Write-Host "Please build the project first or specify the path using -ExePath parameter." -ForegroundColor Red
        exit 1
    }

    Write-Host "Found executable: $ExePath" -ForegroundColor Green
} else {
    if (-not (Test-Path $ExePath)) {
        Write-Host "ERROR: Specified executable not found: $ExePath" -ForegroundColor Red
        exit 1
    }
    $ExePath = (Resolve-Path $ExePath).Path
}

Write-Host ""

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "WARNING: Task '$TaskName' already exists." -ForegroundColor Yellow
    $response = Read-Host "Do you want to overwrite it? (Y/N)"

    if ($response -ne 'Y' -and $response -ne 'y') {
        Write-Host "Installation cancelled." -ForegroundColor Yellow
        exit 0
    }

    Write-Host "Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Prepare arguments
$arguments = ""
if ($StartMinimized) {
    $arguments = "--tray"
}

# Create task action
$action = New-ScheduledTaskAction -Execute $ExePath -Argument $arguments

# Create task trigger (at logon)
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

# Create task settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -DontStopOnIdleEnd `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

# Create task principal (run as current user)
$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

# Register the task
try {
    Write-Host "Registering scheduled task..." -ForegroundColor Yellow

    $task = Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "Monitors WSL kernel version and notifies when updates are available."

    Write-Host ""
    Write-Host "SUCCESS: Task registered successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  Name: $TaskName"
    Write-Host "  Executable: $ExePath"
    Write-Host "  Arguments: $(if ($arguments) { $arguments } else { '(none)' })"
    Write-Host "  Trigger: At user logon ($env:USERNAME)"
    Write-Host ""

    # Ask if user wants to start the task now
    $response = Read-Host "Do you want to start WSL Kernel Watcher now? (Y/N)"

    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host "Starting task..." -ForegroundColor Yellow
        Start-ScheduledTask -TaskName $TaskName
        Start-Sleep -Seconds 2

        # Check if the process is running
        $processName = [System.IO.Path]::GetFileNameWithoutExtension($ExePath)
        $process = Get-Process -Name $processName -ErrorAction SilentlyContinue

        if ($process) {
            Write-Host "SUCCESS: WSL Kernel Watcher is now running!" -ForegroundColor Green
            if ($StartMinimized) {
                Write-Host "The application is running in the system tray." -ForegroundColor Cyan
            }
        } else {
            Write-Host "WARNING: Task started but process not detected. Please check Task Scheduler." -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "Installation complete! WSL Kernel Watcher will start automatically at logon." -ForegroundColor Green
    Write-Host ""
    Write-Host "To uninstall, run: .\uninstall.ps1" -ForegroundColor Cyan

} catch {
    Write-Host "ERROR: Failed to register task." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
