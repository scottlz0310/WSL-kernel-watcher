# WSL Kernel Watcher Install Script
# PowerShell Execution Policy may need to be set:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

param(
    [string]$InstallMethod = "uv",  # "uv" or "pipx"
    [string]$InstallPath = "",
    [switch]$Dev = $false,
    [switch]$Help = $false
)

$script:LastInstallDetails = $null

function Show-Help {
    Write-Host "WSL Kernel Watcher Install Script" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\install.ps1 [Options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -InstallMethod <method>  Install method ('uv' or 'pipx')"
    Write-Host "  -InstallPath <path>      Target directory for uv installs"
    Write-Host "                               (project files are copied when set)"
    Write-Host "  -Dev                     Setup as development environment"
    Write-Host "  -Help                    Show this help"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\install.ps1                    # Install using uv"
    Write-Host "  .\install.ps1 -InstallMethod pipx # Install using pipx"
    Write-Host "  .\install.ps1 -InstallPath C:\Apps\WSLKW # Install to custom folder (uv)"
    Write-Host "  .\install.ps1 -Dev               # Setup development environment"
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Copy-ProjectContent {
    param(
        [string]$Source,
        [string]$Destination,
        [string[]]$ExcludeDirectories = @(),
        [string[]]$ExcludeFiles = @()
    )

    if (-not (Test-Path -LiteralPath $Destination)) {
        New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    }

    Get-ChildItem -LiteralPath $Source -Force | ForEach-Object {
        if ($_.PSIsContainer) {
            if ($ExcludeDirectories -contains $_.Name) {
                return
            }
            $targetDir = Join-Path $Destination $_.Name
            Copy-ProjectContent -Source $_.FullName -Destination $targetDir -ExcludeDirectories $ExcludeDirectories -ExcludeFiles $ExcludeFiles
        }
        else {
            if ($ExcludeFiles -contains $_.Name) {
                return
            }
            Copy-Item -LiteralPath $_.FullName -Destination $Destination -Force
        }
    }
}

function Resolve-InstallRoot {
    param(
        [string]$RequestedPath,
        [string]$ProjectRoot
    )

    $projectRootFull = [System.IO.Path]::GetFullPath($ProjectRoot)

    if ([string]::IsNullOrWhiteSpace($RequestedPath)) {
        return [pscustomobject]@{
            Path = $projectRootFull
            Copied = $false
        }
    }

    $expandedPath = [System.Environment]::ExpandEnvironmentVariables($RequestedPath)
    if ($expandedPath.StartsWith('~')) {
        if ($expandedPath.Length -eq 1) {
            $expandedPath = $HOME
        }
        elseif ($expandedPath[1] -eq '/' -or $expandedPath[1] -eq '\') {
            $expandedPath = Join-Path $HOME $expandedPath.Substring(2)
        }
        else {
            $expandedPath = $expandedPath.Replace('~', $HOME)
        }
    }

    if (-not [System.IO.Path]::IsPathRooted($expandedPath)) {
        $expandedPath = Join-Path (Get-Location).Path $expandedPath
    }

    $expandedPath = [System.IO.Path]::GetFullPath($expandedPath)

    try {
        if (Test-Path -LiteralPath $expandedPath) {
            $item = Get-Item -LiteralPath $expandedPath
            if (-not $item.PSIsContainer) {
                throw "InstallPath must be a directory."
            }
            $targetFull = $item.FullName
        }
        else {
            $targetFull = (New-Item -ItemType Directory -Path $expandedPath -Force).FullName
        }
    }
    catch {
        throw "Failed to prepare install path '$RequestedPath': $($_.Exception.Message)"
    }

    $targetFull = [System.IO.Path]::GetFullPath($targetFull)

    $excludeDirs = @('.git', '.venv', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'htmlcov', 'dist', '.amazonq', '.kiro', [System.IO.Path]::GetFileName($targetFull))
    $excludeFiles = @('.coverage', 'config.toml')

    $copied = $false

    if (-not (Test-Path -LiteralPath (Join-Path $targetFull 'pyproject.toml'))) {
        Write-Host "Copying project files to $targetFull..." -ForegroundColor Yellow
        Copy-ProjectContent -Source $projectRootFull -Destination $targetFull -ExcludeDirectories $excludeDirs -ExcludeFiles $excludeFiles
        $copied = $true
    }

    return [pscustomobject]@{
        Path = $targetFull
        Copied = $copied
    }
}

function Install-UV {
    Write-Host "Installing uv..." -ForegroundColor Yellow
    try {
        irm https://astral.sh/uv/install.ps1 | iex
        Write-Host "uv installation completed." -ForegroundColor Green
        # Update PATH
        $userPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
        $machinePath = [System.Environment]::GetEnvironmentVariable("PATH", "Machine")
        $env:PATH = $userPath + ";" + $machinePath
        return $true
    }
    catch {
        Write-Host "Failed to install uv: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Install-Pipx {
    Write-Host "Installing pipx..." -ForegroundColor Yellow
    try {
        python -m pip install --user pipx
        python -m pipx ensurepath
        Write-Host "pipx installation completed." -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Failed to install pipx: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Install-WithUV {
    param([string]$Path, [bool]$IsDev)

    Write-Host "Installing WSL Kernel Watcher using uv..." -ForegroundColor Yellow

    $script:LastInstallDetails = $null

    $projectRoot = Split-Path -Parent $PSScriptRoot

    try {
        $resolved = Resolve-InstallRoot -RequestedPath $Path -ProjectRoot $projectRoot
    }
    catch {
        Write-Host $_.Exception.Message -ForegroundColor Red
        return $false
    }

    $installRoot = $resolved.Path

    if ($resolved.Copied) {
        Write-Host "Project files copied to $installRoot." -ForegroundColor Green
    }
    else {
        Write-Host "Using project files from $installRoot." -ForegroundColor Green
    }

    Push-Location $installRoot
    try {
        uv venv

        if ($IsDev) {
            uv sync --extra dev
            uv run pre-commit install

            Write-Host "Development environment setup completed." -ForegroundColor Green
            Write-Host "You can run the application with:" -ForegroundColor Cyan
            Write-Host "  uv run wsl-kernel-watcher" -ForegroundColor White
        }
        else {
            uv sync

            Write-Host "Installation completed." -ForegroundColor Green
            Write-Host "You can run the application with:" -ForegroundColor Cyan
            Write-Host "  uv run wsl-kernel-watcher" -ForegroundColor White
        }

        if (-not (Test-Path "config.toml")) {
            if (Test-Path "config.template.toml") {
                Copy-Item "config.template.toml" "config.toml"
                Write-Host "Created configuration file config.toml." -ForegroundColor Green
            }
        }

        $script:LastInstallDetails = [pscustomobject]@{
            InstallMethod = "uv"
            InstallRoot = $installRoot
            DevMode = $IsDev
            ProjectCopied = $resolved.Copied
        }

        return $true
    }
    catch {
        $script:LastInstallDetails = $null
        Write-Host "Installation failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    finally {
        Pop-Location
    }
}


function Install-WithPipx {
    Write-Host "Installing WSL Kernel Watcher using pipx..." -ForegroundColor Yellow

    $script:LastInstallDetails = $null

    try {
        # Install from current directory
        pipx install .
        
        Write-Host "Installation completed." -ForegroundColor Green
        Write-Host "You can run the application with:" -ForegroundColor Cyan
        Write-Host "  wsl-kernel-watcher" -ForegroundColor White
        
        # Guide for configuration file location
        $configPath = "$env:APPDATA\wsl-kernel-watcher"
        Write-Host "Configuration file will be created at:" -ForegroundColor Cyan
        Write-Host "  $configPath\config.toml" -ForegroundColor White

        $script:LastInstallDetails = [pscustomobject]@{
            InstallMethod = "pipx"
            BinaryName = "wsl-kernel-watcher"
            ConfigPath = Join-Path $configPath "config.toml"
        }

        return $true
    }
    catch {
        $script:LastInstallDetails = $null
        Write-Host "Installation failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Main processing
if ($Help) {
    Show-Help
    exit 0
}

Write-Host "WSL Kernel Watcher Install Script" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Validate install method
if ($InstallMethod -notin @("uv", "pipx")) {
    Write-Host "Error: Invalid install method. Please specify 'uv' or 'pipx'." -ForegroundColor Red
    Show-Help
    exit 1
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Python
if (-not (Test-Command "python")) {
    Write-Host "Error: Python is not installed." -ForegroundColor Red
    Write-Host "Please install Python 3.9 or later." -ForegroundColor Red
    exit 1
}

$pythonVersion = python --version 2>&1
Write-Host "Python: $pythonVersion" -ForegroundColor Green

# Check WSL
if (-not (Test-Command "wsl")) {
    Write-Host "Warning: WSL is not installed." -ForegroundColor Yellow
    Write-Host "It is recommended to install WSL2." -ForegroundColor Yellow
}
else {
    Write-Host "WSL: Installed" -ForegroundColor Green
}

# Process based on install method
$success = $false

if ($InstallMethod -eq "uv") {
    # Check/install uv
    if (-not (Test-Command "uv")) {
        Write-Host "uv is not installed." -ForegroundColor Yellow
        $install = Read-Host "Do you want to install uv? (y/N)"
        if ($install -eq "y" -or $install -eq "Y") {
            if (-not (Install-UV)) {
                exit 1
            }
        }
        else {
            Write-Host "uv is required. Please install it manually." -ForegroundColor Red
            exit 1
        }
    }
    else {
        $uvVersion = uv --version
        Write-Host "uv: $uvVersion" -ForegroundColor Green
    }
    
    $success = Install-WithUV -Path $InstallPath -IsDev $Dev
}
elseif ($InstallMethod -eq "pipx") {
    # Check/install pipx
    if (-not (Test-Command "pipx")) {
        Write-Host "pipx is not installed." -ForegroundColor Yellow
        $install = Read-Host "Do you want to install pipx? (y/N)"
        if ($install -eq "y" -or $install -eq "Y") {
            if (-not (Install-Pipx)) {
                exit 1
            }
        }
        else {
            Write-Host "pipx is required. Please install it manually." -ForegroundColor Red
            exit 1
        }
    }
    else {
        $pipxVersion = pipx --version
        Write-Host "pipx: $pipxVersion" -ForegroundColor Green
    }
    
    $success = Install-WithPipx
}

if ($success) {
    Write-Host ""
    Write-Host "Installation completed successfully!" -ForegroundColor Green

    if ($script:LastInstallDetails) {
        switch ($script:LastInstallDetails.InstallMethod) {
            'uv' {
                $configPath = Join-Path $script:LastInstallDetails.InstallRoot 'config.toml'
                Write-Host "Install root: $($script:LastInstallDetails.InstallRoot)" -ForegroundColor Cyan
                Write-Host "Configuration file: $configPath" -ForegroundColor Cyan
            }
            'pipx' {
                Write-Host "Executable: wsl-kernel-watcher (managed by pipx)" -ForegroundColor Cyan
                if ($script:LastInstallDetails.ConfigPath) {
                    Write-Host "Configuration file: $($script:LastInstallDetails.ConfigPath)" -ForegroundColor Cyan
                }
            }
        }
    }

    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    if ($script:LastInstallDetails -and $script:LastInstallDetails.InstallMethod -eq 'pipx') {
        Write-Host "1. Edit the configuration file listed above as needed" -ForegroundColor White
        Write-Host "2. Run the application with: wsl-kernel-watcher" -ForegroundColor White
    }
    else {
        Write-Host "1. Edit the configuration file listed above as needed" -ForegroundColor White
        Write-Host "2. Run the application with: uv run wsl-kernel-watcher" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "For support, please refer to README.md." -ForegroundColor Cyan
}
else {
    Write-Host ""
    Write-Host "Installation failed." -ForegroundColor Red
    Write-Host "Please check the error messages and try again." -ForegroundColor Red
    exit 1
}



