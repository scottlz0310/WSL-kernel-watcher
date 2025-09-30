# WSL Kernel Watcher Install Script
# PowerShell Execution Policy may need to be set:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

param(
    [string]$InstallMethod = "uv",  # "uv" or "pipx"
    [string]$InstallPath = "",
    [switch]$Dev = $false,
    [switch]$Help = $false
)

function Show-Help {
    Write-Host "WSL Kernel Watcher Install Script" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\install.ps1 [Options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -InstallMethod <method>  Install method ('uv' or 'pipx')"
    Write-Host "  -InstallPath <path>      Install path (uv only)"
    Write-Host "  -Dev                     Setup as development environment"
    Write-Host "  -Help                    Show this help"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\install.ps1                    # Install using uv"
    Write-Host "  .\install.ps1 -InstallMethod pipx # Install using pipx"
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
    
    if ($Path -eq "") {
        $Path = Get-Location
    }
    
    try {
        Set-Location $Path
        
        # Create virtual environment
        uv venv
        
        if ($IsDev) {
            # Install development dependencies
            uv sync --extra dev
            
            # Setup pre-commit hooks
            uv run pre-commit install
            
            Write-Host "Development environment setup completed." -ForegroundColor Green
            Write-Host "You can run the application with:" -ForegroundColor Cyan
            Write-Host "  uv run wsl-kernel-watcher" -ForegroundColor White
        }
        else {
            # Install production dependencies
            uv sync
            
            Write-Host "Installation completed." -ForegroundColor Green
            Write-Host "You can run the application with:" -ForegroundColor Cyan
            Write-Host "  uv run wsl-kernel-watcher" -ForegroundColor White
        }
        
        # Copy configuration file
        if (-not (Test-Path "config.toml")) {
            if (Test-Path "config.template.toml") {
                Copy-Item "config.template.toml" "config.toml"
                Write-Host "Created configuration file config.toml." -ForegroundColor Green
            }
        }
        
        return $true
    }
    catch {
        Write-Host "Installation failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Install-WithPipx {
    Write-Host "Installing WSL Kernel Watcher using pipx..." -ForegroundColor Yellow
    
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
        
        return $true
    }
    catch {
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
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Edit the configuration file (config.toml) as needed" -ForegroundColor White
    Write-Host "2. Run the application" -ForegroundColor White
    Write-Host ""
    Write-Host "For support, please refer to README.md." -ForegroundColor Cyan
}
else {
    Write-Host ""
    Write-Host "Installation failed." -ForegroundColor Red
    Write-Host "Please check the error messages and try again." -ForegroundColor Red
    exit 1
}