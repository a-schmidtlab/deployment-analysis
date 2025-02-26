# Deployment Analyzer Debug Launcher (PowerShell Version)
Write-Host "===================================================="
Write-Host "Deployment Analyzer Debug Launcher (PowerShell)"
Write-Host "===================================================="
Write-Host "Running at: $(Get-Date)"
Write-Host "Current directory: $(Get-Location)"

# Change to the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $scriptDir
Write-Host "Script directory: $(Get-Location)"

# Display directory contents
Write-Host "`nDirectory contents:"
Get-ChildItem -Name

# Check for executable
Write-Host "`nChecking for executable..."
$exePath = "dist\DeploymentAnalyzer\DeploymentAnalyzer.exe"
if (Test-Path $exePath) {
    Write-Host "Found executable at $exePath"

    # Create required directories if missing
    Write-Host "`nCreating required directories if missing..."
    $dirs = @("dist\DeploymentAnalyzer\data", "dist\DeploymentAnalyzer\logs", "dist\DeploymentAnalyzer\output")
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            Write-Host "Creating directory: $dir"
            New-Item -Path $dir -ItemType Directory -Force | Out-Null
        } else {
            Write-Host "Directory already exists: $dir"
        }
    }
    
    # Launch application
    Write-Host "`nLaunching application with output logged to app_output.log..."
    Set-Location -Path "dist\DeploymentAnalyzer"
    Write-Host "Changed directory to: $(Get-Location)"
    
    try {
        # Start the process and redirect output
        $process = Start-Process -FilePath ".\DeploymentAnalyzer.exe" -RedirectStandardOutput "..\..\app_output.log" -RedirectStandardError "..\..\app_error.log" -NoNewWindow -PassThru
        Write-Host "Application started with process ID: $($process.Id)"
        Write-Host "Check app_output.log and app_error.log for details."
    }
    catch {
        Write-Host "Error starting application: $_" -ForegroundColor Red
    }
} else {
    Write-Host "ERROR: DeploymentAnalyzer.exe not found in the dist\DeploymentAnalyzer directory." -ForegroundColor Red
    
    Write-Host "`nCurrent directory contents:"
    Get-ChildItem -Name
    
    Write-Host "`nDist directory contents:"
    if (Test-Path "dist") {
        Get-ChildItem -Path "dist" -Name
        
        if (Test-Path "dist\DeploymentAnalyzer") {
            Write-Host "`nDeploymentAnalyzer directory contents:"
            Get-ChildItem -Path "dist\DeploymentAnalyzer" -Name
        }
    } else {
        Write-Host "Dist directory not found." -ForegroundColor Yellow
    }
    
    Write-Host "`nPlease run PyInstaller to build the application first." -ForegroundColor Yellow
}

Write-Host "`nPress Enter to exit..."
Read-Host 